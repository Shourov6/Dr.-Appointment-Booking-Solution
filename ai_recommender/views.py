import json
from functools import lru_cache

from django.conf import settings
from django.http import FileResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from openpyxl import load_workbook

RECOMMENDER_ROOT = settings.BASE_DIR / 'drseba-intelligent-doctor-recommendation-main'
DATA_PATH = RECOMMENDER_ROOT / 'data' / 'Dr.Seba_500_Organized_Final.xlsx'
STYLE_PATH = RECOMMENDER_ROOT / 'demo_ui' / 'style.css'


def _normalize_column(name):
    return str(name or '').strip().lower().replace(' ', '_')


def _to_int(value, default=0):
    try:
        if value is None or value == '':
            return default
        return int(float(str(value).strip()))
    except Exception:
        return default


def _to_float(value, default=0.0):
    try:
        if value is None or value == '':
            return default
        return float(str(value).strip())
    except Exception:
        return default


def _to_yes_no_int(value):
    text = str(value or '').strip().lower()
    return 1 if text in {'yes', 'y', 'true', '1'} else 0


@lru_cache(maxsize=1)
def get_runtime():
    if not DATA_PATH.exists():
        raise RuntimeError(f'Data file not found: {DATA_PATH}')

    workbook = load_workbook(DATA_PATH, data_only=True, read_only=True)
    worksheet = workbook.active

    rows = worksheet.iter_rows(values_only=True)
    headers = next(rows, None)
    if not headers:
        raise RuntimeError('Recommendation data file has no headers.')

    normalized_headers = [_normalize_column(h) for h in headers]

    records = []
    districts = set()
    specializations = set()
    thanas_by_district = {}

    for values in rows:
        row = dict(zip(normalized_headers, values))

        district = str(row.get('district') or '').strip()
        thana = str(row.get('thana') or '').strip()
        specialization = str(row.get('specialization_group') or row.get('specialization') or '').strip()

        if not district or not thana or not specialization:
            continue

        consultation_fees = _to_int(row.get('consultation_fees'), default=0)
        rating_avg = _to_float(row.get('rating_avg'), default=0.0)
        experience_years = _to_int(row.get('experience_years'), default=0)

        record = {
            'doctor_name': str(row.get('doctor_name') or 'Unknown Doctor').strip(),
            'specialization': specialization,
            'rating_avg': max(0.0, min(rating_avg, 5.0)),
            'experience_years': max(0, experience_years),
            'consultation_fees': max(0, consultation_fees),
            'hospital_name': str(row.get('hospital_name') or 'Unknown Hospital').strip(),
            'full_address': str(row.get('full_address') or '').strip(),
            'district': district,
            'thana': thana,
            'online_consultation': _to_yes_no_int(row.get('online_consultation')),
            'emergency_service': _to_yes_no_int(row.get('emergency_service')),
        }
        records.append(record)

        districts.add(district)
        specializations.add(specialization)
        thanas_by_district.setdefault(district, set()).add(thana)

    workbook.close()

    return {
        'records': records,
        'districts': sorted(districts),
        'specializations': sorted(specializations),
        'thanas_by_district': {k: sorted(v) for k, v in thanas_by_district.items()},
    }


def get_options_data():
    runtime = get_runtime()
    all_thanas = sorted({thana for thanas in runtime['thanas_by_district'].values() for thana in thanas})
    return {
        'districts': runtime['districts'],
        'thanas': all_thanas,
        'specializations': runtime['specializations'],
    }


def get_thanas_for_district(district):
    runtime = get_runtime()
    return runtime['thanas_by_district'].get(district, [])


def _heuristic_score(record, max_fee):
    rating_component = (record['rating_avg'] / 5.0) * 0.5
    experience_component = (min(record['experience_years'], 30) / 30.0) * 0.3
    if max_fee > 0:
        affordability_component = (1.0 - min(record['consultation_fees'] / max_fee, 1.0)) * 0.2
    else:
        affordability_component = 0.0
    return (rating_component + experience_component + affordability_component) * 2.0


def get_recommendations(user_input, top_n=5):
    runtime = get_runtime()
    district = user_input['district']
    thana = user_input['thana']
    specialization = user_input['specialization']
    max_fee = max(0, _to_int(user_input.get('max_fee'), default=0))
    require_online = int(user_input.get('online', 0)) == 1
    require_emergency = int(user_input.get('emergency', 0)) == 1

    candidates = []
    for record in runtime['records']:
        if record['district'].lower() != district.lower():
            continue
        if record['thana'].lower() != thana.lower():
            continue
        if record['specialization'].lower() != specialization.lower():
            continue
        if record['consultation_fees'] > max_fee:
            continue
        if require_online and record['online_consultation'] != 1:
            continue
        if require_emergency and record['emergency_service'] != 1:
            continue

        enriched = dict(record)
        enriched['predicted_score'] = round(_heuristic_score(record, max_fee), 4)
        candidates.append(enriched)

    if not candidates:
        return {'message': 'No doctors found with these criteria'}

    candidates.sort(
        key=lambda item: (
            item['predicted_score'],
            item['rating_avg'],
            item['experience_years'],
            -item['consultation_fees'],
        ),
        reverse=True,
    )

    return {'success': True, 'count': len(candidates[:top_n]), 'doctors': candidates[:top_n]}


@require_http_methods(['GET', 'POST'])
def home(request):
    try:
        options = get_options_data()
    except Exception as exc:
        return render(
            request,
            'ai_recommender/index.html',
            {
                'districts': [],
                'specializations': [],
                'thanas': [],
                'selected_district': '',
                'selected_thana': '',
                'selected_spec': '',
                'max_fee': '2000',
                'online': False,
                'emergency': False,
                'top_n': '5',
                'searched': False,
                'error': f'Recommender data unavailable: {exc}',
                'doctors': [],
            },
        )

    selected_district = request.POST.get('district') or (options['districts'][0] if options['districts'] else '')
    thanas_for_selected = get_thanas_for_district(selected_district) if selected_district else []
    selected_thana = request.POST.get('thana') or (thanas_for_selected[0] if thanas_for_selected else '')
    if selected_thana not in thanas_for_selected and thanas_for_selected:
        selected_thana = thanas_for_selected[0]
    selected_spec = request.POST.get('specialization') or (
        options['specializations'][0] if options['specializations'] else ''
    )
    if selected_spec not in options['specializations'] and options['specializations']:
        selected_spec = options['specializations'][0]
    max_fee = request.POST.get('maxFee', '2000')
    online = request.POST.get('online') == 'on'
    emergency = request.POST.get('emergency') == 'on'
    top_n = request.POST.get('topN', '5')

    context = {
        'districts': options['districts'],
        'specializations': options['specializations'],
        'thanas': thanas_for_selected,
        'selected_district': selected_district,
        'selected_thana': selected_thana,
        'selected_spec': selected_spec,
        'max_fee': max_fee,
        'online': online,
        'emergency': emergency,
        'top_n': top_n,
        'searched': False,
        'error': '',
        'doctors': [],
        'scoring_mode': 'heuristic',
    }

    if request.method == 'POST':
        context['searched'] = True
        try:
            top_n_int = int(top_n)
            if top_n_int < 1:
                top_n_int = 1
            if top_n_int > 20:
                top_n_int = 20

            max_fee_int = int(max_fee)
            if max_fee_int < 0:
                max_fee_int = 0

            payload = {
                'district': selected_district,
                'thana': selected_thana,
                'specialization': selected_spec,
                'max_fee': max_fee_int,
                'online': 1 if online else 0,
                'emergency': 1 if emergency else 0,
            }
            result = get_recommendations(payload, top_n_int)
            if result.get('success'):
                context['doctors'] = result['doctors']
            else:
                context['error'] = result.get('message') or result.get('error') or 'No doctors found'
        except Exception as exc:
            context['error'] = str(exc)

    return render(request, 'ai_recommender/index.html', context)


@require_GET
def style_css(request):
    return FileResponse(open(STYLE_PATH, 'rb'), content_type='text/css')


@require_GET
def api_root(request):
    return JsonResponse(
        {
            'status': 'healthy',
            'message': 'Doctor Recommendation API is running',
            'endpoints': [
                '/best-doctor-for-you/api/health',
                '/best-doctor-for-you/api/options',
                '/best-doctor-for-you/api/thanas/<district>',
                '/best-doctor-for-you/api/recommendations',
            ],
        }
    )


@require_GET
def api_health(request):
    return JsonResponse({'status': 'healthy'})


@require_GET
def api_options(request):
    try:
        return JsonResponse({'success': True, 'options': get_options_data()})
    except Exception as exc:
        return JsonResponse({'success': False, 'error': str(exc)}, status=500)


@require_GET
def api_thanas(request, district):
    thanas = get_thanas_for_district(district)
    if not thanas:
        return JsonResponse({'error': f'No thanas found for {district}'}, status=404)
    return JsonResponse({'district': district, 'thanas': thanas})


@csrf_exempt
@require_http_methods(['POST'])
def api_recommendations(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

    required = ['district', 'thana', 'specialization', 'max_fee', 'online', 'emergency']
    for field in required:
        if field not in data:
            return JsonResponse({'error': f'Missing: {field}'}, status=400)

    top_n = data.get('top_n', 5)
    result = get_recommendations(data, top_n)

    if 'error' in result:
        return JsonResponse(result, status=400)
    return JsonResponse(result)

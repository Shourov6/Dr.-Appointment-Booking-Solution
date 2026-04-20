"""Shared helpers for displaying doctor hospital schedules."""


def format_time_display(time_value):
    """Render a time object as a stable 12-hour label."""
    if not time_value:
        return ''
    return time_value.strftime('%I:%M %p').lstrip('0')


def build_schedule_display(schedule, weekly_entries=None):
    """Build a normalized schedule display payload for templates."""
    display_rows = []
    display_days = list(schedule.consultation_days or [])

    if weekly_entries:
        day_indices = []
        for entry in weekly_entries:
            if entry.day_of_week not in day_indices:
                day_indices.append(entry.day_of_week)
            start_text = format_time_display(entry.start_time)
            end_text = format_time_display(entry.end_time)
            display_rows.append({
                'day': entry.get_day_of_week_display(),
                'time': f'{start_text} - {end_text}' if start_text and end_text else 'N/A',
                'day_index': entry.day_of_week,
                'start': start_text,
                'end': end_text,
            })
        display_days = [entry.get_day_of_week_display() for entry in weekly_entries if entry.day_of_week in day_indices]
    else:
        joined_days = ', '.join(display_days) if display_days else 'Available'
        if schedule.morning_start and schedule.morning_end:
            display_rows.append({
                'day': joined_days,
                'time': f'{format_time_display(schedule.morning_start)} - {format_time_display(schedule.morning_end)}',
            })
        if schedule.evening_start and schedule.evening_end:
            display_rows.append({
                'day': joined_days,
                'time': f'{format_time_display(schedule.evening_start)} - {format_time_display(schedule.evening_end)}',
            })
        if not display_rows:
            display_rows.append({
                'day': joined_days,
                'time': 'N/A',
            })

    display_time = ' | '.join(row['time'] for row in display_rows if row.get('time') and row['time'] != 'N/A')
    if not display_time:
        display_time = 'N/A'

    return {
        'display_rows': display_rows,
        'display_days': display_days,
        'display_time': display_time,
    }


def attach_schedule_display(schedule, weekly_entries=None):
    """Attach display helper fields to a schedule object."""
    payload = build_schedule_display(schedule, weekly_entries)
    schedule.display_rows = payload['display_rows']
    schedule.display_days = payload['display_days']
    schedule.display_time = payload['display_time']
    return schedule
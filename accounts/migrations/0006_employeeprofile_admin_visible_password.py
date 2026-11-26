from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_patient_profile_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='employeeprofile',
            name='admin_visible_password',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]

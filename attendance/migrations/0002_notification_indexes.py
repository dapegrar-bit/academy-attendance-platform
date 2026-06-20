# Generated for Academy Attendance Platform update
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='color',
            field=models.CharField(choices=[('#2f7d6f', 'أخضر أكاديميتي'), ('#f2bd3a', 'ذهبي'), ('#2d5d54', 'أخضر داكن'), ('#9cc9ba', 'نعناعي'), ('#3f8f80', 'فيروزي'), ('#6dbb8e', 'أخضر فاتح')], default='#2f7d6f', max_length=20, verbose_name='لون الدفعة'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['date', 'is_active'], name='attendance_s_date_58e6ac_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['batch', 'date'], name='attendance_s_batch_i_5a7f20_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['trainee', 'session'], name='attendance_a_trainee_753a39_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['status', 'checked_at'], name='attendance_a_status_606ab5_idx'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180, verbose_name='العنوان')),
                ('body', models.TextField(verbose_name='الرسالة')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')),
                ('is_read', models.BooleanField(default=False, verbose_name='مقروءة')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='platform_notifications', to=settings.AUTH_USER_MODEL, verbose_name='المستلم')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to='attendance.session', verbose_name='المحاضرة')),
            ],
            options={
                'verbose_name': 'تنبيه متدرب',
                'verbose_name_plural': 'تنبيهات المتدربين',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', 'is_read', '-created_at'], name='attendance_n_recipie_c28909_idx')],
            },
        ),
    ]

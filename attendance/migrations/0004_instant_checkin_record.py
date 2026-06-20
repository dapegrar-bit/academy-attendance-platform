# Generated for Academy Attendance Platform - instant check-in repeat records
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0003_rename_attendance_a_trainee_753a39_idx_attendance__trainee_8d966a_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstantCheckinRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instant_sent_at', models.DateTimeField(verbose_name='وقت إرسال طلب الحضور الفجائي')),
                ('checked_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='وقت تسجيل الحضور الفجائي')),
                ('zoom_url_snapshot', models.URLField(blank=True, max_length=500, verbose_name='الرابط المستخدم')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='المتصفح والجهاز')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instant_checkin_records', to='attendance.session', verbose_name='المحاضرة')),
                ('trainee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='instant_checkin_records', to='attendance.traineeprofile', verbose_name='المتدرب')),
            ],
            options={
                'verbose_name': 'سجل حضور فجائي',
                'verbose_name_plural': 'سجلات الحضور الفجائي',
                'ordering': ['-checked_at'],
                'unique_together': {('trainee', 'session', 'instant_sent_at')},
            },
        ),
        migrations.AddIndex(
            model_name='instantcheckinrecord',
            index=models.Index(fields=['trainee', 'session'], name='attendance__traine_812ccf_idx'),
        ),
        migrations.AddIndex(
            model_name='instantcheckinrecord',
            index=models.Index(fields=['session', 'instant_sent_at'], name='attendance__session_f650ca_idx'),
        ),
        migrations.AddIndex(
            model_name='instantcheckinrecord',
            index=models.Index(fields=['checked_at'], name='attendance__checked_163cc4_idx'),
        ),
    ]

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Batch(models.Model):
    COLORS = [
        ('#2f7d6f', 'أخضر أكاديميتي'),
        ('#f2bd3a', 'ذهبي'),
        ('#2d5d54', 'أخضر داكن'),
        ('#9cc9ba', 'نعناعي'),
        ('#3f8f80', 'فيروزي'),
        ('#6dbb8e', 'أخضر فاتح'),
    ]
    name = models.CharField('اسم الدفعة', max_length=180)
    description = models.TextField('وصف مختصر', blank=True)
    color = models.CharField('لون الدفعة', max_length=20, choices=COLORS, default='#2f7d6f')
    is_active = models.BooleanField('نشطة', default=True)
    created_at = models.DateTimeField('تاريخ الإنشاء', auto_now_add=True)

    class Meta:
        verbose_name = 'دفعة تدريبية'
        verbose_name_plural = 'الدفعات التدريبية'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def trainees_count(self):
        return self.trainees.count()

    @property
    def sessions_count(self):
        return self.sessions.count()

    @property
    def attendance_rate(self):
        profiles = self.trainees.all()
        sessions = self.sessions.filter(is_active=True)
        total = profiles.count() * sessions.count()
        if total == 0:
            return 0
        present = AttendanceRecord.objects.filter(trainee__in=profiles, session__in=sessions, status='present').count()
        return round((present / total) * 100)


class TraineeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainee_profile')
    full_name = models.CharField('الاسم الكامل', max_length=180)
    phone = models.CharField('رقم الجوال', max_length=30, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='trainees', verbose_name='الدفعة')
    created_at = models.DateTimeField('تاريخ التسجيل', auto_now_add=True)

    class Meta:
        verbose_name = 'متدرب'
        verbose_name_plural = 'المتدربون'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        parts = [p[0] for p in self.full_name.split() if p]
        return ''.join(parts[:2]) or self.user.username[:2]

    @property
    def attendance_rate(self):
        if not self.batch:
            return 0
        sessions_count = self.batch.sessions.filter(is_active=True).count()
        if sessions_count == 0:
            return 0
        present = self.attendance_records.filter(session__batch=self.batch, session__is_active=True, status='present').count()
        return round((present / sessions_count) * 100)

    @property
    def present_count(self):
        return self.attendance_records.filter(status='present').count()


class Session(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='sessions', verbose_name='الدفعة')
    title = models.CharField('عنوان المحاضرة', max_length=220)
    description = models.TextField('وصف المحاضرة', blank=True)
    date = models.DateField('تاريخ المحاضرة')
    start_time = models.TimeField('وقت البداية', null=True, blank=True)
    end_time = models.TimeField('وقت النهاية', null=True, blank=True)
    zoom_url = models.URLField('رابط زووم', max_length=500)
    is_active = models.BooleanField('فعالة', default=True)
    created_at = models.DateTimeField('تاريخ الإضافة', auto_now_add=True)

    class Meta:
        verbose_name = 'محاضرة ورابط زووم'
        verbose_name_plural = 'المحاضرات وروابط الزووم'
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['date', 'is_active']),
            models.Index(fields=['batch', 'date']),
        ]

    def __str__(self):
        return f'{self.title} - {self.batch.name}'

    @property
    def is_today(self):
        return self.date == timezone.localdate()

    @property
    def attendance_count(self):
        return self.attendance_records.filter(status='present').count()

    @property
    def attendance_ratio_text(self):
        total = self.batch.trainees.count()
        return f'{self.attendance_count}/{total}' if total else '0/0'


class TraineeZoomLink(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='custom_links')
    trainee = models.ForeignKey(TraineeProfile, on_delete=models.CASCADE, related_name='custom_zoom_links')
    zoom_url = models.URLField('رابط زووم خاص', max_length=500)

    class Meta:
        verbose_name = 'رابط زووم مخصص'
        verbose_name_plural = 'روابط زووم مخصصة'
        unique_together = ('session', 'trainee')

    def __str__(self):
        return f'{self.trainee} - {self.session}'


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('late', 'متأخر'),
        ('absent', 'غائب'),
    ]
    trainee = models.ForeignKey(TraineeProfile, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='المتدرب')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='المحاضرة')
    status = models.CharField('الحالة', max_length=20, choices=STATUS_CHOICES, default='present')
    checked_at = models.DateTimeField('وقت التحضير', default=timezone.now)
    zoom_url_snapshot = models.URLField('الرابط المستخدم', max_length=500, blank=True)
    ip_address = models.GenericIPAddressField('عنوان IP', null=True, blank=True)
    user_agent = models.TextField('المتصفح والجهاز', blank=True)

    class Meta:
        verbose_name = 'سجل حضور'
        verbose_name_plural = 'سجلات الحضور'
        unique_together = ('trainee', 'session')
        ordering = ['-checked_at']
        indexes = [
            models.Index(fields=['trainee', 'session']),
            models.Index(fields=['status', 'checked_at']),
        ]

    def __str__(self):
        return f'{self.trainee} - {self.session} - {self.get_status_display()}'


class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='platform_notifications', verbose_name='المستلم')
    title = models.CharField('العنوان', max_length=180)
    body = models.TextField('الرسالة')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications', verbose_name='المحاضرة')
    created_at = models.DateTimeField('تاريخ الإرسال', auto_now_add=True)
    is_read = models.BooleanField('مقروءة', default=False)

    class Meta:
        verbose_name = 'تنبيه متدرب'
        verbose_name_plural = 'تنبيهات المتدربين'
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read', '-created_at'])]

    def __str__(self):
        return f'{self.title} - {self.recipient.username}'


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'الجميع'),
        ('admin', 'الإدارة فقط'),
        ('trainee', 'المتدربون فقط'),
    ]
    title = models.CharField('العنوان', max_length=160)
    body = models.TextField('المحتوى')
    audience = models.CharField('الفئة المستهدفة', max_length=20, choices=AUDIENCE_CHOICES, default='all')
    created_at = models.DateTimeField('تاريخ النشر', auto_now_add=True)
    is_active = models.BooleanField('مفعّل', default=True)

    class Meta:
        verbose_name = 'إعلان'
        verbose_name_plural = 'الإعلانات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SiteSetting(models.Model):
    academy_name = models.CharField('اسم الأكاديمية', max_length=180, default='أكاديميتي')
    system_name = models.CharField('اسم النظام', max_length=220, default='النظام الشامل للحضور والمحاضرات')
    logo_url = models.URLField('رابط الشعار', max_length=500, default='https://i.top4top.io/p_3822gqcjp1.png')
    primary_color = models.CharField('اللون الأساسي', max_length=20, default='#2f7d6f')
    accent_color = models.CharField('لون التمييز', max_length=20, default='#f2bd3a')

    class Meta:
        verbose_name = 'إعدادات الموقع'
        verbose_name_plural = 'إعدادات الموقع'

    def __str__(self):
        return self.academy_name

    @classmethod
    def current(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

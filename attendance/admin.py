from django.contrib import admin
from .models import Batch, TraineeProfile, Session, TraineeZoomLink, AttendanceRecord, Announcement, SiteSetting, Notification


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active',)


@admin.register(TraineeProfile)
class TraineeProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'phone', 'batch', 'attendance_rate')
    search_fields = ('full_name', 'phone', 'user__username', 'user__email')
    list_filter = ('batch',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'date', 'start_time', 'is_active', 'attendance_ratio_text')
    search_fields = ('title', 'description', 'zoom_url')
    list_filter = ('batch', 'date', 'is_active')


@admin.register(TraineeZoomLink)
class TraineeZoomLinkAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'session', 'zoom_url')
    search_fields = ('trainee__full_name', 'session__title')


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('trainee', 'session', 'status', 'checked_at', 'ip_address')
    search_fields = ('trainee__full_name', 'trainee__user__username', 'session__title')
    list_filter = ('status', 'session__batch', 'session__date')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'audience', 'is_active', 'created_at')
    list_filter = ('audience', 'is_active')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('academy_name', 'system_name', 'primary_color', 'accent_color')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'session', 'is_read', 'created_at')
    search_fields = ('title', 'body', 'recipient__username', 'recipient__first_name')
    list_filter = ('is_read', 'created_at')

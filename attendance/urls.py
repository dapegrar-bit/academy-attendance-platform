from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('auth/', views.auth_view, name='auth'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('panel/admin/', views.admin_overview, name='admin_overview'),
    path('panel/admin/batches/', views.admin_batches, name='admin_batches'),
    path('panel/admin/batches/<int:pk>/delete/', views.delete_batch, name='delete_batch'),
    path('panel/admin/sessions/', views.admin_sessions, name='admin_sessions'),
    path('panel/admin/sessions/<int:pk>/delete/', views.delete_session, name='delete_session'),
    path('panel/admin/trainees/', views.admin_trainees, name='admin_trainees'),
    path('panel/admin/trainees/export/', views.export_trainees_csv, name='export_trainees_csv'),
    path('panel/admin/trainees/<int:pk>/delete/', views.delete_trainee, name='delete_trainee'),
    path('panel/admin/attendance/', views.admin_attendance, name='admin_attendance'),
    path('panel/admin/attendance/export/', views.export_attendance_csv, name='export_attendance_csv'),
    path('panel/admin/reports/', views.admin_reports, name='admin_reports'),
    path('panel/admin/settings/', views.admin_settings, name='admin_settings'),

    path('panel/trainee/', views.trainee_home, name='trainee_home'),
    path('panel/trainee/check-in/<int:session_id>/', views.check_in, name='check_in'),
    path('panel/trainee/calendar/', views.trainee_calendar, name='trainee_calendar'),
    path('panel/trainee/schedule/', views.trainee_schedule, name='trainee_schedule'),
    path('panel/trainee/profile/', views.trainee_profile, name='trainee_profile'),
]

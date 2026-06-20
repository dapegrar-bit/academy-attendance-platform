import csv
import calendar
from datetime import date
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from .forms import (
    ArabicAuthenticationForm,
    RegisterForm,
    BatchForm,
    SessionForm,
    TraineeAdminForm,
    ProfileForm,
    SiteSettingForm,
)
from .models import (
    Batch,
    Session,
    TraineeProfile,
    AttendanceRecord,
    Announcement,
    TraineeZoomLink,
    SiteSetting,
)


def is_admin(user):
    return user.is_authenticated and user.is_staff


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_profile(user):
    profile, _ = TraineeProfile.objects.get_or_create(
        user=user,
        defaults={'full_name': user.get_full_name() or user.username}
    )
    return profile


def home(request):
    if not request.user.is_authenticated:
        return redirect('auth')
    if request.user.is_staff:
        return redirect('admin_overview')
    return redirect('trainee_home')


def auth_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    login_form = ArabicAuthenticationForm(request, data=request.POST or None if request.POST.get('action') == 'login' else None)
    register_form = RegisterForm(request.POST or None if request.POST.get('action') == 'register' else None)
    active_tab = request.POST.get('action', 'login')

    if request.method == 'POST' and request.POST.get('action') == 'login':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'أهلًا بك، {user.first_name or user.username}')
            return redirect('home')
        messages.error(request, 'بيانات الدخول غير صحيحة.')

    if request.method == 'POST' and request.POST.get('action') == 'register':
        if register_form.is_valid():
            user = User.objects.create_user(
                username=register_form.cleaned_data['username'],
                password=register_form.cleaned_data['password'],
                first_name=register_form.cleaned_data['full_name'],
            )
            TraineeProfile.objects.create(
                user=user,
                full_name=register_form.cleaned_data['full_name'],
                phone=register_form.cleaned_data.get('phone') or '',
                batch=register_form.cleaned_data.get('batch'),
            )
            login(request, user)
            messages.success(request, 'تم إنشاء حسابك بنجاح، أهلًا بك في أكاديميتي')
            return redirect('trainee_home')
        messages.error(request, 'توجد أخطاء في نموذج إنشاء الحساب.')

    return render(request, 'attendance/auth.html', {
        'login_form': login_form,
        'register_form': register_form,
        'active_tab': active_tab,
    })


@login_required
@user_passes_test(is_admin)
def admin_overview(request):
    today = timezone.localdate()
    trainees_count = TraineeProfile.objects.count()
    batches_count = Batch.objects.filter(is_active=True).count()
    sessions_today = Session.objects.filter(date=today, is_active=True)
    today_records = AttendanceRecord.objects.filter(session__date=today, status='present')
    sessions_total = Session.objects.count()
    possible_today = sum(s.batch.trainees.count() for s in sessions_today)
    today_rate = round((today_records.count() / possible_today) * 100) if possible_today else 0
    recent_attendance = AttendanceRecord.objects.select_related('trainee', 'session')[:8]
    batch_stats = Batch.objects.filter(is_active=True)[:5]
    announcements = Announcement.objects.filter(is_active=True).filter(Q(audience='all') | Q(audience='admin'))[:3]
    return render(request, 'attendance/admin_overview.html', {
        'today': today,
        'trainees_count': trainees_count,
        'batches_count': batches_count,
        'sessions_today_count': sessions_today.count(),
        'today_rate': today_rate,
        'recent_attendance': recent_attendance,
        'batch_stats': batch_stats,
        'sessions_total': sessions_total,
        'announcements': announcements,
    })


@login_required
@user_passes_test(is_admin)
def admin_batches(request):
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(Batch, pk=edit_id) if edit_id else None
    form = BatchForm(instance=instance)
    if request.method == 'POST':
        instance = None
        if request.POST.get('batch_id'):
            instance = get_object_or_404(Batch, pk=request.POST.get('batch_id'))
        form = BatchForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ الدفعة بنجاح')
            return redirect('admin_batches')
    batches = Batch.objects.all()
    return render(request, 'attendance/admin_batches.html', {'batches': batches, 'form': form, 'edit_instance': instance})


@login_required
@user_passes_test(is_admin)
def delete_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        batch.delete()
        messages.success(request, 'تم حذف الدفعة')
    return redirect('admin_batches')


@login_required
@user_passes_test(is_admin)
def admin_sessions(request):
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(Session, pk=edit_id) if edit_id else None
    form = SessionForm(instance=instance)
    if request.method == 'POST':
        instance = None
        if request.POST.get('session_id'):
            instance = get_object_or_404(Session, pk=request.POST.get('session_id'))
        form = SessionForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ المحاضرة ورابط الزووم')
            return redirect('admin_sessions')
    batch_id = request.GET.get('batch')
    sessions = Session.objects.select_related('batch')
    if batch_id:
        sessions = sessions.filter(batch_id=batch_id)
    return render(request, 'attendance/admin_sessions.html', {
        'sessions': sessions,
        'form': form,
        'batches': Batch.objects.filter(is_active=True),
        'selected_batch': batch_id,
        'today': timezone.localdate(),
        'edit_instance': instance,
    })


@login_required
@user_passes_test(is_admin)
def delete_session(request, pk):
    session = get_object_or_404(Session, pk=pk)
    if request.method == 'POST':
        session.delete()
        messages.success(request, 'تم حذف المحاضرة')
    return redirect('admin_sessions')


@login_required
@user_passes_test(is_admin)
def admin_trainees(request):
    edit_id = request.GET.get('edit')
    instance = get_object_or_404(TraineeProfile, pk=edit_id) if edit_id else None
    form = TraineeAdminForm(instance=instance)
    if request.method == 'POST':
        instance = None
        if request.POST.get('trainee_id'):
            instance = get_object_or_404(TraineeProfile, pk=request.POST.get('trainee_id'))
        form = TraineeAdminForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ بيانات المتدرب')
            return redirect('admin_trainees')
    q = request.GET.get('q', '')
    batch_id = request.GET.get('batch', '')
    trainees = TraineeProfile.objects.select_related('user', 'batch')
    if q:
        trainees = trainees.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(user__username__icontains=q))
    if batch_id:
        trainees = trainees.filter(batch_id=batch_id)
    return render(request, 'attendance/admin_trainees.html', {
        'trainees': trainees,
        'batches': Batch.objects.filter(is_active=True),
        'form': form,
        'q': q,
        'selected_batch': batch_id,
        'edit_instance': instance,
    })


@login_required
@user_passes_test(is_admin)
def delete_trainee(request, pk):
    profile = get_object_or_404(TraineeProfile, pk=pk)
    if request.method == 'POST':
        user = profile.user
        user.delete()
        messages.success(request, 'تم حذف المتدرب')
    return redirect('admin_trainees')


def filtered_attendance_queryset(request):
    q = request.GET.get('q', '')
    batch_id = request.GET.get('batch', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    sessions = Session.objects.select_related('batch').all()
    trainees = TraineeProfile.objects.select_related('user', 'batch').all()

    if q:
        trainees = trainees.filter(Q(full_name__icontains=q) | Q(phone__icontains=q) | Q(user__username__icontains=q))
    if batch_id:
        sessions = sessions.filter(batch_id=batch_id)
        trainees = trainees.filter(batch_id=batch_id)
    if date_from:
        sessions = sessions.filter(date__gte=date_from)
    if date_to:
        sessions = sessions.filter(date__lte=date_to)

    rows = []
    for session in sessions.order_by('-date')[:100]:
        for trainee in trainees.filter(batch=session.batch):
            record = AttendanceRecord.objects.filter(session=session, trainee=trainee).first()
            computed_status = record.status if record else 'absent'
            if status and computed_status != status:
                continue
            rows.append({'session': session, 'trainee': trainee, 'record': record, 'status': computed_status})
    return rows, {'q': q, 'batch': batch_id, 'status': status, 'date_from': date_from, 'date_to': date_to}


@login_required
@user_passes_test(is_admin)
def admin_attendance(request):
    rows, filters = filtered_attendance_queryset(request)
    present_count = sum(1 for r in rows if r['status'] == 'present')
    absent_count = sum(1 for r in rows if r['status'] == 'absent')
    return render(request, 'attendance/admin_attendance.html', {
        'rows': rows,
        'filters': filters,
        'batches': Batch.objects.filter(is_active=True),
        'present_count': present_count,
        'absent_count': absent_count,
    })


@login_required
@user_passes_test(is_admin)
def export_attendance_csv(request):
    rows, _ = filtered_attendance_queryset(request)
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="academy_attendance.csv"'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow(['المتدرب', 'اسم المستخدم', 'الجوال', 'الدفعة', 'المحاضرة', 'التاريخ', 'الحالة', 'وقت التحضير', 'رابط زووم'])
    for row in rows:
        record = row['record']
        writer.writerow([
            row['trainee'].full_name,
            row['trainee'].user.username,
            row['trainee'].phone,
            row['session'].batch.name,
            row['session'].title,
            row['session'].date,
            'حاضر' if row['status'] == 'present' else 'غائب',
            timezone.localtime(record.checked_at).strftime('%Y-%m-%d %H:%M') if record else '-',
            record.zoom_url_snapshot if record else row['session'].zoom_url,
        ])
    return response


@login_required
@user_passes_test(is_admin)
def admin_reports(request):
    batch_id = request.GET.get('batch')
    batches = Batch.objects.filter(is_active=True)
    selected_batch = batches.filter(pk=batch_id).first() if batch_id else batches.first()
    trainees = TraineeProfile.objects.filter(batch=selected_batch).select_related('user') if selected_batch else []
    total_rate = selected_batch.attendance_rate if selected_batch else 0
    top = sorted(list(trainees), key=lambda p: p.attendance_rate, reverse=True)[:10]
    low = [p for p in trainees if p.attendance_rate < 60]
    return render(request, 'attendance/admin_reports.html', {
        'batches': batches,
        'selected_batch': selected_batch,
        'total_rate': total_rate,
        'top': top,
        'low': low,
    })


@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    setting = SiteSetting.current()
    form = SiteSettingForm(instance=setting)
    if request.method == 'POST':
        form = SiteSettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ إعدادات النظام')
            return redirect('admin_settings')
    return render(request, 'attendance/admin_settings.html', {'form': form})


@login_required
def trainee_home(request):
    if request.user.is_staff:
        return redirect('admin_overview')
    profile = get_profile(request.user)
    today = timezone.localdate()
    todays_session = None
    if profile.batch:
        todays_session = Session.objects.filter(batch=profile.batch, date=today, is_active=True).order_by('start_time').first()
    record = AttendanceRecord.objects.filter(trainee=profile, session=todays_session).first() if todays_session else None
    zoom_url = None
    if record:
        custom = TraineeZoomLink.objects.filter(session=todays_session, trainee=profile).first()
        zoom_url = custom.zoom_url if custom else todays_session.zoom_url
    announcements = Announcement.objects.filter(is_active=True).filter(Q(audience='all') | Q(audience='trainee'))[:3]
    total_sessions = profile.batch.sessions.count() if profile.batch else 0
    return render(request, 'attendance/trainee_home.html', {
        'profile': profile,
        'today': today,
        'todays_session': todays_session,
        'record': record,
        'zoom_url': zoom_url,
        'total_sessions': total_sessions,
        'announcements': announcements,
    })


@login_required
def check_in(request, session_id):
    if request.user.is_staff:
        return redirect('admin_overview')
    profile = get_profile(request.user)
    session = get_object_or_404(Session, pk=session_id, batch=profile.batch, is_active=True)
    custom = TraineeZoomLink.objects.filter(session=session, trainee=profile).first()
    zoom_url = custom.zoom_url if custom else session.zoom_url
    AttendanceRecord.objects.get_or_create(
        trainee=profile,
        session=session,
        defaults={
            'status': 'present',
            'zoom_url_snapshot': zoom_url,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:1000],
        }
    )
    messages.success(request, 'تم تسجيل حضورك بنجاح')
    return redirect('trainee_home')


@login_required
def trainee_schedule(request):
    if request.user.is_staff:
        return redirect('admin_overview')
    profile = get_profile(request.user)
    sessions = Session.objects.filter(batch=profile.batch).order_by('-date') if profile.batch else []
    records = {r.session_id: r for r in AttendanceRecord.objects.filter(trainee=profile)}
    return render(request, 'attendance/trainee_schedule.html', {'profile': profile, 'sessions': sessions, 'records': records})


@login_required
def trainee_calendar(request):
    if request.user.is_staff:
        return redirect('admin_overview')
    profile = get_profile(request.user)
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    records = AttendanceRecord.objects.filter(trainee=profile, session__date__year=year, session__date__month=month).select_related('session')
    present_days = {r.session.date.day: r for r in records}
    prev_month = month - 1 or 12
    prev_year = year - 1 if month == 1 else year
    next_month = month + 1 if month < 12 else 1
    next_year = year + 1 if month == 12 else year
    month_names = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    return render(request, 'attendance/trainee_calendar.html', {
        'profile': profile,
        'weeks': weeks,
        'month': month,
        'year': year,
        'month_name': month_names[month - 1],
        'present_days': present_days,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    })


@login_required
def trainee_profile(request):
    if request.user.is_staff:
        return redirect('admin_overview')
    profile = get_profile(request.user)
    profile_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(request.user)
    if request.method == 'POST' and request.POST.get('form_type') == 'profile':
        profile_form = ProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'تم حفظ بياناتك الشخصية')
            return redirect('trainee_profile')
    if request.method == 'POST' and request.POST.get('form_type') == 'password':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'تم تحديث كلمة المرور')
            return redirect('trainee_profile')
    return render(request, 'attendance/trainee_profile.html', {
        'profile': profile,
        'profile_form': profile_form,
        'password_form': password_form,
    })

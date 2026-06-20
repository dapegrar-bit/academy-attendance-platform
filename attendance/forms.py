from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Batch, Session, TraineeProfile, SiteSetting


class ArabicAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='اسم المستخدم', widget=forms.TextInput(attrs={'placeholder': 'أدخل اسم المستخدم'}))
    password = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))


class RegisterForm(forms.Form):
    full_name = forms.CharField(label='الاسم الكامل', max_length=180, widget=forms.TextInput(attrs={'placeholder': 'مثال: عبد الله الشهري'}))
    batch = forms.ModelChoiceField(label='الدفعة / المجموعة التدريبية', queryset=Batch.objects.filter(is_active=True), required=False, empty_label='اختر الدفعة...')
    username = forms.CharField(label='اسم المستخدم', max_length=150, widget=forms.TextInput(attrs={'placeholder': 'بدون فراغات، حروف إنجليزية'}))
    phone = forms.CharField(label='رقم الجوال', max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': '05XXXXXXXX'}))
    password = forms.CharField(label='كلمة المرور', min_length=4, widget=forms.PasswordInput(attrs={'placeholder': '4 أحرف على الأقل'}))

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if ' ' in username:
            raise forms.ValidationError('اسم المستخدم لا يقبل الفراغات.')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('اسم المستخدم موجود مسبقًا.')
        return username


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'description', 'color', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.RadioSelect,
        }


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['batch', 'title', 'description', 'date', 'start_time', 'end_time', 'zoom_url', 'is_active']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class TraineeAdminForm(forms.Form):
    full_name = forms.CharField(label='اسم المتدرب', max_length=180)
    username = forms.CharField(label='اسم المستخدم', max_length=150)
    phone = forms.CharField(label='رقم الجوال', max_length=30, required=False)
    email = forms.EmailField(label='البريد الإلكتروني', required=False)
    batch = forms.ModelChoiceField(label='الدفعة', queryset=Batch.objects.filter(is_active=True), required=False, empty_label='بدون دفعة')
    password = forms.CharField(label='كلمة المرور', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'اتركها فارغة عند التعديل'}))

    def __init__(self, *args, instance=None, **kwargs):
        self.instance = instance
        super().__init__(*args, **kwargs)
        if instance:
            self.fields['username'].initial = instance.user.username
            self.fields['email'].initial = instance.user.email
            self.fields['full_name'].initial = instance.full_name
            self.fields['phone'].initial = instance.phone
            self.fields['batch'].initial = instance.batch

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username=username)
        if self.instance:
            qs = qs.exclude(pk=self.instance.user.pk)
        if qs.exists():
            raise forms.ValidationError('اسم المستخدم موجود مسبقًا.')
        return username

    def save(self):
        if self.instance:
            user = self.instance.user
        else:
            user = User()
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data.get('email') or ''
        user.first_name = self.cleaned_data['full_name']
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        elif not user.pk:
            user.set_password('1234')
        user.save()
        profile, _ = TraineeProfile.objects.get_or_create(user=user)
        profile.full_name = self.cleaned_data['full_name']
        profile.phone = self.cleaned_data.get('phone') or ''
        profile.batch = self.cleaned_data.get('batch')
        profile.save()
        return profile


class ProfileForm(forms.ModelForm):
    email = forms.EmailField(label='البريد الإلكتروني', required=False)

    class Meta:
        model = TraineeProfile
        fields = ['full_name', 'phone', 'batch']
        labels = {'full_name': 'الاسم الكامل', 'phone': 'رقم الجوال', 'batch': 'الدفعة التدريبية'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['batch'].queryset = Batch.objects.filter(is_active=True)
        self.fields['email'].initial = self.instance.user.email if self.instance and self.instance.user else ''

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.user.email = self.cleaned_data.get('email') or ''
        obj.user.first_name = obj.full_name
        if commit:
            obj.user.save()
            obj.save()
        return obj


class SiteSettingForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['academy_name', 'system_name', 'logo_url', 'primary_color', 'accent_color']

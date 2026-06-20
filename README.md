# منصة أكاديميتي لإدارة الحضور والغياب والمحاضرات

نظام عربي مبني بـ Django لإدارة حضور المتدربين، روابط Zoom، الدفعات، المتدربين، الاستيراد من Excel، سجلات الحضور، تنبيهات الغياب، والتقارير.

## أهم التحديثات في هذه النسخة

- إزالة بيانات الدخول التجريبية من واجهة تسجيل الدخول.
- إنشاء حساب المدير من متغيرات Render بدل عرض بيانات عامة في الصفحة.
- تحسين سرعة سجلات الحضور: العرض الافتراضي لليوم فقط مع ترقيم الصفحات.
- إصلاح دخول المتدربين ولوحة المتدرب.
- نقل عنوان النظام إلى أعلى الصفحة في المنتصف.
- إصلاح إنشاء وتعديل الدفعات واختيار لون الدفعة.
- استيراد المتدربين من Excel بصيغة xlsx.
- تصدير المتدربين CSV.
- إرسال تنبيه للغائبين داخل حساب المتدرب وعبر البريد عند ضبط SMTP.
- إضافة تذييل الحقوق في جميع الصفحات.
- استخدام خط Cairo في كل الموقع.

## صيغة ملف Excel للاستيراد

الصف الأول يحتوي العناوين التالية:

| الاسم الكامل | اسم المستخدم | رقم الجوال | البريد الإلكتروني | الدفعة | كلمة المرور |
|---|---|---|---|---|---|
| سارة العتيبي | sara01 | 0500000000 | sara@example.com | دفعة تطوير الويب | S@ra2026 |

يمكن أيضًا استخدام عناوين إنجليزية:

`full_name, username, phone, email, batch, password`

## تشغيل محلي

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py init_platform
python manage.py runserver
```

قبل تشغيل `init_platform` محليًا ضعي داخل `.env`:

```env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=كلمة_مرور_قوية
```

## إعداد Render

Build Command:

```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start Command:

```bash
python manage.py migrate --noinput && python manage.py init_platform && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT
```

Environment Variables الأساسية:

```env
SECRET_KEY=Generate
DEBUG=False
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
LOGO_URL=https://i.top4top.io/p_3822gqcjp1.png
ADMIN_USERNAME=اسم_مدير_خاص
ADMIN_PASSWORD=كلمة_مرور_قوية_خاصة
ADMIN_EMAIL=your-email@example.com
ADMIN_FULL_NAME=مدير النظام
```

لتفعيل البريد الحقيقي، أضيفي إعدادات SMTP:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-smtp-user
EMAIL_HOST_PASSWORD=your-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
```

## تحديث التنبيهات الفورية

تمت إضافة تحديث خفي تلقائي للمتدربين عبر AJAX كل 5 ثوانٍ، حتى تظهر تنبيهات الإدارة للمتدرب مباشرة دون إعادة تحميل الصفحة. يعمل ذلك من خلال:

- `panel/notifications/poll/` لجلب التنبيهات الجديدة.
- `panel/notifications/read/` لتعليم التنبيه كمقروء بعد وصوله للمتدرب.
- `static/js/app.js` للتحديث الخفي وعرض بطاقة تنبيه فورية.
- `static/css/app.css` لتنسيق بطاقة التنبيه.

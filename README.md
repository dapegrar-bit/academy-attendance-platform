# منصة أكاديميتي لإدارة الحضور والغياب والمحاضرات

نظام عربي مبني بـ Django لإدارة حضور المتدربين، روابط Zoom، الدفعات، المتدربين، الاستيراد من Excel، سجلات الحضور، تنبيهات الغياب، التسجيلات، والتقارير.

## تحديثات هذه النسخة

- زر التحضير لا يظهر كزر أخضر ولا يسمح بالحضور إلا عند بداية وقت المحاضرة المسجل في الإدارة.
- إذا لم يتم تحديد وقت بداية المحاضرة فلن يفتح التحضير للمتدرب.
- عند انتهاء وقت المحاضرة، إذا تم تحديد وقت نهاية، يقفل التحضير تلقائيًا.
- إضافة زر إداري: **إرسال حضور فجائي** بجانب كل محاضرة، يفتح التحضير فورًا ويرسل تنبيهًا للمتدربين.
- إضافة رابط **المحاضرة المسجلة** لكل محاضرة، يضيفه المدير بعد انتهاء المحاضرة من رابط التليجرام.
- إضافة رابط **قناة التليجرام لتسجيلات المحاضرات** من إعدادات النظام، ويظهر للمتدرب أسفل جدول المحاضرات.
- استمرار نظام التنبيهات الفورية كل 5 ثوانٍ للمتدربين.
- الحفاظ على البيانات عند التحديث: التحديث يضيف حقولًا جديدة فقط ولا يحذف المستخدمين أو الحضور.

## مهم جدًا لحفظ البيانات في Render

إذا كان الموقع يستخدم SQLite داخل Render المجاني، فقد تضيع البيانات عند إعادة النشر أو إعادة تشغيل الخدمة لأن التخزين المحلي في الخدمات المجانية غير دائم. الحل الصحيح لحفظ المتدربين والحضور دائمًا هو استخدام قاعدة بيانات خارجية PostgreSQL وربطها بمتغير:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
```

الكود جاهز ويدعم `DATABASE_URL` تلقائيًا. عند توفر `DATABASE_URL` يستخدم PostgreSQL بدل SQLite.

لا ترفعي ملف `db.sqlite3` إلى GitHub، ولا تضعي `seed_demo` في Start Command. استخدمي الأمر الآمن التالي فقط:

```bash
python manage.py migrate --noinput && python manage.py init_platform && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT
```

أمر `migrate` يحافظ على البيانات ويضيف الحقول الجديدة، ولا يحذف الجداول.

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
TELEGRAM_CHANNEL_URL=https://t.me/your_channel
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

## صيغة ملف Excel للاستيراد

الصف الأول يحتوي العناوين التالية:

| الاسم الكامل | اسم المستخدم | رقم الجوال | البريد الإلكتروني | الدفعة | كلمة المرور |
|---|---|---|---|---|---|
| سارة العتيبي | sara01 | 0500000000 | sara@example.com | دفعة تطوير الويب | S@ra2026 |

يمكن أيضًا استخدام عناوين إنجليزية:

`full_name, username, phone, email, batch, password`

## طريقة استخدام الحضور الفجائي

من لوحة الإدارة → المحاضرات والروابط:

1. أمام المحاضرة اضغط **إرسال حضور فجائي**.
2. يصل تنبيه فوري للمتدربين داخل الموقع.
3. يصبح زر التحضير متاحًا لهم حتى لو لم يكن وقت المحاضرة قد بدأ.
4. لإيقافه اضغط **إيقاف الفجائي**.

## التسجيلات والتليجرام

- رابط القناة العام يضاف من: **الإعدادات → رابط قناة التليجرام لتسجيلات المحاضرات**.
- رابط تسجيل محاضرة محددة يضاف من: **المحاضرات والروابط → تعديل المحاضرة → رابط المحاضرة المسجلة من التليجرام**.

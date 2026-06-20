# منصة أكاديميتي لإدارة الحضور والغياب والمحاضرات

نظام عربي مبني بـ Django لإدارة حضور المتدربين، روابط Zoom، الدفعات، المتدربين، الاستيراد من Excel، سجلات الحضور، تنبيهات الغياب، التسجيلات، والتقارير.

## تحديث حفظ البيانات الدائم

هذه النسخة محدثة حتى تحفظ بيانات الموقع على قاعدة بيانات PostgreSQL في السيرفر بدل SQLite المحلي.

### لماذا كانت البيانات تُحذف؟

- GitHub يحفظ الكود فقط، ولا يحفظ قاعدة بيانات الموقع.
- SQLite يحفظ البيانات في ملف داخل السيرفر مثل `db.sqlite3`.
- Render في الخدمات العادية يستخدم نظام ملفات مؤقتًا؛ أي ملف ينشئه التطبيق أثناء التشغيل قد يضيع عند إعادة النشر أو إعادة التشغيل.
- الحل الصحيح: ربط Django بقاعدة PostgreSQL عبر متغير `DATABASE_URL`.

### ماذا تغيّر في الكود؟

- دعم كامل لـ PostgreSQL عبر `DATABASE_URL`.
- إضافة حماية إنتاجية: عند تشغيل الموقع على Render بدون `DATABASE_URL` سيظهر خطأ واضح بدل أن يعمل على SQLite ويفقد البيانات لاحقًا.
- تحديث `render.yaml` لإضافة قاعدة بيانات Render Postgres وربطها تلقائيًا بالخدمة عند استخدام Blueprint.
- الإبقاء على SQLite للتشغيل المحلي فقط على جهازك.
- لا يوجد أي أمر يحذف المستخدمين أو الحضور أو الدفعات.
- لا تستخدم `seed_demo` في Render نهائيًا.

## تحديثات النظام السابقة الموجودة في هذه النسخة

- زر التحضير لا يظهر كزر أخضر ولا يسمح بالحضور إلا عند بداية وقت المحاضرة المسجل في الإدارة.
- إذا لم يتم تحديد وقت بداية المحاضرة فلن يفتح التحضير للمتدرب.
- عند انتهاء وقت المحاضرة، إذا تم تحديد وقت نهاية، يقفل التحضير تلقائيًا.
- زر إداري: **إرسال حضور فجائي** بجانب كل محاضرة، يفتح التحضير فورًا ويرسل تنبيهًا للمتدربين.
- رابط **المحاضرة المسجلة** لكل محاضرة، يضيفه المدير بعد انتهاء المحاضرة من رابط التليجرام.
- رابط **قناة التليجرام لتسجيلات المحاضرات** من إعدادات النظام، ويظهر للمتدرب أسفل جدول المحاضرات.
- استمرار نظام التنبيهات الفورية كل 5 ثوانٍ للمتدربين.

## إعداد Render الصحيح لحفظ البيانات

### الخيار الأفضل: إنشاء PostgreSQL يدويًا من Render

1. من Render اضغط **New**.
2. اختر **Postgres**.
3. الاسم المقترح: `academy-attendance-db`.
4. اختر نفس Region الموجود فيه Web Service.
5. بعد الإنشاء افتح قاعدة البيانات.
6. من **Connect** انسخ **Internal Database URL**.
7. افتح Web Service الخاص بالموقع.
8. ادخل إلى **Environment**.
9. أضف:

```env
DATABASE_URL=ضع_هنا_Internal_Database_URL
REQUIRE_DATABASE_URL=True
```

10. اضغط **Save, rebuild, and deploy**.

### Build Command

```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### Start Command

```bash
python manage.py migrate --noinput && python manage.py init_platform && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT
```

### Environment Variables الأساسية

```env
SECRET_KEY=Generate
DEBUG=False
ALLOWED_HOSTS=.onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://*.onrender.com
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
REQUIRE_DATABASE_URL=True
LOGO_URL=https://i.top4top.io/p_3822gqcjp1.png
TELEGRAM_CHANNEL_URL=https://t.me/your_channel
ADMIN_USERNAME=اسم_مدير_خاص
ADMIN_PASSWORD=كلمة_مرور_قوية_خاصة
ADMIN_EMAIL=your-email@example.com
ADMIN_FULL_NAME=مدير النظام
```

لتفعيل البريد الحقيقي:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-smtp-user
EMAIL_HOST_PASSWORD=your-smtp-password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=your-email@example.com
```

## تشغيل محلي على جهازك

محليًا فقط يمكن استخدام SQLite:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py init_platform
python manage.py runserver
```

عند التشغيل المحلي، إذا تركت `DATABASE_URL` فارغًا و`REQUIRE_DATABASE_URL=False` سيستخدم SQLite على جهازك.

## مهم جدًا

- لا ترفعي ملف `db.sqlite3` إلى GitHub.
- لا تضعي `python manage.py seed_demo` في Start Command.
- لا تعتمدي على GitHub لحفظ بيانات المتدربين؛ GitHub للكود فقط.
- قاعدة البيانات الدائمة تكون في PostgreSQL على Render أو Supabase أو Neon أو أي مزود PostgreSQL.
- Render Postgres المجاني مناسب للاختبار، لكن إن كان الموقع رسميًا ومستمرًا يفضل اختيار خطة مدفوعة أو قاعدة PostgreSQL دائمة.

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

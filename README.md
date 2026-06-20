# منصة أكاديميتي لإدارة الحضور والغياب والمحاضرات

نظام عربي RTL مبني بـ Django لإدارة تحضير المتدربين في الأكاديمية. لا يظهر رابط Zoom للمتدرب إلا بعد الضغط على زر التحضير، ويتم تسجيل وقت الحضور وبيانات المتدرب والدفعة والمحاضرة والرابط المستخدم.

## المميزات

- تسجيل دخول للإدارة والمتدربين.
- إنشاء حساب متدرب ذاتيًا أو إضافة متدرب من الإدارة.
- إدارة الدفعات التدريبية.
- إدارة المحاضرات وروابط Zoom حسب الدفعة.
- تحضير يومي قبل ظهور رابط Zoom.
- حفظ وقت التحضير وIP والمتصفح والرابط المستخدم.
- لوحة متدرب: نسبة الحضور، زر التحضير، جدول المحاضرات، سجل شهري، تحديث الحساب.
- لوحة إدارة: نظرة عامة، الدفعات، المتدربون، المحاضرات، سجلات الحضور، التقارير، الإعدادات.
- فلترة حسب الدفعة والتاريخ والحالة والاسم.
- تصدير CSV.
- تصميم داكن مطابق للصور المرفقة بدرجة كبيرة.
- شعار أكاديميتي مضاف من الرابط: https://i.top4top.io/p_3822gqcjp1.png
- جاهز للرفع على GitHub والتشغيل على Render.

## بيانات تجربة

بعد تشغيل أمر البيانات التجريبية:

```text
الإدارة:
admin
admin123

المتدرب:
sara
1234
```

## التشغيل المحلي

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

افتحي:

```text
http://127.0.0.1:8000/
```

## رفع المشروع على GitHub من المتصفح

1. افتحي مستودع GitHub.
2. احذفي الملفات القديمة إن كانت ناقصة أو ارفعي هذا المشروع كاملًا.
3. اضغطي `Add file` ثم `Upload files`.
4. اسحبي كل ملفات ومجلدات المشروع، خصوصًا:

```text
academy_platform
attendance
templates
static
docs
manage.py
requirements.txt
runtime.txt
Procfile
render.yaml
.env.example
README.md
```

5. اضغطي `Commit changes`.

## إعداد Render

في صفحة New Web Service:

```text
Language: Python 3
Branch: main
Root Directory: فارغ
```

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start Command:

```bash
python manage.py migrate && python manage.py seed_demo && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT
```

Environment Variables:

```text
SECRET_KEY = Generate
DEBUG = False
ALLOWED_HOSTS = .onrender.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS = https://*.onrender.com
```

## ملاحظة مهمة للبيانات الدائمة

للتجربة يعمل النظام بدون PostgreSQL باستخدام SQLite. للتشغيل الحقيقي وحفظ بيانات الحضور بشكل دائم، أنشئي قاعدة PostgreSQL في Render ثم أضيفي متغير:

```text
DATABASE_URL = رابط قاعدة البيانات من Render
```

الكود يدعم PostgreSQL تلقائيًا عند وجود DATABASE_URL.

# ربط الموقع بقاعدة PostgreSQL دائمة على Render

هذه الخطوات تمنع حذف بيانات المتدربين والحضور عند إعادة التشغيل أو إعادة النشر.

## 1) إنشاء قاعدة بيانات

Render Dashboard → New → Postgres

- Name: academy-attendance-db
- Region: نفس منطقة خدمة الموقع
- Plan: Free للتجربة أو Basic للاستخدام المستمر

بعد الإنشاء انتظر حتى تصبح الحالة Available.

## 2) نسخ الرابط الداخلي

افتح قاعدة البيانات → Connect → انسخ Internal Database URL.

يكون شكله قريبًا من:

```text
postgresql://academy_user:password@host:5432/academy_attendance
```

## 3) ربطها بخدمة الموقع

افتح Web Service → Environment → Add Environment Variable:

```env
DATABASE_URL=الرابط_الداخلي_الذي_نسخته
REQUIRE_DATABASE_URL=True
```

ثم اضغط:

```text
Save, rebuild, and deploy
```

## 4) الأوامر الصحيحة في Render

Build Command:

```bash
pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput
```

Start Command:

```bash
python manage.py migrate --noinput && python manage.py init_platform && gunicorn academy_platform.wsgi:application --bind 0.0.0.0:$PORT
```

## 5) ممنوع استخدام seed_demo

لا تضع هذا الأمر في Render:

```bash
python manage.py seed_demo
```

لأنه خاص ببيانات التجربة فقط.

## 6) ملاحظة عن البيانات القديمة

إذا كانت البيانات القديمة محفوظة داخل SQLite على Render ثم حدث Restart/Deploy، فقد تكون ضاعت من Render ولا يمكن استرجاعها إلا إذا كان عندك تصدير سابق CSV/Excel/Backup.

بعد ربط PostgreSQL، البيانات الجديدة ستبقى في قاعدة البيانات ولا تعتمد على جهازك أو GitHub.

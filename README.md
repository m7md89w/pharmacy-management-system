# 💊 Pharmacy Management System (نظام إدارة الصيدلية)

نظام متكامل لإدارة الصيدلية مبني باستخدام **Flask** للـ Backend و **Streamlit** للـ Frontend مع قاعدة بيانات **SQLite**.

---

## 🚀 طريقة التشغيل (How to Run)

لتشغيل النظام على جهازك المحلي، اتبع الخطوات التالية بالترتيب:

### 1. إعداد البيئة الافتراضية والاعتماديات
إذا لم تكن مفعلة، قم بتثبيت المكونات المطلوبة داخل المجلد الرئيسي:
```bash
# تفعيل البيئة الافتراضية (Windows PowerShell)
.venv\Scripts\Activate.ps1

# تثبيت الحزم المطلوبة (تم تثبيتها بالفعل)
pip install -r pharmacy-management-system/requirements.txt
pip install streamlit
```

### 2. إعداد ملف البيئة (`.env`)
قم بنسخ ملف الإعدادات التجريبي `.env.example` لإنشاء ملف `.env` حقيقي:
```bash
cp .env.example .env
```
*ملاحظة: ملف `.env` مهيأ تلقائياً بكلمة سر للآدمن ومفتاح تشفير JWT عشوائي وآمن.*

### 3. إنشاء وتغذية قاعدة البيانات (Database Init & Seed)
قم بإنشاء الجداول وحقن البيانات التجريبية الأولية (البيانات تشمل الأدوية الافتراضية وحساب الآدمن):
```bash
# إنشاء الجداول
python pharmacy-management-system/create_database.py

# تغذية قاعدة البيانات بالبيانات الأولية
python pharmacy-management-system/seed_data.py
```
*بيانات الدخول للآدمن بعد التغذية:*
* **اسم المستخدم:** `admin`
* **كلمة المرور:** `Admin@123456`

### 4. تشغيل الخادم الخلفي (Run Flask API)
قم بتشغيل خادم الـ API الخلفي:
```bash
python pharmacy-management-system/main.py
```
سيبدأ الخادم بالعمل على الرابط المحلي: `http://127.0.0.1:5000`

### 5. تشغيل الواجهة الأمامية (Run Streamlit Frontend)
في نافذة تيرمينال جديدة (مع تفعيل البيئة الافتراضية)، قم بتشغيل واجهة المستخدم:
```bash
streamlit run pharmacy-management-system/frontend/app.py
```
ستفتح الواجهة تلقائياً في متصفحك على الرابط: `http://localhost:8501`

---

## 🧪 تشغيل الفحوصات (Running Tests)
يمكنك اختبار كفاءة وعمل النظام ونظام فحص تفاعلات الأدوية في أي وقت عبر تشغيل:
```bash
python pharmacy-management-system/test.py
```
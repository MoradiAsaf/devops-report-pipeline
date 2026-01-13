# 📊 DevOps Report Pipeline

מערכת אוטומטית מבוססת **Jenkins + Python** ליצירת דוחות, ניהול לוגים, והפקת דוח HTML מרכזי עם אפשרות לשליחה במייל.

הפרויקט מריץ סקריפט Python שמקבל קובץ Excel יומי, מייצר ממנו דוחות PDF, בונה דוח HTML מסכם, שומר לוג מסודר לכל ריצה, ומפרסם את התוצאות דרך Jenkins.

---

## 🚀 יכולות עיקריות

* הרצת Pipeline ב־Jenkins (Windows / Linux)
* יצירת קובץ לוג ייעודי לכל Build
* עיבוד קובץ Excel יומי
* יצירת דוחות PDF
* בניית דוח HTML מרכזי
* פרסום הדוח דרך Jenkins (Publish HTML)
* ארכוב דוחות ולוגים כ־Artifacts
* שליחת מייל אוטומטית עם קישור לדוח
* תמיכה בפרמטרים (תאריך, מערכת הפעלה, מייל יעד)

---

## 🧱 מבנה הפרויקט

```
devops-report-pipeline/
│
├── main.py                 # סקריפט פייתון ראשי
├── report.html             # דוח HTML שנוצר אוטומטית
├── requirements.txt        # תלויות פייתון
├── Jenkinsfile             # קובץ ה־Pipeline
│
├── logs/
│   └── run_XX.log           # לוג לכל ריצה
│
├── pdf_reports/
│   └── <date>/
│       └── *.pdf            # דוחות שנוצרו
│
└── README.md
```

---

## ⚙️ דרישות מערכת

### Jenkins

* Jenkins 2.x
* פלאגינים:

  * Pipeline
  * Publish HTML Reports
  * Email Extension / Mailer
  * Role-based Authorization (רשות)

### Python

* Python 3.9+
* התקנת תלויות:

```
pip install -r requirements.txt
```

---

## ▶️ פרמטרים של ה־Pipeline

בעת הרצה ידנית:

* **RUN_ON** – מערכת הפעלה: `windows` / `linux`
* **RUN_DATE** – תאריך קובץ האקסל (לדוגמה: `09.01.2026`)
* **REPORT_EMAIL** – מייל לשליחת הדוח (אופציונלי)

---

## 🧠 תהליך ריצה

1. ניקוי סביבת העבודה
2. יצירת קובץ לוג
3. בדיקת סביבת פייתון
4. הרצת main.py
5. יצירת דוחות PDF
6. יצירת דוח HTML
7. סגירת הלוג
8. רענון HTML עם הלוג הסופי
9. ארכוב תוצרים
10. פרסום הדוח ב־Jenkins
11. שליחת מייל (אם הוגדר)

---

## 🌐 צפייה בדוח

לאחר ריצה:

```
Job → Last Build → HTML Report
```

או קישור חיצוני (אם מוגדר):

```
https://<ngrok>/job/<JOB_NAME>/<BUILD_NUMBER>/HTML_20Report/
```

---

## 📧 מיילים

* נשלחים דרך SMTP שמוגדר ב־Jenkins
* כוללים סטטוס, מספר Build וקישור לדוח

---

## 📝 לוגים

* לכל ריצה:

```
logs/run_<BUILD_NUMBER>.log
```

* הלוג נשמר כ־artifact ומוצג בדוח ה־HTML

---

## 🔐 הרשאות

* admin – ניהול מלא
* user – צפייה והרצה בלבד

---

## 🛠 טכנולוגיות

* Jenkins Pipeline (Groovy)
* Python
* HTML
* SMTP
* GitHub
* Ngrok

---

## 📌 הערות

המערכת נבנתה כדי לדמות סביבת DevOps אמיתית, כולל לוגים, דוחות, ארכוב, פרסום ומיילים – ומתאימה לפרויקט גמר או מערכת תפעולית אמיתית.

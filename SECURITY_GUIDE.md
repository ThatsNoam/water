# 🔐 מדריך אבטחה - מערכת בקרה מרחוק

## 🛡️ סקירת האבטחה

מערכת הבקרה המרחוק כוללת כעת הצפנה מלאה עם SSL/TLS לכל התקשורת ברשת.

## 🔑 רכיבי האבטחה

### 1. **הצפנת סיסמאות (Salt + SHA256)**
- ✅ כל סיסמה מקבלת salt ייחודי של 64 תווים
- ✅ שימוש ב-SHA256 עם salt למניעת Rainbow Table attacks
- ✅ מיגרציה אוטומטית למשתמשים קיימים

### 2. **הצפנת רשת SSL/TLS**
- 🔐 **כל התקשורת מוצפנת** עם SSL/TLS
- 🔐 **אישורי SSL אוטומטיים** - נוצרים באופן אוטומטי
- 🔐 **הצפנת צילומי מסך** - כל הנתונים הרגישים מוגנים
- 🔐 **הצפנת פקודות** - עכבר, מקלדת, וטקסט

### 3. **ארכיטקטורת אבטחה**

```
🖥️ לקוח (Client)
    ↕️ 🔐 SSL/TLS
🛡️ שרת מתווך (Mediator)
    ↕️ 🔐 SSL/TLS  
🔧 טכנאי (Technician)
    ↕️ 🔐 SSL/TLS
🖥️ לקוח (Client) - חיבור ישיר
```

## 📁 קבצי אישורי SSL

המערכת יוצרת באופן אוטומטי:

- `ca.crt` - אישור רשות אישורים (Certificate Authority)
- `ca.key` - מפתח פרטי לרשות האישורים
- `server.crt` - אישור השרת
- `server.key` - מפתח פרטי של השרת

## 🔧 הגדרות אבטחה

### **חיבורים מאובטחים:**
1. **לקוח ← → מתווך**: SSL/TLS על פורט 5556
2. **טכנאי ← → מתווך**: SSL/TLS על פורט 5556  
3. **טכנאי ← → לקוח**: SSL/TLS על פורט 5555

### **הצפנה ברמת הנתונים:**
- צילומי מסך: Base64 → Pickle → SSL
- פקודות עכבר/מקלדת: JSON → SSL
- הודעות מערכת: JSON → SSL

## 🚀 אתחול המערכת המאובטחת

### שלב 1: התקנת חבילות
```bash
pip install -r requirements.txt
```

### שלב 2: אתחול אישורי SSL
```bash
python -c "import ssl_utils; ssl_utils.initialize_ssl()"
```

### שלב 3: הפעלת השרת המתווך
```bash
python mediator_server.py
```

### שלב 4: הפעלת לקוח
```bash
python client_with_mediator.py
```

### שלב 5: הפעלת טכנאי
```bash
python technician_with_mediator.py
```

## 🔍 אינדיקטורי אבטחה בממשק

### **שרת מתווך:**
- `Running (🔐 SSL)` - שרת פועל עם הצפנה

### **לקוח:**
- `🔐 Waiting (SSL)...` - ממתין לחיבור מאובטח
- Log: `🔐 Secure control server started`

### **טכנאי:**
- Log: `🔐 Securely connected to client`

## ⚠️ התראות אבטחה

במקרה של כשל באבטחה, המערכת תציג:
- `❌ Failed to initialize SSL certificates`
- `❌ Failed to establish secure connection`

## 🔐 רמת הגנה נוכחית

| **רכיב** | **רמת אבטחה** | **פרטים** |
|----------|---------------|-----------|
| **סיסמאות** | 🟢 **גבוהה** | Salt + SHA256 |
| **מאגר נתונים** | 🟢 **גבוהה** | Hash מאובטח |
| **תקשורת רשת** | 🟢 **גבוהה** | SSL/TLS מלא |
| **צילומי מסך** | 🟢 **גבוהה** | SSL מוצפן |
| **פקודות בקרה** | 🟢 **גבוהה** | SSL מוצפן |

## 🛠️ פתרון בעיות אבטחה

### בעיה: "SSL certificates not found"
**פתרון:**
```bash
python -c "import ssl_utils; ssl_utils.initialize_ssl()"
```

### בעיה: "Failed to establish secure connection"
**בדיקות:**
1. ודא שהשרת המתווך פועל עם SSL
2. בדוק שקבצי האישורים קיימים
3. ודא שהפורטים פתוחים בחומת האש

### בעיה: אישורי SSL פגום
**פתרון:**
```bash
# מחק אישורים ישנים
del *.crt *.key

# יצור אישורים חדשים
python -c "import ssl_utils; ssl_utils.initialize_ssl()"
```

## 📋 רשימת בדיקות אבטחה

- [x] הצפנת סיסמאות עם Salt
- [x] הצפנת תקשורת SSL/TLS
- [x] הצפנת צילומי מסך
- [x] הצפנת פקודות עכבר ומקלדת
- [x] אישורי SSL אוטומטיים
- [x] אינדיקטורי אבטחה בממשק
- [x] לוגים מאובטחים
- [x] טיפול בשגיאות אבטחה

## 🎯 המלצות נוספות

1. **גיבוי אישורים**: גבה את קבצי ה-SSL במקום בטוח
2. **חידוש אישורים**: חדש אישורים מדי שנה
3. **מעקב לוגים**: עקוב אחר הודעות אבטחה בלוגים
4. **עדכון תקופתי**: עדכן את חבילת cryptography

---

**📞 תמיכה טכנית**: במקרה של בעיות אבטחה, בדוק את הלוגים או צור אישורים חדשים. 
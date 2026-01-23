# Expenses Press | سجل المصروفات

A simple and fast expense recording module for Odoo 18 Community Edition.

تطبيق بسيط وسريع لتسجيل المصروفات لأودو 18.

![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue)
![License](https://img.shields.io/badge/License-LGPL--3-green)

---

## Features | المميزات

### English
- ✅ **Quick Expense Entry** - Record expenses with just description, amount, and category
- ✅ **Automatic Journal Entries** - Every expense automatically creates a posted journal entry
- ✅ **P&L Integration** - Expenses appear directly in your Profit & Loss report
- ✅ **Easy Editing** - Edit any expense and journal entries update automatically
- ✅ **Arabic Support** - Full Arabic language translation included
- ✅ **Category Management** - Create custom expense categories linked to your chart of accounts

### العربية
- ✅ **إدخال سريع للمصروفات** - سجل المصروفات بالوصف والمبلغ والتصنيف فقط
- ✅ **قيود يومية تلقائية** - كل مصروف ينشئ قيد يومية مرحّل تلقائياً
- ✅ **تكامل مع الأرباح والخسائر** - المصروفات تظهر مباشرة في تقرير الأرباح والخسائر
- ✅ **تعديل سهل** - عدّل أي مصروف والقيود المحاسبية تتحدث تلقائياً
- ✅ **دعم اللغة العربية** - ترجمة عربية كاملة
- ✅ **إدارة التصنيفات** - أنشئ تصنيفات مخصصة مربوطة بدليل الحسابات

---

## Screenshots | لقطات الشاشة

### Expense Form | نموذج المصروف
Simple form with only essential fields:
- Description (الوصف)
- Amount (المبلغ)
- Category (التصنيف)
- Date (التاريخ)
- Journal (دفتر اليومية)

### Expense List | قائمة المصروفات
View all expenses with totals and status indicators.

---

## Installation | التثبيت

### English

1. **Download** the module and place it in your Odoo addons directory
   ```bash
   cd /path/to/odoo/addons
   git clone https://github.com/yourusername/expense_express.git
   ```

2. **Restart** Odoo server
   ```bash
   sudo systemctl restart odoo
   ```

3. **Update Apps List**
   - Go to Apps menu
   - Click "Update Apps List"

4. **Install**
   - Search for "Expenses Press"
   - Click Install

### العربية

1. **حمّل** الموديول وضعه في مجلد إضافات أودو

2. **أعد تشغيل** خادم أودو

3. **حدّث قائمة التطبيقات**
   - اذهب إلى قائمة التطبيقات
   - اضغط "تحديث قائمة التطبيقات"

4. **ثبّت**
   - ابحث عن "Expenses Press"
   - اضغط تثبيت

---

## Configuration | الإعداد

### Step 1: Create Categories | الخطوة 1: إنشاء التصنيفات

1. Go to **Expenses Press → Configuration → Categories**
2. Create your expense categories:
   - Food & Ingredients (المواد الغذائية)
   - Utilities (المرافق)
   - Rent (الإيجار)
   - Transport (النقل)
   - Supplies (المستلزمات)
   - Other (أخرى)

3. **Important**: Link each category to an expense account from your Chart of Accounts

### Step 2: Start Recording | الخطوة 2: ابدأ التسجيل

1. Go to **Expenses Press → All Expenses**
2. Click **New**
3. Fill in the details and save
4. The journal entry is created and posted automatically!

---

## How It Works | كيف يعمل

```
┌─────────────────┐         ┌──────────────────┐
│   New Expense   │  ────►  │  Journal Entry   │
│                 │         │                  │
│ - Description   │         │ DR: Expense Acc  │
│ - Amount: $100  │         │ CR: Cash/Bank    │
│ - Category      │         │                  │
│ - Date          │         │ Status: Posted   │
└─────────────────┘         └──────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │   P&L Report     │
                          │                  │
                          │ Expenses: $100   │
                          └──────────────────┘
```

---

## Dependencies | المتطلبات

- Odoo 18.0 Community or Enterprise
- `account` module (Invoicing/Accounting)

---

## Module Structure | هيكل الموديول

```
expense_express/
├── __init__.py
├── __manifest__.py
├── i18n/
│   └── ar.po                 # Arabic translation
├── models/
│   ├── __init__.py
│   ├── expense_category.py   # Category model
│   └── expense_express.py    # Main expense model
├── security/
│   └── ir.model.access.csv   # Access rights
├── static/
│   ├── description/
│   │   └── icon.svg          # App icon
│   └── src/css/
│       └── expense_express.css
└── views/
    ├── expense_express_menus.xml
    └── expense_express_views.xml
```

---

## Support | الدعم

For issues and feature requests, please create an issue on GitHub.

للمشاكل وطلبات الميزات الجديدة، يرجى إنشاء issue على GitHub.

---

## Author | المطور

**Yousif Shakir** | يوسف شاكر

**Company**: Donia Link | دنيا لينك

**Website**: [www.donialink.com](https://www.donialink.com)

---

## License | الرخصة

This module is licensed under LGPL-3.

هذا الموديول مرخص تحت LGPL-3.

---

## Changelog | سجل التغييرات

### Version 18.0.1.0.0
- Initial release
- Expense recording with automatic journal entries
- Arabic language support
- Category management with account linking

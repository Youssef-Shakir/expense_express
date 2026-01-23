# -*- coding: utf-8 -*-
{
    'name': 'Expenses Press',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Expenses',
    'summary': 'Quick and easy expense recording for business owners',
    'description': """
Expenses Press - سجل مصروفاتك بسهولة
=====================================

A simple, fast way to record business expenses with automatic journal entries.
تطبيق بسيط وسريع لتسجيل مصروفات العمل مع إنشاء قيود محاسبية تلقائية.

Features | المميزات:
--------------------
* Quick expense entry: description, amount, category
  إدخال سريع للمصروفات: الوصف، المبلغ، التصنيف

* Automatic journal entry creation (posts to P&L)
  إنشاء قيود يومية تلقائياً (تظهر في تقرير الأرباح والخسائر)

* Easy editing of expenses (auto-updates journal entries)
  تعديل سهل للمصروفات (تحديث تلقائي للقيود المحاسبية)

* Arabic language support
  دعم اللغة العربية

Perfect for restaurant owners and small business operators.
مثالي لأصحاب المطاعم والأعمال الصغيرة.

Setup | الإعداد:
----------------
1. Go to Configuration > Categories
   اذهب إلى الإعدادات > التصنيفات

2. Create expense categories and link each to an expense account
   أنشئ تصنيفات المصروفات واربط كل تصنيف بحساب مصروفات

3. Start recording expenses!
   ابدأ بتسجيل المصروفات!

Developed by Yousif Shakir | تطوير يوسف شاكر
    """,
    'author': 'Donia Link',
    'website': 'https://www.donialink.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/expense_express_views.xml',
        'views/expense_express_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'expense_express/static/src/css/expense_express.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 10,
}

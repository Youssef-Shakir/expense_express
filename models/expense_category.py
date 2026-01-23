# -*- coding: utf-8 -*-
from odoo import models, fields


class ExpenseCategory(models.Model):
    """Expense categories with linked expense accounts."""
    _name = 'expense.category'
    _description = 'Expense Category'
    _order = 'sequence, name'

    name = fields.Char('Category Name', required=True, translate=True)
    code = fields.Char('Code', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    account_id = fields.Many2one(
        'account.account',
        string='Expense Account',
        required=True,
        help='Account used for this expense category in journal entries'
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Category code must be unique!')
    ]

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ExpenseExpress(models.Model):
    """Simple expense recording with automatic journal entries."""
    _name = 'expense.express'
    _description = 'Expense'
    _order = 'date desc, id desc'

    name = fields.Char(
        'Description',
        required=True,
        help='What was this expense for?'
    )

    amount = fields.Monetary(
        'Amount',
        required=True,
        currency_field='currency_id'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        required=True
    )

    date = fields.Date(
        'Date',
        required=True,
        default=fields.Date.today
    )

    category_id = fields.Many2one(
        'expense.category',
        string='Category',
        required=True
    )

    notes = fields.Text('Notes')

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True,
        default=lambda self: self._default_journal(),
        domain="[('type', 'in', ['purchase', 'cash', 'bank'])]"
    )

    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        copy=False
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    ], string='Status', default='draft', readonly=True)

    @api.model
    def _default_journal(self):
        """Get default expense journal (cash or purchase)."""
        journal = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.env.company.id)
        ], limit=1)
        if not journal:
            journal = self.env['account.journal'].search([
                ('type', '=', 'purchase'),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
        return journal

    def _prepare_move_values(self):
        """Prepare values for journal entry."""
        self.ensure_one()

        expense_account = self.category_id.account_id
        if not expense_account:
            raise UserError(_('Please set an expense account on category "%s"') % self.category_id.name)

        # Get the default credit account from journal
        journal = self.journal_id
        if journal.type == 'cash':
            credit_account = journal.default_account_id
        elif journal.type == 'bank':
            credit_account = journal.default_account_id
        else:
            # For purchase journal, use the company's payable account
            credit_account = self.company_id.account_journal_payment_credit_account_id
            if not credit_account:
                credit_account = journal.default_account_id

        if not credit_account:
            raise UserError(_('Please configure a default account on journal "%s"') % journal.name)

        return {
            'move_type': 'entry',
            'date': self.date,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'line_ids': [
                # Debit: Expense account
                (0, 0, {
                    'name': self.name,
                    'account_id': expense_account.id,
                    'debit': self.amount,
                    'credit': 0.0,
                }),
                # Credit: Cash/Bank/Payable account
                (0, 0, {
                    'name': self.name,
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': self.amount,
                }),
            ],
        }

    def action_post(self):
        """Create and post journal entry."""
        for expense in self:
            if expense.state == 'posted':
                continue

            # Create journal entry
            move_vals = expense._prepare_move_values()
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            expense.write({
                'move_id': move.id,
                'state': 'posted',
            })

    @api.model_create_multi
    def create(self, vals_list):
        """Create expense and auto-post."""
        records = super().create(vals_list)
        records.action_post()
        return records

    def write(self, vals):
        """Update expense and recreate journal entry if needed."""
        # Fields that affect the journal entry
        accounting_fields = {'amount', 'category_id', 'date', 'journal_id', 'name'}

        result = super().write(vals)

        # If accounting-related fields changed, recreate journal entry
        if accounting_fields & set(vals.keys()):
            for expense in self:
                if expense.move_id:
                    # Cancel and delete old entry
                    if expense.move_id.state == 'posted':
                        expense.move_id.button_draft()
                    expense.move_id.unlink()

                # Create new entry
                expense.state = 'draft'
                expense.action_post()

        return result

    def unlink(self):
        """Delete journal entry when expense is deleted."""
        moves = self.mapped('move_id')
        for move in moves:
            if move.state == 'posted':
                move.button_draft()
        moves.unlink()
        return super().unlink()

    def action_view_move(self):
        """Open related journal entry."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Journal Entry'),
            'res_model': 'account.move',
            'res_id': self.move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

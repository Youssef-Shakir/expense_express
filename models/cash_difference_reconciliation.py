# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CashDifferenceReconciliation(models.Model):
    """Reconcile POS cash differences by reclassifying them to expense categories."""
    _name = 'cash.difference.reconciliation'
    _description = 'Cash Difference Reconciliation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        'Reference',
        readonly=True,
        copy=False,
        default='New'
    )

    original_move_id = fields.Many2one(
        'account.move',
        string='Original Entry',
        readonly=True,
        ondelete='restrict',
        help='The original POS cash difference journal entry'
    )

    original_move_line_id = fields.Many2one(
        'account.move.line',
        string='Original Line',
        readonly=True,
        ondelete='restrict',
        help='The specific journal entry line with the cash difference'
    )

    date = fields.Date(
        'Date',
        readonly=True,
        help='Date of the cash difference'
    )

    amount = fields.Monetary(
        'Amount',
        currency_field='currency_id',
        readonly=True,
        help='Amount of the cash difference (always positive)'
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    original_account_id = fields.Many2one(
        'account.account',
        string='Original Account',
        readonly=True,
        help='The loss/gain account where the difference was originally posted'
    )

    difference_type = fields.Selection([
        ('loss', 'Cash Loss'),
        ('gain', 'Cash Gain'),
    ], string='Type', readonly=True, help='Whether this is a cash shortage (loss) or overage (gain)')

    category_id = fields.Many2one(
        'expense.category',
        string='Expense Category',
        help='Select a category to reclassify this cash difference'
    )

    correcting_move_id = fields.Many2one(
        'account.move',
        string='Correcting Entry',
        readonly=True,
        copy=False,
        help='The journal entry created to reclassify this difference'
    )

    state = fields.Selection([
        ('pending', 'Pending'),
        ('classified', 'Classified'),
    ], string='Status', default='pending', readonly=True, tracking=True)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        readonly=True
    )

    notes = fields.Text('Notes', help='Optional notes about this cash difference')

    @api.model_create_multi
    def create(self, vals_list):
        """Generate reference sequence on create."""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'cash.difference.reconciliation'
                ) or 'CDR/0001'
        return super().create(vals_list)

    def action_detect_cash_differences(self):
        """
        Scan for unprocessed POS cash differences.
        Finds entries posted to loss/gain accounts from cash journals
        that haven't been reconciled yet.
        """
        # Find loss/gain accounts from cash journals
        cash_journals = self.env['account.journal'].search([
            ('type', '=', 'cash'),
            ('company_id', '=', self.env.company.id),
        ])

        if not cash_journals:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Configuration Required'),
                    'message': _('No cash journals found. Please configure a cash journal first.'),
                    'type': 'warning',
                    'sticky': True,
                }
            }

        loss_accounts = cash_journals.mapped('loss_account_id')
        profit_accounts = cash_journals.mapped('profit_account_id')
        target_accounts = loss_accounts | profit_accounts

        if not target_accounts:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Configuration Required'),
                    'message': _('No loss/profit accounts configured on cash journals. Please configure them first.'),
                    'type': 'warning',
                    'sticky': True,
                }
            }

        # Find already processed entries
        existing_move_line_ids = self.search([]).mapped('original_move_line_id').ids

        # Search for unprocessed cash difference entries
        move_lines = self.env['account.move.line'].search([
            ('account_id', 'in', target_accounts.ids),
            ('parent_state', '=', 'posted'),
            ('id', 'not in', existing_move_line_ids),
            '|',
            ('name', 'ilike', 'cash difference'),
            ('move_id.ref', 'ilike', 'cash difference'),
        ])

        if not move_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Scan Complete'),
                    'message': _('No new cash differences found. All entries are up to date.'),
                    'type': 'info',
                    'sticky': False,
                    'next': {'type': 'ir.actions.client', 'tag': 'reload'},
                }
            }

        # Create reconciliation records for found entries
        created_records = self.env['cash.difference.reconciliation']
        total_loss = 0.0
        total_gain = 0.0
        loss_count = 0
        gain_count = 0

        for line in move_lines:
            # Determine if it's a loss or gain based on debit/credit
            # Loss: money is missing, posted as debit to loss account
            # Gain: extra money, posted as credit to gain account
            if line.debit > 0:
                diff_type = 'loss'
                amount = line.debit
                total_loss += amount
                loss_count += 1
            else:
                diff_type = 'gain'
                amount = line.credit
                total_gain += amount
                gain_count += 1

            vals = {
                'original_move_id': line.move_id.id,
                'original_move_line_id': line.id,
                'date': line.date,
                'amount': amount,
                'currency_id': line.currency_id.id or line.company_currency_id.id,
                'original_account_id': line.account_id.id,
                'difference_type': diff_type,
                'company_id': line.company_id.id,
            }
            created_records |= self.create(vals)

        # Build detailed message
        currency = self.env.company.currency_id
        message_parts = []
        if loss_count:
            message_parts.append(_('%d loss(es) totaling %s') % (loss_count, currency.format(total_loss)))
        if gain_count:
            message_parts.append(_('%d gain(s) totaling %s') % (gain_count, currency.format(total_gain)))

        message = _('Found: %s. Ready for classification.') % ', '.join(message_parts)

        # Show notification and reload the view
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Scan Complete'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            }
        }

    def action_classify(self):
        """
        Create correcting journal entry to reclassify the cash difference
        to the selected expense category.
        """
        self.ensure_one()

        if self.state == 'classified':
            raise UserError(_('This cash difference has already been classified.'))

        if not self.category_id:
            raise UserError(_('Please select an expense category before classifying.'))

        expense_account = self.category_id.account_id
        if not expense_account:
            raise UserError(_(
                'The selected category "%s" does not have an expense account configured.'
            ) % self.category_id.name)

        # Get the journal from the original entry
        journal = self.original_move_id.journal_id

        # Prepare the correcting entry
        # For LOSS: Debit expense account, Credit loss account
        # For GAIN: Debit gain account, Credit expense account (or income)
        if self.difference_type == 'loss':
            debit_account = expense_account
            credit_account = self.original_account_id
            description = _('Reclassify cash loss: %s') % self.category_id.name
        else:
            debit_account = self.original_account_id
            credit_account = expense_account
            description = _('Reclassify cash gain: %s') % self.category_id.name

        move_vals = {
            'move_type': 'entry',
            'date': fields.Date.today(),
            'ref': _('Reclassification of %s') % self.name,
            'journal_id': journal.id,
            'company_id': self.company_id.id,
            'line_ids': [
                (0, 0, {
                    'name': description,
                    'account_id': debit_account.id,
                    'debit': self.amount,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'name': description,
                    'account_id': credit_account.id,
                    'debit': 0.0,
                    'credit': self.amount,
                }),
            ],
        }

        # Create and post the correcting entry
        move = self.env['account.move'].create(move_vals)
        move.action_post()

        # Update the reconciliation record
        self.write({
            'correcting_move_id': move.id,
            'state': 'classified',
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Classified'),
                'message': _('Cash difference successfully reclassified to "%s".') % self.category_id.name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            }
        }

    def action_view_original_move(self):
        """Open the original journal entry."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Original Entry'),
            'res_model': 'account.move',
            'res_id': self.original_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_correcting_move(self):
        """Open the correcting journal entry."""
        self.ensure_one()
        if not self.correcting_move_id:
            raise UserError(_('No correcting entry has been created yet.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Correcting Entry'),
            'res_model': 'account.move',
            'res_id': self.correcting_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

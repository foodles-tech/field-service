# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    fsm_order_ids = fields.Many2many(
        'fsm.order', 'fsm_order_line_invoice_rel',
        'invoice_id', 'fsm_order_id', string='FSM Orders')

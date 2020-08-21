# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMOrder(models.Model):
    _inherit = 'fsm.order'

    contract_line_id = fields.Many2one(
        comodel_name="contract.line",
        inverse_name="fsm_order_id",
        readonly=True,
        copy=False,
    )

    contract_id = fields.Many2one(
        related="contract_line_id.contract_id",
        readonly=True,
    )

    invoice_lines = fields.Many2many(
        # we need to link an invoice line, not only an invoice
        'account.invoice.line', 'fsm_order_line_invoice_rel',
        'order_line_id', 'invoice_line_id', string='Invoice Lines', copy=False)

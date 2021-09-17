# Copyright (C) 2020 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    fsm_frequency_set_id = fields.Many2one(
        "fsm.frequency.set",
        "Frequency SET",
        index=True,
        help="Frequency of the service",
        domain=[("is_abstract", "=", True)],
    )

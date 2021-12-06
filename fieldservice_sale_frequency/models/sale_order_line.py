# Copyright (C) 2021 Akretion (http:\/\/www.akretion.com)
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
    fsm_order_type_id = fields.Many2one("fsm.order.type", string="Fsm order Type")

    def _field_create_fsm_order_prepare_values(self):
        self.ensure_one()
        vals = super()._field_create_fsm_order_prepare_values()
        if self.fsm_order_type_id:
            vals["type"] = self.fsm_order_type_id.id
        return vals

    def _field_create_fsm_recurring_prepare_values(self):
        self.ensure_one()
        vals = super()._field_create_fsm_recurring_prepare_values()
        if self.fsm_order_type_id:
            vals["fsm_order_type_id"] = self.fsm_order_type_id.id
        return vals

    def _field_service_generation(self):
        """For service lines, create the field service order or requiring order
        depending on  fsm_frequency_set_id. If it already
        exists, it simply links the existing one to the line.
        """
        result = super()._field_service_generation()
        import ipdb

        ipdb.set_trace()
        for so_line in self.filtered(
            lambda sol: sol.product_id.field_service_tracking
            == "based_on_sale_line_frequency"
        ):
            if so_line.fsm_frequency_set_id:
                so_line._field_find_fsm_recurring()
            else:
                so_line._field_find_fsm_order()
        return result

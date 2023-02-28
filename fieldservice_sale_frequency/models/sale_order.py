# Copyright (C) 2020 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        """On SO confirmation, some lines generate field service recurrings."""
        result = super(SaleOrder, self)._action_confirm()
        self.order_line.filtered(
            lambda l: l.product_id.field_service_tracking
            == "based_on_sale_line_frequency"
            and l.fsm_frequency_set_id
        )._field_create_fsm_recurring()
        return result

    def _field_service_generate(self):
        """
        For service lines, create the field service order for sale order
        if fsm_frequency_set_id is not set.
        """
        new_fsm_orders = super()._field_service_generate()

        new_fsm_based_on_sale_line_frequency_sol = self.order_line.filtered(
            lambda l: l.product_id.field_service_tracking
            == "based_on_sale_line_frequency"
            and not l.fsm_order_id
            and not l.fsm_frequency_set_id
        )

        new_fsm_orders |= self._field_service_generate_sale_fsm_orders(
            new_fsm_based_on_sale_line_frequency_sol
        )

        return new_fsm_orders

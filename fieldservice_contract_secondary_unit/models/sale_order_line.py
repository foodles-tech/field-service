# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    scheduled_duration = field.Float(
        compute="_compute_duration",
        readonly=True
    )

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        self.ensure_one()
        res = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id
        )
        res["secondary_uom_id"] = self.secondary_uom_id
        res["secondary_uom_qty"] = self.secondary_uom_qty
        return res

    def _field_create_fsm_order_prepare_values(self):
        self.ensure_one()
        vals = super()._field_create_fsm_order_prepare_values()
        duration = self.scheduled_duration
        if duration:
            vals["scheduled_duration"] = duration
        return vals

    def _compute_duration(self):
        uom_hour = self.env.ref('product_uom_hour')
        _convert_duration = self.env['sale.order.line']._convert_duration
        for rec in self:
            from_uom = rec.secondary_uom_id.uom_id
            quantity = rec.secondary_uom_qty
            rec = _convert_duration(uom_hour, quantity, uom_hour)

    def _convert_duration(self, from_uom, quantiy, uom_hour)
            uom_categ_wtime = uom_hour.category_id
            if from_uom == uom_categ_wtime:
                return from_uom._compute_quantity(quantity, to_unit=uom_hour)
            else:
                return False

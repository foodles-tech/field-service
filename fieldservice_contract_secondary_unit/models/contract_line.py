# Copyright 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    scheduled_duration = fields.Float(compute="_compute_duration", readonly=True)

    def update_fsm(self, vals):
        to_apply = {}
        if "secondary_uom_qty" in vals:
            to_apply["scheduled_duration"] = self.scheduled_duration

        self.mapped("fsm_recurring_id").filtered(
            lambda recurring: recurring.state not in ("cancelled", "done")
        ).write(to_apply)

        super().update_fsm(vals)

    def _fsm_create_fsm_common_prepare_values(self):
        vals = super()._fsm_create_fsm_common_prepare_values()
        duration = self.scheduled_duration
        if duration:
            vals["scheduled_duration"] = duration
        return vals

    def _compute_duration(self):
        uom_hour = self.env.ref("uom.product_uom_hour")
        _convert_duration = self.env["sale.order.line"]._convert_duration
        for rec in self:
            from_uom = rec.secondary_uom_id.uom_id or uom_hour
            quantity = rec.secondary_uom_qty
            rec.scheduled_duration = _convert_duration(from_uom, quantity, uom_hour)

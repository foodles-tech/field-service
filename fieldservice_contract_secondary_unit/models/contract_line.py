# Copyright 2019 Akretion <raphael.reverdy@akretion.com>
# Copyright 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class ContractLine(models.Model):
    _inherit = "contract.line"

    scheduled_duration = field.Float(
        compute="_compute_duration",
        readonly=True
    )

    def update_fsm(self, vals):
        to_apply = {}
        if "secondary_uom_qty" in vals:
            to_apply["scheduled_duration"] = vals["scheduled_duration"]

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
        uom_hour = self.env.ref('product_uom_hour')
        _convert_duration = self.env['sale.order.line']._convert_duration
        for rec in self:
            from_uom = rec.secondary_uom_id.uom_id
            quantity = rec.secondary_uom_qty
            rec = _convert_duration(uom_hour, quantity, uom_hour)
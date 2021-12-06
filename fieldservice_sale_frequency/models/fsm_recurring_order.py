# Copyright (C) 2021 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    fsm_order_type_id = fields.Many2one("fsm.order.type", string="Fsm order Type")

    def _prepare_order_values(self, date=None):
        self.ensure_one()
        vals = super()._prepare_order_values(date=date)
        if self.fsm_order_type_id:
            vals["type"] = self.fsm_order_type_id.id
        return vals

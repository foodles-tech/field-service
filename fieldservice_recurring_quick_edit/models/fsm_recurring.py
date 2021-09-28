# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    fsm_frequency_set_id = fields.Many2one(required=False)
    fsm_frequency_qedit_ids = fields.One2many(
        "fsm.frequency",
        "fsm_recurring_id",
        copy=False,
        domain="[('is_quick_editable','=', True)]",
        help="Technical fields used to allow a quick edit of fsm_frequency_ids",
    )
    fsm_abstract_frequency_set_id = fields.Many2one(
        "fsm.frequency.set",
        "Generic Frequency Set",
        index=True,
        copy=True,
        help="Frequency of the service",
        domain=[("is_abstract", "=", True)],
    )
    edit_type = fields.Selection(
        [("quick_edit", "Quick edit"), ("advanced", "Advanced edit"),],
        default="quick_edit",
    )
    fsm_frequency_ids = fields.One2many(
        "fsm.frequency",
        "fsm_recurring_id",
        # compute="_calc_fsm_frequency_ids",
        # inverse="_inverse_fsm_frequency_ids",
        string="Frequency Rules",
    )

    @api.onchange("fsm_abstract_frequency_set_id")
    def onchange_fsm_abstract_frequency_set_id(self):
        if not self.fsm_abstract_frequency_set_id:
            return
        frequencies = self.env["fsm.frequency"]
        freq_list = [(5, 0, 0)]
        for freq in self.fsm_abstract_frequency_set_id.fsm_frequency_ids:
            copied_vals = freq.copy_data()[0]
            # copied_vals['fsm_recurring_id'] = self.id
            copied_vals["origin"] = self.fsm_abstract_frequency_set_id.name
            freq_list.append((0, 0, copied_vals))
            # frequencies |= frequencies.new(copied_vals)
        if self.edit_type == "quick_edit":
            self.fsm_frequency_qedit_ids = freq_list
        else:
            self.fsm_frequency_ids = freq_list

    def _inverse_fsm_frequency_ids(self):
        for rec in self:
            rec.fsm_frequency_set_id.fsm_frequency_ids = rec.fsm_frequency_ids

    @api.depends("fsm_frequency_set_id.fsm_frequency_ids")
    def _calc_fsm_frequency_ids(self):
        for rec in self:
            rec.fsm_frequency_ids = rec.fsm_frequency_set_id.fsm_frequency_ids

    def action_view_fms_order(self):
        # TODO: move this in parent
        fms_orders = self.mapped("fsm_order_ids")
        action = self.env.ref("fieldservice.action_fsm_operation_order").read()[0]
        if len(fms_orders) > 1:
            action["domain"] = [("id", "in", fms_orders.ids)]
        elif len(fms_orders) == 1:
            form_view = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = fms_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        action["key2"] = "client_action_multi"
        return action

    def generate_orders(self):
        """
        Executed from form view (call private method) _generate_orders
        """
        return self._generate_orders()

    @api.model
    def create(self, values):
        recurring = super().create(values)
        if not recurring.fsm_frequency_set_id:
            recurring.fsm_frequency_set_id = recurring.fsm_frequency_set_id.create(
                {"name": recurring.name, "is_quick_edit": True,}
            )
            recurring.fsm_frequency_set_id.fsm_frequency_ids = (
                recurring.fsm_frequency_ids
            )
        return recurring

    def write(self, values):
        result = super().write(values)
        for recurring in self:
            if not recurring.fsm_frequency_set_id:
                recurring.fsm_frequency_set_id = recurring.fsm_frequency_set_id.create(
                    {"name": recurring.name, "is_quick_edit": True,}
                )
                recurring.fsm_frequency_set_id.fsm_frequency_ids = (
                    recurring.fsm_frequency_ids
                )
            else:
                recurring.fsm_frequency_set_id.fsm_frequency_ids = (
                    recurring.fsm_frequency_ids
                )
        return result

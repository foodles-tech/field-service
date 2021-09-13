# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"

    fsm_frequency_set_id = fields.Many2one(required=False)
    fsm_frequency_qedit_ids = fields.One2many(
        "fsm.frequency", "fsm_recurring_id",
        copy=False,
        domain="[('is_quick_editable','=', True)]",
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
        frequencys = self.env["fsm.frequency"]
        for freq in self.fsm_abstract_frequency_set_id.fsm_frequency_ids:
            frequencys |= freq.copy()
        self.fsm_frequency_ids = frequencys

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
        return result

    def generate_5w(self):
        if self.start_date:
            planned_hour = self.start_date.hour + self.start_date.minute / 60
        else:
            planned_hour = False

        base = {
            "name": "5w",
            "interval_type": "weekly",
            "use_byweekday": True,
            "use_planned_hour": True,
            "interval_frequency": "6",  # each
            "is_quick_edit": True,
            "planned_hour": planned_hour,
        }

        days = [
            {"mo": True, "name": "Monday %s" % self.name},
            {"tu": True, "name": "Tuesday %s" % self.name},
            {"we": True, "name": "Wednesday %s" % self.name},
            {"th": True, "name": "Thuesday %s" % self.name},
            {"fr": True, "name": "Friday %s" % self.name},
            {"sa": True, "name": "Saturday %s" % self.name},
            {"su": True, "name": "Sunday %s" % self.name},
        ]
        # base | day is python3.9
        fsm = [{**base, **day} for day in days]
        if not self.frequency_type == "edit_inplace":
            return "Not Quickedit"  # TODO do it better

        if not self.fsm_frequency_set_id:
            self.fsm_frequency_set_id = self.fsm_frequency_set_id.create(
                {"name": self.name, "is_quick_edit": True,}
            )

        freqs = self.env["fsm.frequency"].create(fsm)
        previous = self.fsm_frequency_set_id.fsm_frequency_ids
        self.fsm_frequency_set_id.fsm_frequency_ids = [(6, 0, freqs.ids)]
        previous.unlink()
        self.fsm_frequency_set_id = self.fsm_frequency_set_id
        return

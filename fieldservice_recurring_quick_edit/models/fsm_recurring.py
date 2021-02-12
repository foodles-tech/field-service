# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"
    #_inherits = {"fsm.frequency.set": "fsm_frequency_set_qedit_id"}

    #name = fields.Char(
    #    related="fsm_frequency_set_qedit_id.name", inherited=True, readonly=False
    #)
    fsm_frequency_set_id = fields.Many2one(
        required=False)
    fsm_frequency_set_qedit_id = fields.Many2one(
        "fsm.frequency.set",
        ondelete="restrict",
        string="Quick Edit Frequency Set",
        help="Quick Edit Frequency Set-related " "data to the user Recurring Order",
    )
    frequency_type = fields.Selection(
        [
            ("use_predefined", "Use predifined frequency"),
            ("edit_inplace", "Quick edit"),
        ],
        default="use_predefined",
    )
    fsm_frequency_qedit_ids = fields.Many2many(
        "fsm.frequency",
    #     related="fsm_frequency_set_qedit_id.fsm_frequency_ids",
 #       readonly=True,
        compute="_calc_fsm_frequency_qedit_ids",
        inverse="_inv_fsm_frequency_qedit_ids",
        string="Frequency Rules",
    )

    def _inv_fsm_frequency_qedit_ids(self):
        # TODO: allow to edit
        pass
    
    @api.depends('fsm_frequency_set_qedit_id.fsm_frequency_ids')
    def _calc_fsm_frequency_qedit_ids(self):
        for rec in self:
            rec.fsm_frequency_qedit_ids = rec.fsm_frequency_set_qedit_id.fsm_frequency_ids


    # def init(self):
    # TODO move this to migration script ?
    #     # set all existing unset fsm_frequency_set_qedit_id fields to ``true``
    #     self._cr.execute(
    #         "UPDATE fsm_recurring"
    #         " SET fsm_frequency_set_qedit_id = fsm_frequency_set_id"
    #         " WHERE fsm_frequency_set_qedit_id IS NULL"
    #     )
    #     self._cr.execute(
    #         "UPDATE fsm_recurring"
    #         " SET frequency_type = 'use_predefined'"
    #         " WHERE frequency_type IS NULL"
    #     )


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

    def generate_5w(self):
        base = {
            "name": "5w",
            "interval_type": "weekly",
            "use_byweekday": True,
            "use_planned_hour": True,
            "interval_frequency": "6",  # each
            "is_quick_edit": True,
        }

        days = [
            { "mo": True, "name": "Monday %s" % self.name },
            { "tu": True, "name": "Tuesday %s" % self.name },
            { "we": True, "name": "Wednesday %s" % self.name },
            { "th": True, "name": "Thuesday %s" % self.name },
            { "fr": True, "name": "Friday %s" % self.name },
            { "sa": True, "name": "Saturday %s" % self.name },
            { "su": True, "name": "Sunday %s" % self.name },
        ]
        # base | day is python3.9
        fsm = [ {**base, **day} for day in days]
        if not self.frequency_type == "edit_inplace":
            return "Not Quickedit" # TODO do it better

        if not self.fsm_frequency_set_qedit_id:
            self.fsm_frequency_set_qedit_id = self.fsm_frequency_set_qedit_id.create(
                {
                    "name": self.name,
                    "is_quick_edit": True,
                }
            )

        freqs = self.env['fsm.frequency'].create(fsm)
        previous = self.fsm_frequency_set_qedit_id.fsm_frequency_ids
        self.fsm_frequency_set_qedit_id.fsm_frequency_ids = [(6, 0, freqs.ids) ]
        previous.unlink()
        self.fsm_frequency_set_id = self.fsm_frequency_set_qedit_id
        return

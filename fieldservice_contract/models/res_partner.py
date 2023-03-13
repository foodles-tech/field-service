# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    contract_line_count = fields.Integer(
        string="Contract lines count", compute="_compute_contract_line_count"
    )

    def _get_contract_line_count(self, partner):
        child_partner_list = self.env["res.partner"].search(
            [("parent_id", "=", partner.id)]
        )
        orders = self.env["contract.line"].search_count(
            [
                "&",
                ("contract_id.partner_id", "=", partner.id),
                "&",
                ("active", "=", True),
                (
                    "date_start",
                    "<=",
                    (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                ),
                "|",
                ("date_end", ">=", datetime.now().strftime("%Y-%m-%d")),
                ("date_end", "=", False),
            ]
        )

        if child_partner_list:
            for child_partner in child_partner_list:
                orders += self._get_contract_line_count(child_partner)

        return orders

    def _compute_contract_line_count(self):
        for partner in self:
            partner.contract_line_count = self._get_contract_line_count(partner)

    def _get_contract_lines(self, partner):
        child_partner_list = self.env["res.partner"].search(
            [("parent_id", "=", partner.id)]
        )
        orders = self.env["contract.line"].search(
            [("contract_id.partner_id", "=", partner.id)]
        )

        if child_partner_list:
            for child_partner in child_partner_list:
                orders += self._get_contract_lines(child_partner)

        return orders

    def action_view_contract_list(self):
        """
        This function returns an action that display existing order lines
        of given fsm location id and its child locations. It can
        either be a in a list or in a form view, if there is only one
        contact to show.
        """
        for partner in self:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "fieldservice_contract.action_contextual_contract_lines"
            )
            contract_list = self._get_contract_lines(partner)
            action["context"] = self.env.context.copy()
            action["context"].update({"group_by": ""})
            action["context"].update({"search_default_in_progress": True})
            if len(contract_list) == 0 or len(contract_list) > 1:
                action["domain"] = [("id", "in", contract_list.ids)]
            elif contract_list:
                action["views"] = [
                    (
                        self.env.ref(
                            "fieldservice_contract." + "contract_line_form_view"
                        ).id,
                        "form",
                    )
                ]
                action["res_id"] = contract_list.id
            return action

# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FSMLocation(models.Model):
    _inherit = "fsm.location"

    contract_line_count = fields.Integer(
        string="Contract lines count", compute="_compute_contract_line_count"
    )

    def _get_contract_line_count(self, loc):
        child_loc_list = self.env["fsm.location"].search(
            [("fsm_parent_id", "=", loc.id)]
        )
        orders = self.env["contract.line"].search_count([("fsm_location_id", "=", loc.id)])

        if child_loc_list:
            for child_loc in child_loc_list:
                orders += self._get_contract_line_count(child_loc)

        return orders

    def _compute_contract_line_count(self):
        for loc in self:
            loc.contract_line_count = self._get_contract_line_count(loc)

    def _get_contract_lines(self, loc):
        child_loc_list = self.env["fsm.location"].search(
            [("fsm_parent_id", "=", loc.id)]
        )
        orders = self.env["contract.line"].search([("fsm_location_id", "=", loc.id)])

        if child_loc_list:
            for child_loc in child_loc_list:
                orders += self._get_contract_lines(child_loc)

        return orders

    def action_view_contract_list(self):
        """
        This function returns an action that display existing order lines
        of given fsm location id and its child locations. It can
        either be a in a list or in a form view, if there is only one
        contact to show.
        """
        for location in self:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "fieldservice_contract.action_location_contract_lines"
            )
            contract_list = self._get_contract_lines(location)
            action["context"] = self.env.context.copy()
            action["context"].update({"group_by": ""})
            action["context"].update({"default_service_location_id": self.id})
            if len(contract_list) == 0 or len(contract_list) > 1:
                action["domain"] = [("id", "in", contract_list.ids)]
            elif contract_list:
                action["views"] = [
                    (self.env.ref("fieldservice_contract." + "contract_line_form_view").id, "form")
                ]
                action["res_id"] = contract_list.id
            return action

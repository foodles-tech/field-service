# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    type = fields.Selection(selection_add=[("fsm_location", "Location")])
    fsm_location = fields.Boolean("Is a FS Location")
    fsm_person = fields.Boolean("Is a FS Worker")
    fsm_location_id = fields.One2many(
        comodel_name="fsm.location",
        string="Related FS Location",
        inverse_name="partner_id",
        readonly=1,
    )
    service_location_id = fields.Many2one(
        "fsm.location", string="Primary Service Location"
    )
    owned_location_ids = fields.One2many(
        "fsm.location",
        "owner_id",
        string="Owned Locations",
        domain=[("fsm_parent_id", "=", False)],
    )
    owned_location_count = fields.Integer(
        compute="_compute_owned_location_count", string="# of Owned Locations"
    )

    contract_line_count = fields.Integer(
        string="Contract lines count", compute="_compute_contract_line_count"
    )

    def _get_contract_lines(self, partner):
        child_partner_list = self.env["res.partner"].search(
            [("parent_id", "=", partner.id)]
        )
        orders = self.env["fsm.order"].search(
            [("location_id.owner_id", "=", partner.id)]
        )

        if child_partner_list:
            for child_partner in child_partner_list:
                orders += self._get_contract_lines(child_partner)

        return orders

    def _get_contract_line_count(self, partner):
        child_partner_list = self.env["res.partner"].search(
            [("parent_id", "=", partner.id)]
        )
        orders = self.env["fsm.order"].search_count(
            [("location_id.owner_id", "=", partner.id)]
        )

        if child_partner_list:
            for child_partner in child_partner_list:
                orders += self._get_contract_line_count(child_partner)

        return orders

    def action_view_contract_list(self):
        """
        This function returns an action that display existing order lines
        of given fsm partner id and its child partner. It can
        either be a in a list or in a form view, if there is only one
        contact to show.
        """
        for location in self:
            action = self.env["ir.actions.act_window"]._for_xml_id(
                "fieldservice.action_fsm_operation_order"
            )
            contract_list = self._get_contract_lines(location)
            action["context"] = self.env.context.copy()
            action["context"].update({"group_by": ""})
            if len(contract_list) == 0 or len(contract_list) > 1:
                action["domain"] = [("id", "in", contract_list.ids)]
            elif contract_list:
                action["views"] = [
                    (self.env.ref("fieldservice." + "fsm_order_form").id, "form")
                ]
                action["res_id"] = contract_list.id
            return action

    def _compute_contract_line_count(self):
        for partner in self:
            partner.contract_line_count = self._get_contract_line_count(partner);

    def _compute_owned_location_count(self):
        for partner in self:
            res = self.env["fsm.location"].search_count(
                [("owner_id", "child_of", partner.id)]
            )
            partner.owned_location_count = res

    def action_open_owned_locations(self):
        for partner in self:
            owned_location_ids = self.env["fsm.location"].search(
                [("owner_id", "child_of", partner.id)]
            )
            action = self.env["ir.actions.actions"]._for_xml_id(
                "fieldservice.action_fsm_location"
            )
            action["context"] = {}
            if len(owned_location_ids) > 1:
                action["domain"] = [("id", "in", owned_location_ids.ids)]
            elif len(owned_location_ids) == 1:
                action["views"] = [
                    (self.env.ref("fieldservice.fsm_location_form_view").id, "form")
                ]
                action["res_id"] = owned_location_ids.ids[0]
            return action

    def _convert_fsm_location(self):
        wiz = self.env["fsm.wizard"]
        partners_with_loc_ids = (
            self.env["fsm.location"]
            .sudo()
            .search([("active", "in", [False, True]), ("partner_id", "in", self.ids)])
            .mapped("partner_id")
        ).ids

        partners_to_convert = self.filtered(
            lambda p: p.type == "fsm_location" and p.id not in partners_with_loc_ids
        )
        for partner_to_convert in partners_to_convert:
            wiz.action_convert_location(partner_to_convert)

    def write(self, value):
        res = super(ResPartner, self).write(value)
        self._convert_fsm_location()
        return res

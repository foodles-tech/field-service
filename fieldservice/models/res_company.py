# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    stage_management = fields.Boolean(
        string="Do not allow stages management", store=True, default=True
    )
    no_child_equipment = fields.Boolean(
        string="Equipment can't have children", store=True
    )
    no_territory_management = fields.Boolean(
        string="Users do not manage territory", store=True
    )
    auto_populate_persons_on_location = fields.Boolean(
        string="Auto-populate Workers on Location based on Territory"
    )
    auto_populate_equipments_on_order = fields.Boolean(
        string="Auto-populate Equipments on Order based on Location"
    )
    search_on_complete_name = fields.Boolean(string="Search Location By Hierarchy")

# Copyright (C) 2023 Syera BONNEAUX
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    default_resupply_warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Default resupply warehouse ",
        compute="_compute_warehouse_id",
    )

    @api.depends("current_location_id")
    def _compute_warehouse_id(self):
        for rec in self:
            rec.default_resupply_warehouse_id = (
                rec.current_location_id.partner_id._get_warehouse()
            )

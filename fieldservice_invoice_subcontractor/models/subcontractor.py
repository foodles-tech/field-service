# Copyright (C) 2022 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ResSubcontractor(models.Model):
    _name = "res.subcontractor"
    _description = "Subcontractor"
    _order = "subcontractor_partner_id asc"

    @api.model
    def _get_subcontractor_type(self):
        return [
            ("internal", "Internal Subcontractor"),
            ("external", "External Subcontractor"),
        ]

    # name = fields.Char("Name", required=True)
    display_name = fields.Char(compute="_compute_display_name")

    subcontractor_company_id = fields.Many2one(
        "res.company", string="Subcontractor Company"
    )
    subcontractor_partner_id = fields.Many2one(
        "res.partner", string="Partner to invoice"
    )
    subcontractor_type = fields.Selection(
        string="Subcontractor Type",
        selection="_get_subcontractor_type",
        required=True,
        default="internal",
    )
    commission_rate = fields.Float(
        help="Rate in % for the commission on subcontractor work", default=10.00
    )

    @api.onchange("subcontractor_company_id")
    def _onchange_subcontractor_company_id(self):
        if self.subcontractor_company_id:
            self.subcontractor_partner_id = self.subcontractor_company_id.partner_id

    @api.depends("subcontractor_partner_id", "subcontractor_type")
    def _compute_display_name(self):
        type_name_mapping = {
            k: v
            for k, v in self._fields["subcontractor_type"]._description_selection(
                self.env
            )
        }
        for record in self:
            name = type_name_mapping[record.subcontractor_type]
            record.display_name = ("%s - (%s)") % (
                record.subcontractor_partner_id.name,
                name,
            )

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, rec.display_name))
        return res

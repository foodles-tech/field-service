# Copyright (C) 2021 Mourad EL HADJ MIMOUNE Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    field_service_tracking = fields.Selection(
        selection_add=[
            (
                "based_on_sale_line_frequency",
                "Create a recurring order if Frequency is set on sale line."
                " Otherwise create an order",
            )
        ]
    )

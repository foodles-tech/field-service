# Copyright (C) 2021 <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    subcontractor_id = fields.Many2one(
        "res.subcontractor",
        string="Work for",
        help="This field is used to invoice subcontracted field service orders",
    )

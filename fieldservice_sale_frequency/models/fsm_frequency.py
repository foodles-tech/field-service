# Copyright (C) 2022 Akretion (https://www.akretion.com)
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMFrequency(models.Model):
    _inherit = "fsm.frequency"

    is_abstract = fields.Boolean()

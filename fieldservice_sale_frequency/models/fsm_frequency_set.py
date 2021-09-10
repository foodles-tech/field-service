# Copyright (C) 2020 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class FSMFrequencySet(models.Model):
    _inherit = "fsm.frequency.set"

    is_abstract = fields.Boolean(oldname="is_abstract")
    # todo: rename it like


# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import rrule

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class FSMFrequencySet(models.Model):
    _inherit = "fsm.frequency.set"

    quick_edit_fsm_recurring_id = fields.One2many(
        comodel_name="fsm.recurring",
        inverse_name="fsm_frequency_set_qedit_id",
        readonly=True,
    )
    # TODO add a constraint to have only
    # on quickedit per fsm_recurring_id

    # quick_edit_fsm_frequency_ids = fields.One2many(
    #     comodel_name="fsm.frequency",
    #     inverse_name="",
    #     domain="[('is_quick_edit','=', is_quick_edit)]",
    #     readonly=True,
    #   ajouter on ondelete
    # )

    is_quick_edit = fields.Boolean(default=False, readonly=True)
    fsm_frequency_ids = fields.Many2many(
        # limit available frequency in the view
        # take care to add is_quick_edit the views
        domain="[('is_quick_edit','=', is_quick_edit)]",
    )

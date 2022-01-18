# Copyright (C) 2020 Akretion (https://www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMFrequencySet(models.Model):
    _inherit = "fsm.frequency.set"

    is_abstract = fields.Boolean()

    fsm_frequency_ids = fields.Many2many(
        comodel_name="fsm.frequency",
        compute='_compute_fsm_frequency_ids',
        inverse='_inverse_fsm_frequency_ids',
    )

    fsm_abstract_frequency_ids = fields.Many2many(
        comodel_name='fsm.frequency',
        relation='fsm_abstract_set_freq',
        domain="[('is_abstract', '=', True)]",
    )
    fsm_concrete_frequency_ids = fields.Many2many(
        comodel_name='fsm.frequency',
        relation='fsm_concrete_set_freq',
        domain="[('is_abstract', '=', False)]",
    )


    @api.depends('is_abstract', 'fsm_concrete_frequency_ids', 'fsm_abstract_frequency_ids')
    def _compute_fsm_frequency_ids(self):
        for rec in self:
            if rec.is_abstract:
                rec.fsm_frequency_ids = rec.fsm_abstract_frequency_ids
            else:
                rec.fsm_frequency_ids = rec.fsm_concrete_frequency_ids

    def _inverse_fsm_frequency_ids(self):
        for rec in self:
            if rec.is_abstract:
                rec.fsm_abstract_frequency_ids = rec.fsm_frequency_ids
            else:
                rec.fsm_concrete_frequency_ids = rec.fsm_frequency_ids

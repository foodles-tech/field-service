# Copyright (C) 2020 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _field_create_fsm_recurring_prepare_values(self):
        self.ensure_one()
        values = super()._field_create_fsm_recurring_prepare_values()
        values["fsm_abstract_frequency_set_id"] = self.fsm_frequency_set_id.id
        return values

    def _field_create_fsm_recurring(self):
        result = super()._field_create_fsm_recurring()
        for line in self:
            if line.fsm_frequency_set_id.fsm_frequency_ids:
                recurring= result[line.id]
                frequencies = self.env["fsm.frequency"]
                for freq in line.fsm_frequency_set_id.fsm_frequency_ids:
                    frequencies |= freq.copy({"fsm_recurring_id": recurring.id,
                        "origin": line.fsm_frequency_set_id.name})
                recurring.fsm_frequency_ids= frequencies
        return result

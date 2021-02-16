# Copyright (C) 2021 <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class FSMPerson(models.Model):
    _inherit = "fsm.person"

    employee_id = fields.Many2one(
        "hr.employee",
        string="Related Employee",
        ondelete="restrict",
    )
    calendar_id = fields.Many2one("resource.calendar", string="Working Schedule")

    @api.onchange("employee_id")
    def onchange_employee_id(self):
        if self.employee_id and not self.calendar_id:
            self.calendar_id = self.employee_id.resource_calendar_id

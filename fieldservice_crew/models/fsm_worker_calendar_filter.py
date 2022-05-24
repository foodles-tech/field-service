# Copyright (C) 2022 Raphaël Reverdy
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FSMWorkerCalendarFilter(models.Model):
    """Assigned Worker Calendar Filter"""

    _name = "fsm.worker.calendar.filter"
    _description = "FSM Worker Calendar Filter"

    user_id = fields.Many2one(
        "res.users", "Me", required=True, default=lambda self: self.env.user
    )
    fsm_worker_id = fields.Many2one("hr.employee", "Employee", required=True)
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        (
            "user_id_fsm_worker_id_unique",
            "UNIQUE(user_id,fsm_worker_id)",
            "You cannot have the same worker twice.",
        )
    ]

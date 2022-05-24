# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    crew_member_ids = fields.One2many(
        "fsm.order.member",
        "fsm_order_id",
        string="Members",
    )

    crew_worker_ids = fields.Many2many(
        "hr.employee",
        relation="fsm_order_roster",
        compute="_compute_crew_worker_ids",
        inverse="_inverse_crew_worker_ids",
        store=True,
    )

    crew_total_duration = fields.Float(compute="_compute_crew_total_duration")

    @api.depends("crew_member_ids.scheduled_duration")
    def _compute_crew_total_duration(self):
        for rec in self:
            rec.crew_total_duration = sum(
                rec.crew_member_ids.mapped("scheduled_duration")
            )

    @api.depends("crew_member_ids", "crew_member_ids.fsm_worker_id")
    def _compute_crew_worker_ids(self):
        for rec in self:
            rec.crew_worker_ids = rec.crew_member_ids.mapped("fsm_worker_id")

    def _inverse_crew_worker_ids(self):
        for rec in self:
            to_add = rec.crew_worker_ids - rec.crew_member_ids.mapped("fsm_worker_id")
            to_rm = rec.crew_member_ids.mapped("fsm_worker_id") - rec.crew_worker_ids

            for worker in to_add:
                self.env["fsm.order.member"].create(
                    {
                        "fsm_order_id": rec.id,
                        "fsm_worker_id": worker.id,
                    }
                )
            rec.crew_member_ids.filtered(
                lambda w: w.fsm_worker_id.id in to_rm.ids
            ).unlink()


class FSMCrewMember(models.Model):
    _name = "fsm.order.member"
    _description = "FSM Order Member"
    _order = "fsm_order_id, sequence, id"
    _sql_constraints = [
        (
            "fsm_order_member_unicity",
            "unique (fsm_order_id, fsm_worker_id)",
            "Worker already on order",
        ),
    ]

    sequence = fields.Integer(string="Sequence", default=10)
    fsm_order_id = fields.Many2one(
        "fsm.order",
        string="Order Reference",
        required=True,
        ondelete="cascade",
        index=True,
        copy=False,
    )
    scheduled_date_start = fields.Datetime(
        string="Scheduled Start (ETA)", related="fsm_order_id.scheduled_date_start"
    )
    scheduled_duration = fields.Float(
        string="Scheduled duration",
        related="fsm_order_id.scheduled_duration",
        help="Scheduled duration of the work in" " hours",
    )
    scheduled_date_end = fields.Datetime(
        string="Scheduled End",
        related="fsm_order_id.scheduled_date_end",
    )

    fsm_worker_id = fields.Many2one("hr.employee", string="Worker", index=True)

    # add validation with calendar here

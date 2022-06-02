from odoo import fields, models


class Meeting(models.Model):
    _inherit = "calendar.event"

    def _update_fsm_assigned(self):
        self.ensure_one()
        if self._context.get("recurse_order_calendar"):
            # avoid recursion
            return
        super()._update_fsm_assigned()

        # Update crew worker_ids from the new partners
        hr_employee_ids = [
            partner.hr_employee_id.id
            for partner in self.partner_ids
            if partner.hr_employee_id
        ]

        self.fsm_order_id.with_context(recurse_order_calendar=True).write(
            {"crew_worker_ids": [(6, 0, hr_employee_ids)]}
        )

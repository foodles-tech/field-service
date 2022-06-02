from odoo import api, fields, models


class FSMOrder(models.Model):
    _inherit = "fsm.order"

    def _prepare_calendar_event(self):
        vals = super()._prepare_calendar_event()
        if self.crew_member_ids:
            for crew_member in self.crew_member_ids:
                hr_employee = crew_member.fsm_worker_id
                # If the employee still don't have an associated partner,
                # create one
                partner = (
                    hr_employee.partner_id or hr_employee._create_associated_employee()
                )

                vals["partner_ids"] += [(4, partner.id, False)]

        return vals

    def write(self, vals):
        old_partners = {}
        for rec in self:
            old_partners[rec.id] = rec.crew_worker_ids.mapped("partner_id")

        res = super().write(vals)

        if any(field in vals for field in ("crew_member_ids", "crew_worker_ids")):
            # We need to have a partner for all linked employees
            self.crew_worker_ids._create_all_associated_employees()

            self.filtered("calendar_event_id").update_calendar_crew(old_partners)
        return res

    def update_calendar_crew(self, old_partners):
        if self._context.get("recurse_order_calendar"):
            # avoid recursion
            return

        for rec in self:
            old_partner_ids = old_partners[rec.id]
            new_partner_ids = rec.crew_worker_ids.mapped("partner_id")

            calendar_event = rec.calendar_event_id.with_context(
                recurse_order_calendar=True
            )
            to_rm = old_partner_ids - new_partner_ids
            to_add = new_partner_ids - old_partner_ids
            calendar_event.partner_ids = calendar_event.partner_ids - to_rm + to_add

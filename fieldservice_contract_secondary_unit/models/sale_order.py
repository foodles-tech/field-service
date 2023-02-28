from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_line_fsm_values(self, line):
        values = super()._prepare_line_fsm_values(line)

        if line.scheduled_duration:
            values.update(
                {
                    "scheduled_duration": line.scheduled_duration,
                }
            )
        return values

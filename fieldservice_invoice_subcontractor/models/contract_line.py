# © 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ContractLine(models.Model):
    _inherit = "contract.line"

    def _prepare_invoice_line(self, move_form):
        res = super(ContractLine, self)._prepare_invoice_line(move_form)
        if "fsm_order_ids" in res:
            order_ids = res["fsm_order_ids"][0][2]
            orders = self.env["fsm.order"].browse(order_ids)
            subcontracted_orders = orders.filtered(
                lambda o: o.person_id
                and o.person_id.subcontractor_id.subcontractor_company_id
                != self.contract_id.company_id
            )
            if subcontracted_orders:
                res["subcontracted"] = True
            subcontractors = subcontracted_orders.mapped("person_id.subcontractor_id")
            # in this module we don't manage multisubcontractor
            if len(subcontractors) == 1:
                res["subcontractor_id"] = subcontractors.id
        return res

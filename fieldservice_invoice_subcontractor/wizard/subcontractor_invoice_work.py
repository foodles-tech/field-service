# © 2015 Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.tools.translate import _


class SubcontractorInvoiceWork(models.TransientModel):
    _name = "subcontractor.invoice.work"
    _description = "subcontractor invoice work"

    def generate_invoice(self):
        move_obj = self.env["account.move"]
        move_ids = self._context.get("active_ids")
        moves = move_obj.browse(move_ids)
        invoices = moves.invoice_subcontractor_work()
        return {
            "name": _("Customer Invoices"),
            "view_mode": "tree,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "nodestroy": True,
            "target": "current",
            "domain": "[('id','in', %s)]" % invoices.ids,
        }

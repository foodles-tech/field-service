# © 2022 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    subcontracted = fields.Boolean()
    subcontractor_id = fields.Many2one(
        "res.subcontractor",
        string="Subcontractor",
    )
    invalid_subcontractor_inf = fields.Boolean(
        compute="_compute_invalid_subcontractor_inf", store=True
    )
    origin_subcontracted_invoice_line_id = fields.Many2one(
        "account.move.line",
        string="Origin Subcontracted invoice line",
        readonly=True,
    )
    origin_subcontracted_invoice_id = fields.Many2one(
        "account.move",
        string="Origin Subcontracted Invoice",
        related="origin_subcontracted_invoice_line_id.move_id",
        store=True,
        index=True,
        readonly=True,
    )
    target_subcontracted_invoice_line_ids = fields.One2many(
        comodel_name="account.move.line",
        inverse_name="origin_subcontracted_invoice_line_id",
        string="Target Subcontracted invoice lines",
        readonly=True,
    )

    @api.depends("subcontracted", "subcontractor_id")
    def _compute_invalid_subcontractor_inf(self):
        for line in self:
            line.invalid_subcontractor_inf = False
            if (line.subcontracted and not line.subcontractor_id) or (
                not line.subcontracted and line.subcontractor_id
            ):
                line.invalid_subcontractor_inf = True

    @api.model
    def _prepare_subcontractor_invoice_line(self):
        self.ensure_one()
        self.env["account.move.line"]
        line_vals = {
            "product_id": self.sudo().product_id.id,
            "quantity": self.quantity,
            "name": "Client final {} :{}".format(self.partner_id.name, self.name),
            "price_unit": self.price_unit
            * (1 - self.subcontractor_id.commission_rate / 100.0),
            "origin_subcontracted_invoice_line_id": self.id,
            "product_uom_id": self.product_uom_id.id,
        }
        if hasattr(self.sudo(), "start_date") and hasattr(self.sudo(), "end_date"):
            line_vals.update(
                {
                    "start_date": self.sudo().start_date,
                    "end_date": self.sudo().end_date,
                }
            )
        # onchange_vals = invoice_line_obj.play_onchanges(line_vals, ["product_id"])
        # line_vals.update(onchange_vals)
        return line_vals


class AccountMove(models.Model):
    _inherit = "account.move"

    is_line_subcontracted = fields.Boolean(
        string="Subcontracted",
        compute="_compute_is_line_subcontracted",
        store=True,
        compute_sudo=True,
    )
    invalid_subcontractor_inf = fields.Boolean(
        compute="_compute_invalid_subcontractor_inf", store=True
    )
    target_subcontracted_invoice_ids = fields.One2many(
        "account.move",
        compute="_compute_target_subcontracted_invoice_bills_ids",
        string="Target Subcontracted Invoices",
        readonly=True,
    )
    target_subcontracted_invoice_count = fields.Integer(
        string="Target subcontracted invoice count",
        compute="_compute_target_subcontracted_invoice_bills_ids",
        readonly=True,
        store=True,
    )
    target_subcontracted_bill_ids = fields.One2many(
        "account.move",
        compute="_compute_target_subcontracted_invoice_bills_ids",
        string="Target Subcontracted Bills",
        readonly=True,
    )
    target_subcontracted_bill_count = fields.Integer(
        string="Target subcontracted Bills count",
        compute="_compute_target_subcontracted_invoice_bills_ids",
        readonly=True,
        store=True,
    )

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.target_subcontracted_invoice_line_ids",
    )
    def _compute_target_subcontracted_invoice_bills_ids(self):
        for inv in self:
            inv.target_subcontracted_invoice_ids = inv.invoice_line_ids.mapped(
                "target_subcontracted_invoice_line_ids.move_id"
            ).filtered(lambda i: i.move_type not in ("out_invoice", "out_refund"))
            inv.target_subcontracted_invoice_count = len(
                inv.target_subcontracted_invoice_ids
            )
            inv.target_subcontracted_bill_ids = inv.invoice_line_ids.mapped(
                "target_subcontracted_invoice_line_ids.move_id"
            ).filtered(lambda i: i.move_type not in ("in_invoice", "in_refund"))
            inv.target_subcontracted_bill_count = len(inv.target_subcontracted_bill_ids)

    def action_view_invoices(self):
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        invoices = self.mapped("target_subcontracted_invoice_ids")
        if len(invoices) > 1:
            action["domain"] = [("id", "in", invoices.ids)]
        elif invoices:
            action["views"] = [(self.env.ref("account.view_move_form").id, "form")]
            action["res_id"] = invoices.ids[0]
        return action

    def action_view_bills(self):
        action = self.env.ref("account.action_invoice_tree1").read()[0]
        vendor_bills = self.mapped("target_subcontracted_bills_ids")
        if len(vendor_bills) > 1:
            action["domain"] = [("id", "in", vendor_bills.ids)]
        elif vendor_bills:
            action["views"] = [(self.env.ref("account.invoice_form").id, "form")]
            action["res_id"] = vendor_bills.ids[0]
        return action

    def action_view_target_subcontracted_invoice(self):
        action = self.env.ref("purchase.purchase_order_action_generic").read()[0]
        purchases = self.mapped("purchase_ids")
        if len(purchases) > 1:
            action["domain"] = [("id", "in", purchases.ids)]
            action["views"] = [
                (self.env.ref("purchase.purchase_order_tree").id, "tree"),
                (self.env.ref("purchase.purchase_order_form").id, "form"),
            ]
        elif purchases:
            action["views"] = [
                (self.env.ref("purchase.purchase_order_form").id, "form")
            ]
            action["res_id"] = purchases.id
        return action

    @api.depends(
        "invoice_line_ids",
        "invoice_line_ids.subcontracted",
    )
    def _compute_is_line_subcontracted(self):
        for invoice in self:
            subcontracted_lines = invoice.invoice_line_ids.filtered(
                lambda line: line.subcontracted
            )
            if subcontracted_lines:
                invoice.is_line_subcontracted = True
            else:
                invoice.is_line_subcontracted = False

    @api.depends("invoice_line_ids", "invoice_line_ids.invalid_subcontractor_inf")
    def _compute_invalid_subcontractor_inf(self):
        for invoice in self:
            invalid_subcontracted_lines = invoice.invoice_line_ids.filtered(
                lambda line: line.invalid_subcontractor_inf
            )
            if invalid_subcontracted_lines:
                invoice.invalid_subcontractor_inf = True
            else:
                invoice.invalid_subcontractor_inf = False

    @api.model
    def _prepare_subcontractor_invoice(self):
        self.ensure_one()
        # the source invoice is always from customer, out_invoice or out_refund
        # but, depending on the subcontractor type, we want to create :
        # 1. For internal : the same type of invoice on the subcontractor company side
        # Then the supplier invoice/refund will be created with intercompant invoice
        # module.
        # 2. For external : directly create a supplier invoice/refund
        orig_invoice = self.sudo()

        subcontracted_line = self.invoice_line_ids.filtered(lambda l: l.subcontracted)
        subcontractors = subcontracted_line.mapped("subcontractor_id")
        invoice_vals_list = []
        for subcontractor in subcontractors:
            if subcontractor.subcontractor_type == "internal":
                invoice_type = orig_invoice.move_type
                journal_type = "sale"
                partner = self.company_id.partner_id
                company = subcontractor.subcontractor_company_id

            elif subcontractor.subcontractor_type == "external":
                invoice_type = (
                    orig_invoice.move_type == "out_invoice"
                    and "in_invoice"
                    or "in_refund"
                )
                journal_type = "purchase"
                partner = subcontractor.subcontractor_partner_id
                company = self.company_id

            if invoice_type in ["out_invoice", "out_refund"]:
                user = self.env["res.users"].search(
                    [("company_id", "=", company.id)], limit=1
                )
            elif invoice_type in ["in_invoice", "in_refund"]:
                user = self.env.user
            journal = (
                self.env["account.journal"]
                .sudo()
                .search(
                    [("company_id", "=", company.id), ("type", "=", journal_type)],
                    limit=1,
                )
            )
            if not journal:
                raise UserError(
                    _('Please define %s journal for this company: "%s" (id:%d).')
                    % (journal_type, company.name, company.id)
                )
            invoice_vals = {"partner_id": partner.id, "move_type": invoice_type}
            # invoice_vals = self.env["account.move"].play_onchanges(
            #     invoice_vals, ["partner_id"]
            # )
            original_invoice_date = orig_invoice.invoice_date
            last_invoices = self.env["account.move"].search(
                [
                    ("move_type", "=", invoice_type),
                    ("company_id", "=", company.id),
                    ("invoice_date", ">", original_invoice_date),
                    ("name", "!=", False),
                ],
                order="invoice_date desc",
            )
            if not last_invoices:
                invoice_date = original_invoice_date
            else:
                invoice_date = last_invoices[0].invoice_date
            sub_inv_lines = subcontracted_line.filtered(
                lambda l: l.subcontractor_id == subcontractor
            )
            line_vals_list = []
            for line in sub_inv_lines:
                line_vals = line._prepare_subcontractor_invoice_line()
                line_vals_list.append((0, 0, line_vals))

            invoice_vals.update(
                {
                    "invoice_date": invoice_date,
                    "partner_id": partner.id,
                    "journal_id": journal.id,
                    "invoice_line_ids": line_vals_list,
                    "currency_id": company.currency_id.id,
                    "user_id": user.id,
                    "company_id": company.id,
                }
            )
            invoice_vals_list.append(invoice_vals)
        return invoice_vals_list

    def invoice_subcontractor_work(self):
        # group subcontractor by invoice : internal sub should produce one invoice
        # per (employee/original_invoice_id) and external sub should produce one
        # invoice per employee
        subcontractor_invoices = self.env["account.move"]

        if self.filtered(lambda i: i.state in ("draft", "cancel")):
            raise UserError(_("You must chose only posted invoice"))
        if self.filtered(lambda i: i.move_type not in ("out_invoice", "out_refund")):
            raise UserError(
                _(
                    "You can only invoice the subcontractors on a customer invoice/refund"
                )
            )
        if self.filtered(lambda i: not i.is_line_subcontracted):
            raise UserError(_("Choice subcontracted invoice only"))
        if self.filtered(lambda i: i.invalid_subcontractor_inf):
            raise UserError(
                _(
                    "All subcontracted lines must have a subcontractor. Check subcontracted invoices not valid"
                )
            )
        invoice_obj = self.env["account.move"]

        for inv in self:
            invoice_vals_list = inv._prepare_subcontractor_invoice()
            for invoice_vals in invoice_vals_list:
                company = self.company_id.browse(invoice_vals["company_id"])
                invoice = invoice_obj.with_company(company).create(invoice_vals)
                subcontractor_invoices |= invoice
        return subcontractor_invoices

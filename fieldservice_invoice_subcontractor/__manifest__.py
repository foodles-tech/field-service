# © 2015 Akretion
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice Subcontractor",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Others",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "fieldservice_contract",
        "account",
        "onchange_helper",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/subcontractor_view.xml",
        "views/invoice_view.xml",
        "views/fsm_person.xml",
        "wizard/subcontractor_invoice_work_view.xml",
    ],
    "installable": True,
}

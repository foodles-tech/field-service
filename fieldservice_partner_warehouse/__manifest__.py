# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "fieldservice_equipment partner's warehouse",
    "summary": "Add automaticcaly the partner's warehouse on a fsm_equipment and a fsm_location",
    "version": "14.0.1.0.1",
    "category": "Field Service",
    "website": "https://github.com/OCA/field-service",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "auto_install": False,
    "depends": ["stock_partner_warehouse", "fieldservice"],
    "data": ["views/fsm_location.xml", "views/fsm_equipment.xml"],
}

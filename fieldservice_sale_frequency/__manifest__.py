# Copyright (C) 2020 Akretion (https://www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sales - Frequency Set",
    "version": "14.0.2.0.0",
    "summary": "Define frequencies with simple Frequency Set.",
    "category": "Field Service",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice_sale_recurring"],
    "data": ["views/fsm_frequency_set_view.xml", "views/sale_order_view.xml",],
    "license": "AGPL-3",
    "development_status": "Beta",
    "installable": True,
    "auto_install": True,
}

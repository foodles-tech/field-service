# Copyright (C) 2020 Akretion (http:\/\/www.akretion.com)
# @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service - Sales - Frequency Set",
    "version": "13.0.1.0.0",
    "summary": "Sell field services with simple Frequency Set.",
    "category": "Field Service",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": ["fieldservice_recurring", "fieldservice_sale"],
    "data": [
        "views/fsm_frequency_set_view.xml",
        "views/sale_order_view.xml",
    ],
    "license": "AGPL-3",
    "development_status": "Beta",
    "installable": True,
    "auto_install": True,
}

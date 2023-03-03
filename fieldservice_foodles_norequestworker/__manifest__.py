# Copyright (C) 2023 Raphaël Reverdy
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Field service custom no preferred workers",
    "summary": "Base module to install lot of things in no time",
    "version": "14.0.0.0.1",
    "license": "AGPL-3",
    "category": "Akretion",
    "author": "Akretion",
    "website": "https://github.com/akretion",
    "depends": [
        "fieldservice",
    ],
    "data": [
        "views/fsm_location.xml",
        "views/fsm_order.xml",
        "views/menu.xml",
    ],
    "application": True,
}

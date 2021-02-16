# Copyright (C) 2021 <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Field Service HR",
    "summary": "Link Workers and Employees",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Field Service",
    "author": "Akretin, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/field-service",
    "depends": [
        "hr",
        "fieldservice",
    ],
    "data": [
        "views/fsm_person.xml",
    ],
    "application": True,
    "development_status": "Beta",
    "maintainers": ["hparfr"],
}

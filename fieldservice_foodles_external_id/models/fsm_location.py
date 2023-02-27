
from odoo import _, fields, models

class FSMLocation(models.Model):
    _inherit = "fsm.location"

    external_id = fields.Char(string="External id")

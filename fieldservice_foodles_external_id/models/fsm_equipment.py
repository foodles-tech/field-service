
from odoo import _, fields, models

class FSMEquipment(models.Model):
    _inherit = "fsm.equipment"

    external_id = fields.Char(string="External id")

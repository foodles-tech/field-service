from odoo import fields, models, api

class FSMVisibilityMixin(models.AbstractModel):
    _name = 'fsm.visibility.mixin'
    _description= "Helps fsm models to decide wether or not they should display stages information"

    visibility_display_stage_management = fields.Boolean(
        "Display stage management", compute="_compute_stage_management"
    )

    visibility_territory_management = fields.Boolean(
        "Display stage management", compute="_compute_territory_management"
    )

    visibility_child_equipment = fields.Boolean(
        "Display stage management", compute="_compute_child_equipment"
    )

    def _compute_stage_management(self):
        for record in self:
            record.visibility_display_stage_management = self.env.user.company_id.stage_management

    def _compute_territory_management(self):
        for record in self:
            record.visibility_territory_management = not self.env.user.company_id.no_territory_management

    def _compute_child_equipment(self):
        for record in self:
            record.visibility_child_equipment = self.env.user.company_id.child_equipment


from odoo import fields, models, api

class FSMStageVisibilityMixin(models.AbstractModel):
    _name = 'fsm.stage.visibility.mixin'
    _description= "Helps fsm models to decide wether or not they should display stages information"

    visibility_display_stage_management = fields.Boolean(
        "Display stage management", compute="_compute_stage_management"
    )

    def _compute_stage_management(self):
        for record in self:
            record.visibility_display_stage_management = not self.env.user.company_id.no_stage_management




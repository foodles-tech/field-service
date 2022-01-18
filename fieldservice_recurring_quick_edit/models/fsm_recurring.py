# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class FSMRecurringOrder(models.Model):
    _inherit = "fsm.recurring"


    is_fsm_frequency_set_abstract = fields.Boolean()
    fsm_abstract_frequency_set_id = fields.Many2one(
        "fsm.frequency.set",
        "Generic Frequency Set",
        index=True,
        copy=True,
        help="Frequency of the service",
        domain=[("is_abstract", "=", True)],
    )
    fsm_frequency_qedit_ids = fields.One2many(
        "fsm.frequency",
        "fsm_recurring_id",
        copy=False,
        domain="[('is_quick_editable','=', True)]",
        compute="_compute_quickedit",
        inverse="_inverse_quickedit",
        store=True,
        help="Technical field used to allow a quick edit of fsm_frequency_ids",
    )
    fsm_concrete_frequency_ids = fields.Many2many(
        related="fsm_concrete_frequency_set_id.fsm_concrete_frequency_ids"
        # fsm_concrete_frequency_set_id.concrete_frequency_ids ?
#        "fsm.frequency", "fsm_recurring_id", string="Frequency Rules",
    )
    fsm_frequency_ids = fields.Many2many(
        related="fsm_frequency_set_id.fsm_frequency_ids"
    )


    fsm_concrete_frequency_set_id = fields.Many2one(
        "fsm.frequency.set",
        "Concrete Frequency",
        copy=False,
    )

    fsm_frequency_set_id = fields.Many2one(
        compute="_compute_fsm_frequency_set_id",
        readonly=True,
        store=True)


    edit_type = fields.Selection(
        [("quick_edit", "Quick edit"),
        ("advanced", "Advanced edit"),
        ("none", "Only abstract")],
        default="none",
    )

    @api.depends("edit_type", "fsm_abstract_frequency_set_id")
    def _compute_fsm_frequency_set_id(self):
        for rec in self:
            print('dans edit_type')
            if rec.edit_type == "none":
                rec.fsm_frequency_set_id = rec.fsm_abstract_frequency_set_id
            else:
                #TODO copy frequency_set params like buffer, days ahead ?
                rec.fsm_frequency_set_id = rec.fsm_concrete_frequency_set_id
    
    @api.depends("edit_type", "fsm_abstract_frequency_set_id")
    def _compute_quickedit(self):
        for rec in self:
            if not rec.fsm_concrete_frequency_set_id:
                # save first
                print('no concrete')
                continue
            if rec.edit_type == "advanced":
                print(" on copie dans qedit ?")

            if rec.edit_type == "quick_edit" and rec.fsm_abstract_frequency_set_id:
                if not len(rec.fsm_concrete_frequency_ids) == 0:
                    # we do not know if old value was advanced or none
                    # always copy concrete freq
                    # if one wants to restart from blank
                    # just delete all the concrete lines
                    to_add = rec.fsm_concrete_frequency_ids - rec.fsm_frequency_qedit_ids
                    to_rm = rec.fsm_frequency_qedit_ids - rec.fsm_concrete_frequency_ids
                    import pdb
                    pdb.set_trace()
                    rec.fsm_frequency_qedit_ids |= rec.fsm_concrete_frequency_ids
                    print('on va ajouter')
                    print(to_add.ids)
                    continue

                print('on copie')
                for freq in self.fsm_abstract_frequency_set_id.fsm_frequency_ids:
                    new_freq = freq.copy({
                        "origin": self.fsm_abstract_frequency_set_id.name,
                        "is_abstract": False,
                        "fsm_recurring_id": self.id,
                        })
                    rec.fsm_frequency_qedit_ids |= new_freq
                   # rec.fsm_concrete_frequency_ids |= new_freq
                   # rec.fsm_concrete_frequency_set_id.fsm_concrete_frequency_ids = [(6, 0, rec.fsm_concrete_frequency_ids.ids)]
    
    def _inverse_quickedit(self):
        for rec in self:
            if rec.fsm_frequency_qedit_ids:
                # import pdb
                # pdb.set_trace()
                to_rm = rec.fsm_concrete_frequency_ids - rec.fsm_frequency_qedit_ids
                to_rm.unlink()
                print('vont se faire degager -')
                print(to_rm.ids)
                rec.fsm_concrete_frequency_ids = rec.fsm_frequency_qedit_ids
            else:
                print('pas de quickedit on fait rien')


    def action_view_fms_order(self):
        # TODO: move this in parent
        fms_orders = self.mapped("fsm_order_ids")
        action = self.env.ref("fieldservice.action_fsm_operation_order").read()[0]
        if len(fms_orders) > 1:
            action["domain"] = [("id", "in", fms_orders.ids)]
        elif len(fms_orders) == 1:
            form_view = [(self.env.ref("fieldservice.fsm_order_form").id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = fms_orders.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        action["key2"] = "client_action_multi"
        return action

    def generate_orders(self):
        """
        Executed from form view (call private method) _generate_orders
        """
        return self._generate_orders()

    @api.model
    def create(self, values):
        recurring = super().create(values)
        if not recurring.fsm_concrete_frequency_set_id:
            # always create a fsm_concrete for each recurring.
            # it's a bit overkill but spare us lots of issues.
            concrete_freq_set_id = self.env['fsm.frequency.set'].create(
                {"name": recurring.name,
                "is_abstract": False,
            })
            recurring.fsm_concrete_frequency_set_id = concrete_freq_set_id
        return recurring


    def write(self, values):
        result = super().write(values)
        for rec in self:
            # kind of inverse method for related fields
            # new frequencies may exist here but not linked to 
            # frequency_set
            # and unlinked frequency can be there too
            freq_set = rec.fsm_concrete_frequency_set_id
            # removing abstracted will not hurt
            import pdb
            aa = rec.fsm_concrete_frequency_ids
            bb = rec.fsm_frequency_ids
            if rec.edit_type == 'quick_edit':
                print('on sauvg quick')
                frequencies = rec.fsm_frequency_qedit_ids
            elif rec.edit_type == 'advanced':
                print('on sauvg advanced')
                frequencies = rec.fsm_frequency_ids.filtered(lambda x: not x.is_abstract)
                to_rm = rec.fsm_concrete_frequency_ids - frequencies
                print("on va virer")
                print(to_rm)
                to_rm.unlink()
            else:
                print('on sauvg abstract donc on quitte')
                continue

            concrete = rec.fsm_concrete_frequency_ids.filtered(lambda x: not x.is_abstract)
            to_rm = concrete - frequencies
            pdb.set_trace()
            #to_rm.unlink()

            freq_set.fsm_concrete_frequency_ids = [(6, 0, frequencies.ids)]
        return result

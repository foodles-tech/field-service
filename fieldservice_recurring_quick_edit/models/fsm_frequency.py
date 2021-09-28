# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import rrule

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.fieldservice_recurring.models.fsm_frequency import FREQUENCIES

INTERVAl_FREQUENCIES = [
    ("1", "First"),
    ("2", "Second"),
    ("3", "Third"),
    ("4", "Forth"),
    ("5", "Last"),
    ("6", "Each"),
]


class FSMFrequency(models.Model):
    _inherit = "fsm.frequency"

    fsm_recurring_id = fields.Many2one(
        "fsm.recurring", "Recurring order", ondelete="cascade", readonly=True
    )
    # simple edit helper with planned_hour precision
    interval_frequency = fields.Selection(INTERVAl_FREQUENCIES)
    use_planned_hour = fields.Boolean()
    planned_hour = fields.Float("Planned Hours")
    is_quick_editable = fields.Boolean(
        compute="_compute_is_quick_editable", default=False, store=True
    )
    day_quick_edit = fields.Selection(
        string="Day",
        selection=[
            ("mo", "Monday"),
            ("tu", "Tuesday"),
            ("we", "Wednesday"),
            ("th", "Thuesday"),
            ("fr", "Friday"),
            ("sa", "Saturday"),
            ("su", "Sunday"),
        ],
        compute="_compute_day_quick_edit",
        default="mo",
    )
    week_day = fields.Char(compute="_calc_week_day")
    #    interval_type = fields.Selection(default="weekly")
    origin = fields.Char()

    def name_get(self):
        result = []
        for freq in self.sudo():
            name = freq.name
            if freq.fsm_recurring_id:
                name = "{} - {}".format(freq.fsm_recurring_id.name, freq.name)
            result.append((freq.id, name))
        return result

    @api.depends("mo", "tu", "we", "th", "fr", "sa", "su")
    def _compute_day_quick_edit(self):
        for rec in self:
            rec.day_quick_edit = False
            weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            for field in weekdays:
                if rec[field]:
                    rec.day_quick_edit = field

    @api.depends("mo", "tu", "we", "th", "fr", "sa", "su")
    def _compute_is_quick_editable(self):
        for rec in self:
            nb_dayselected = 0
            weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
            for field in weekdays:
                if rec[field]:
                    nb_dayselected += 1
            rec.is_quick_editable = nb_dayselected == 1

    @api.onchange("day_quick_edit")
    def onchange_day_quick_edit(self):
        if not self.day_quick_edit:
            self.name = ""
            return
        days = {
            "mo": _("Monday"),
            "tu": _("Tuesday"),
            "we": _("Wednesday"),
            "th": _("Thuesday"),
            "fr": _("Friday"),
            "sa": _("Saturday"),
            "su": _("Sunday"),
        }
        weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]

        weekdays.remove(self.day_quick_edit)
        self[self.day_quick_edit] = True
        self.name = self.day_quick_edit and days[self.day_quick_edit] or ""
        self.use_byweekday = True
        for field in weekdays:
            print(field)
            self[field] = False

    def _calc_week_day(self):
        for rec in self:
            rec.week_day = ",".join(["%s" % d for d in (rec._byweekday() or [])])

    @api.onchange("use_planned_hour")
    def _onchange_use_planned_hour(self):
        """
        Checks use_byweekday boolean
        """
        for freq in self:
            freq.use_byweekday = freq.use_planned_hour

    def _byhours(self):
        self.ensure_one()
        if not self.use_planned_hour or not self.week_day or self.week_day == "none":
            return None, None
        hours, minutes = self._split_time_to_hour_min(self.planned_hour)
        return hours, minutes

    def _split_time_to_hour_min(self, time):
        if not time:
            time = 0.0
        duration_minute = time * 60
        hours, minutes = divmod(duration_minute, 60)
        return int(hours), int(minutes)

    @api.constrains("week_day", "planned_hour")
    def _check_planned_hour(self):
        for rec in self:
            # if not rec.week_day:
            #     raise UserError(_("Week day must be set"))
            if rec.use_planned_hour:
                hours, minutes = rec._byhours()
                if not 0 <= hours <= 23:
                    raise UserError(_("Planned hours must be between 0 and 23"))

    def _get_rrule(self, dtstart=None, until=None):
        self.ensure_one()
        if self.planned_hour:
            # TODO move use_planned_hour to parent module
            hours, minutes = self._byhours()
            freq = FREQUENCIES[self.interval_type]
            # to avoid bug off creation of rrule if somme args is none
            # we add anly defined args to kwargs
            kwargs = {}
            if self.interval:
                kwargs["interval"] = self.interval
            if dtstart:
                kwargs["dtstart"] = dtstart
            if until:
                kwargs["until"] = until
            if self._byweekday():
                kwargs["byweekday"] = self._byweekday()
            if self._bymonth():
                kwargs["bymonth"] = self._bymonth()
            if self._bymonthday():
                kwargs["bymonthday"] = self._bymonthday()
            if self._bysetpos():
                kwargs["bysetpos"] = self._bysetpos()
            if hours or hours == 0:
                kwargs["byhour"] = hours
            if minutes or minutes == 0:
                kwargs["byminute"] = minutes
                kwargs["bysecond"] = 0
            return rrule(freq, **kwargs)
        return super(FSMFrequency, self)._get_rrule(dtstart=dtstart, until=until)

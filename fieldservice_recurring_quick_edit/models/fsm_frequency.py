# Copyright (C) 2019 - TODAY, mourad EL HADJ MIMOUNE, Akretion
# Copyright (C) 2021 Akretion <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

import pytz
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
        # only if set.is_abstract is false
        # it's quite hard to have a good sql constraint
        "fsm.recurring", "Recurring order", ondelete="cascade", readonly=True
    )
    # simple edit helper with planned_hour precision
    interval_frequency = fields.Selection(INTERVAl_FREQUENCIES, default="6")
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


    @api.onchange("interval_frequency")
    def _onchange_interval_frequency(self):
        """
        Checks use_bypose boolean
        """
        for freq in self:
            if not freq.interval_frequency or freq.interval_frequency == "6":
                freq.set_pos = 0
            elif freq.interval_frequency == "5":
                freq.set_pos = -1
            else:
                freq.set_pos = int(freq.interval_frequency)

    def _byhours(self):
        self.ensure_one()
        if not self.planned_hour:
            return 0, 0
        tzhours, minutes = self._split_time_to_hour_min(self.planned_hour)
        # todo set timezone on company. if user tz is not defined we can use company tz
        user_tz = (
            self.env.user.tz
            and pytz.timezone(self.env.user.tz)
            or pytz.timezone("Europe/Paris")
        )
        dt = datetime.datetime.now(user_tz)
        dt = dt.replace(hour=tzhours)
        hours = dt.astimezone(pytz.utc).hour
        return hours, minutes

    def _split_time_to_hour_min(self, time):
        if not time:
            time = 0.0
        duration_minute = time * 60
        hours, minutes = divmod(duration_minute, 60)
        return int(hours), int(minutes)

    def _get_rrule(self, dtstart=None, until=None):
        self.ensure_one()
        if self.planned_hour:
            # TODO move planned_hour to parent module
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

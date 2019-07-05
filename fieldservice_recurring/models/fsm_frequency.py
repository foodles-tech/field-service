# Copyright (C) 2019 - TODAY, Brian McMaster, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.rrule import MO, TU, WE, TH, FR, SA, SU
from dateutil.rrule import YEARLY, MONTHLY, WEEKLY, DAILY
from dateutil.rrule import rrule

from odoo import fields, models, api, _
from odoo.exceptions import UserError


WEEKDAYS = {
    'mo': MO,
    'tu': TU,
    'we': WE,
    'th': TH,
    'fr': FR,
    'sa': SA,
    'su': SU
}

FREQUENCIES = {
    'yearly': YEARLY,
    'monthly': MONTHLY,
    'weekly': WEEKLY,
    'daily': DAILY,
}

FREQUENCY_SELECT = [
    ('yearly', 'Yearly'),
    ('monthly', 'Monthly'),
    ('weekly', 'Weekly'),
    ('daily', 'Daily')
]


class FSMFrequency(models.Model):
    _name = 'fsm.frequency'
    _description = 'Frequency Rule for Field Service Orders'
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True)
    active = fields.Boolean(default=True)
    interval = fields.Integer(
        string='Repeat Every', help="The number of intervals between events",
        default=1, required=True, track_visibility='onchange')
    interval_type = fields.Selection(
        FREQUENCY_SELECT, string='Interval Type',
        required=True, track_visibility='onchange')
    is_exclusive = fields.Boolean(
        string='Exclusive Rule?', default=False,
        help="""Checking this box will make this an exclusive rule. Exclusive
            rules prevent the configured days from being a schedule option""")
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
    use_bymonthday = fields.Boolean(
        string='Use Day of Month',
        help="""When selected you will be able to specify which calendar day
            of the month the event occurs on""")
    month_day = fields.Integer(
        string='Day of Month', track_visibility='onchange')

    use_byweekday = fields.Boolean(
        string='Use Days of Week',
        help="""When selected you will be able to choose which days of the
            week the scheduler will include (or exclude if Exclusive rule)""")
    mo = fields.Boolean('Monday', default=False)
    tu = fields.Boolean('Tuesday', default=False)
    we = fields.Boolean('Wednesday', default=False)
    th = fields.Boolean('Thursday', default=False)
    fr = fields.Boolean('Friday', default=False)
    sa = fields.Boolean('Saturday', default=False)
    su = fields.Boolean('Sunday', default=False)

    use_bymonth = fields.Boolean(string='Use Months')
    jan = fields.Boolean('January', default=False)
    feb = fields.Boolean('February', default=False)
    mar = fields.Boolean('March', default=False)
    apr = fields.Boolean('April', default=False)
    may = fields.Boolean('May', default=False)
    jun = fields.Boolean('June', default=False)
    jul = fields.Boolean('July', default=False)
    aug = fields.Boolean('August', default=False)
    sep = fields.Boolean('September', default=False)
    oct = fields.Boolean('October', default=False)
    nov = fields.Boolean('November', default=False)
    dec = fields.Boolean('December', default=False)

    use_setpos = fields.Boolean(string='Use Position')
    set_pos = fields.Integer(
        string="By Position",
        help="""Specify an occurrence number, positive or negative,
            corresponding to the nth occurrence of the rule inside
            the frequency period. For example, -1 if combined with a
            'Monthly' frequency, and a weekday of (MO, TU, WE, TH, FR),
            will result in the last work day of every month.""")
    use_rrulestr = fields.Boolean(string='Use rrule string')
    rrule_string = fields.Char()

    @api.constrains('set_pos')
    def _check_set_pos(self):
        if self.use_setpos:
            if not (-366 < self.set_pos < 366):
                raise UserError(_("Position must be between -366 and 366"))

    @api.constrains('month_day')
    def _check_month_day(self):
        if self.use_bymonthday:
            if not (1 <= self.month_day <= 31):
                raise UserError(_("'Day of Month must be between 1 and 31"))

    def _get_rrule(self, dtstart=None, until=None):
        self.ensure_one()
        if self.use_rrulestr:
            return rrule.rrulestr(self.rrule_string)
        else:
            freq = FREQUENCIES[self.interval_type]
            return rrule(freq, interval=self.interval,
                         dtstart=dtstart, until=until,
                         byweekday=self._byweekday(),
                         bymonth=self._bymonth(),
                         bymonthday=self._bymonthday(),
                         bysetpos=self._bysetpos(),
                         )

    def _byweekday(self):
        """
        Checks day of week booleans and builds the value for rrule parameter
        @returns: {list} byweekday: list of WEEKDAY values used for rrule
        """
        self.ensure_one()
        if not self.use_byweekday:
            return None
        weekdays = ['mo', 'tu', 'we', 'th', 'fr', 'sa', 'su']
        byweekday = [WEEKDAYS[field] for field in weekdays if self[field]]
        return byweekday

    def _bymonth(self):
        """
        Checks month booleans and builds the value for rrule parameter
        @returns: {list} bymonth: list of integers used for rrule
        """
        self.ensure_one()
        if not self.use_bymonth:
            return None
        months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun',
                  'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        bymonth = [months.index(field) + 1 for field in months if self[field]]
        return bymonth

    def _bymonthday(self):
        self.ensure_one()
        if not self.use_bymonthday:
            return None
        return self.month_day

    def _bysetpos(self):
        self.ensure_one()
        if not self.use_setpos or self.set_pos == 0:
            return None
        return self.set_pos

FREQNAMES = ['YEARLY','MONTHLY','WEEKLY','DAILY','HOURLY','MINUTELY','SECONDLY']

def rrule_to_string(rule):
    """
       this methode can be used to debuging
       ex: print(FSMFrequency._get_rrule())
    """
    output = []
    h,m,s = [None] * 3
    if rule._dtstart:
        output.append(rule._dtstart.strftime('DTSTART:%Y%m%dT%H%M%S'))
        h,m,s = rule._dtstart.timetuple()[3:6]

    parts = ['FREQ='+FREQNAMES[rule._freq]]
    if rule._interval != 1:
        parts.append('INTERVAL='+str(rule._interval))
    if rule._wkst:
        parts.append('WKST='+str(rule._wkst))
    if rule._count:
        parts.append('COUNT='+str(rule._count))

    for name, value in [
            ('BYSETPOS', rule._bysetpos),
            ('BYMONTH', rule._bymonth),
            ('BYMONTHDAY', rule._bymonthday),
            ('BYYEARDAY', rule._byyearday),
            ('BYWEEKNO', rule._byweekno),
            ('BYWEEKDAY', rule._byweekday),
            ]:
        if value:
            parts.append(name+'='+','.join(str(v) for v in value))

    # Only include these if they differ from rule._dtstart
    if rule._byhour and list(rule._byhour)[0] != h:
        parts.append('BYHOUR=%s' % rule._byhour)
    if rule._byminute and list(rule._byminute)[0] != m:
        parts.append('BYMINUTE=%s' % rule._byminute)
    if rule._bysecond and list(rule._bysecond)[0] != s:
        parts.append('BYSECOND=%s' % rule._bysecond),


    output.append(';'.join(parts))
    return '\n'.join(output)

from dateutil.rrule import rrule
rrule.__str__ = rrule_to_stringfields


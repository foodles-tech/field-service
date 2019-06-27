# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class FSMRecurringCase(TransactionCase):

    def setUp(self):
        super(FSMRecurringCase, self).setUp()
        self.Recurring = self.env['fsm.recurring']
        self.Frequency = self.env['fsm.frequency']
        self.FrequencySet = self.env['fsm.frequency.set']
        self.RecurringTemplate = self.env['fsm.recurring.template']

    def _create_frequence_rule_set(self):
        print('_create_frequence_rule_set()')
        # Create frequence rule

        # Create frequency rule set

    def test_fsm_recurring(self):
        """I create frequency rule, frequence rule set, recurring template
        then create a recurring order and select recurring template.
        When I click contirm I expect,
        ...
        """
        frset = self._create_frequence_rule_set()
        # self.Recurring._cron_scheduled_task()

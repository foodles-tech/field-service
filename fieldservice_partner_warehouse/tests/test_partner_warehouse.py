from odoo.tests.common import Form, TransactionCase


class TestPartnerWarehouse(TransactionCase):
    def setUp(self):
        super(TestPartnerWarehouse, self).setUp()
        self.order = self.env["sale.order"]
        self.equipment = self.env["fsm.equipment"]

        self.whconfig = self.env["res.config.settings"].write(
            {
                "group_fsm_equipment": True,
            }
        )
        self.wh1 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse_test_1",
                "code": "WHT1",
            }
        )
        self.wh2 = self.env["stock.warehouse"].create(
            {
                "name": "Warehouse_test_2",
                "code": "WHT2",
            }
        )
        self.partner1 = self.env.ref("base.res_partner_3")
        self.partner1.write(
            {
                "partner_supply_warehouse_id": self.wh1,
            }
        )
        self.partner2 = self.env.ref("base.res_partner_address_10")
        self.partner2.write(
            {
                "type": "fsm_location",
                "partner_supply_warehouse_id": self.wh2,
            }
        )
        self.partner3 = self.env["res.partner"].create(
            {
                "name": "TestPartner3",
                "company_type": "person",
                "parent_id": self.partner1.id,
                "type": "fsm_location",
            }
        )

    # in this first test, we test "_compute_warehouse_id" in a default_resupply_warehouse_id which is in a fsm_equipment_form_view
    def test_1_autofill_fsm_partner_warehouse_id(self):
        view_id = "fieldservice.fsm_equipment_form_view"
        with Form(self.equipment, view=view_id) as Equipment1Test:
            Equipment1Test.name = "equipment test 1"
            Equipment1Test.current_location_id = self.partner2.owned_location_ids
        Equipment1Test.save()
        self.assertEqual(
            self.equipment.default_resupply_warehouse_id.id,
            self.equipment.current_location_id.partner_id.partner_supply_warehouse_id.id,
        )

    # in this second test, we test "_compute_warehouse_id" in a default_resupply_warehouse_id when the choosen partner has no attribute warehouse but his parent does
    def test_2_autofill_fsm_partner_warehouse_id(self):
        view_id = "fieldservice.fsm_equipment_form_view"
        with Form(self.equipment, view=view_id) as Equipment2Test:
            Equipment2Test.name = "equipment test 2"
            Equipment2Test.current_location_id = self.partner3.owned_location_ids
        Equipment2Test.save()
        self.assertEqual(
            self.equipment.default_resupply_warehouse_id.id,
            self.equipment.current_location_id.partner_id.parent_id.partner_supply_warehouse_id.id,
        )

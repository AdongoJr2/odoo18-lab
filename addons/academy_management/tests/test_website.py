from odoo.tests import TransactionCase


class TestAcademyWebsite(TransactionCase):
    def test_academy_home_route_and_template_are_configured(self):
        from ..controllers.website import AcademyWebsiteController

        routing = AcademyWebsiteController.academy_home.original_routing
        self.assertEqual(routing["routes"], ["/academy"])
        self.assertEqual(routing["auth"], "public")
        self.assertTrue(routing["website"])
        self.assertTrue(self.env.ref("academy_management.academy_website_home"))

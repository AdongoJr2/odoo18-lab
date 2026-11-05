from odoo.tests import TransactionCase


class TestAcademyWebsite(TransactionCase):
    def test_academy_home_route_and_template_are_configured(self):
        from ..controllers.website import AcademyWebsiteController

        routing = AcademyWebsiteController.academy_home.original_routing
        self.assertEqual(routing["routes"], ["/academy"])
        self.assertEqual(routing["auth"], "public")
        self.assertTrue(routing["website"])
        self.assertTrue(self.env.ref("academy_management.academy_website_home"))

    def test_public_enrollment_routes_and_templates_are_configured(self):
        from ..controllers.website import AcademyWebsiteController

        self.assertEqual(
            AcademyWebsiteController.academy_courses.original_routing["routes"],
            ["/academy/courses"],
        )
        self.assertEqual(
            AcademyWebsiteController.academy_course.original_routing["routes"],
            ["/academy/course/<int:course_id>"],
        )
        self.assertEqual(
            AcademyWebsiteController.academy_enroll.original_routing["routes"],
            ["/academy/course/<int:course_id>/enroll"],
        )
        self.assertEqual(
            AcademyWebsiteController.academy_enroll.original_routing["methods"],
            ["POST"],
        )
        self.assertTrue(
            self.env.ref("academy_management.academy_website_course_detail")
        )
        self.assertTrue(
            self.env.ref("academy_management.academy_website_enrollment_success")
        )

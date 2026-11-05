from odoo.tests import TransactionCase


class TestAcademyCatalogCourse(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Course = self.env["x_academy.catalog.course"]

    def test_create_course_uses_xml_defaults(self):
        course = self.Course.create(
            {
                "x_code": "XML101",
                "x_name": "XML Data Modules",
            }
        )
        self.assertEqual(course.x_capacity, 0)
        self.assertTrue(course.x_active)

    def test_course_fields_and_views_are_defined_in_xml(self):
        field_names = self.Course._fields
        self.assertIn("x_code", field_names)
        self.assertIn("x_description", field_names)
        self.assertIn("x_capacity", field_names)
        self.assertIn("x_active", field_names)

        action = self.env.ref("academy_catalog.action_x_academy_catalog_course")
        self.assertEqual(action.res_model, "x_academy.catalog.course")
        self.assertEqual(action.view_mode, "list,form")

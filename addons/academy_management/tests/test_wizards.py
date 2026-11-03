from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestAcademyBulkEnrollment(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Student = self.env["academy.student"]
        self.Course = self.env["academy.course"]
        self.Wizard = self.env["academy.bulk.enrollment"]

    def test_bulk_enrollment_assigns_course_and_state(self):
        course = self.Course.create({"name": "Python", "capacity": 2})
        students = self.Student.create([{"name": "Student A"}, {"name": "Student B"}])
        wizard = self.Wizard.with_context(active_ids=students.ids).create(
            {"course_id": course.id}
        )

        self.assertEqual(wizard.student_ids, students)
        wizard.action_confirm()

        self.assertEqual(students.mapped("state"), ["enrolled", "enrolled"])
        self.assertEqual(students.mapped("course_id"), course)

    def test_bulk_enrollment_rejects_insufficient_capacity(self):
        course = self.Course.create({"name": "Python", "capacity": 1})
        students = self.Student.create([{"name": "Student A"}, {"name": "Student B"}])
        wizard = self.Wizard.with_context(active_ids=students.ids).create(
            {"course_id": course.id}
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()

        self.assertEqual(students.mapped("state"), ["draft", "draft"])

    def test_bulk_enrollment_rejects_non_draft_students(self):
        course = self.Course.create({"name": "Python"})
        student = self.Student.create({"name": "Student A", "state": "enrolled"})
        wizard = self.Wizard.with_context(active_ids=student.ids).create(
            {"course_id": course.id}
        )

        with self.assertRaises(UserError):
            wizard.action_confirm()

    def test_bulk_enrollment_action_is_bound_to_student_list(self):
        action = self.env.ref("academy_management.academy_bulk_enrollment_action")
        self.assertEqual(action.binding_model_id.model, "academy.student")
        self.assertEqual(action.binding_view_types, "list")

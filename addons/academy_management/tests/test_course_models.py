from odoo.tests import TransactionCase


class TestAcademyCourse(TransactionCase):
    def test_course_creation(self):
        course = self.env["academy.course"].create(
            {
                "name": "New Course",
                "description": "Test description",
            }
        )
        self.assertTrue(course.active)
        self.assertEqual(course.name, "New Course")

    def test_course_student_relationship(self):
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {
                "name": "Test Student",
                "course_id": course.id,
            }
        )
        self.assertIn(student, course.student_ids)

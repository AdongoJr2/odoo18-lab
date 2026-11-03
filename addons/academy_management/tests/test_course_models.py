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


class TestAcademyCourseComputedFields(TransactionCase):
    def test_student_count_computation(self):
        """Test that student_count is computed correctly."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        self.assertEqual(course.student_count, 0)

        self.env["academy.student"].create(
            {"name": "Student 1", "course_id": course.id}
        )
        self.env["academy.student"].create(
            {"name": "Student 2", "course_id": course.id}
        )
        self.assertEqual(course.student_count, 2)

    def test_is_full_computation(self):
        """Test that is_full is computed correctly."""
        course = self.env["academy.course"].create(
            {"name": "Test Course", "capacity": 2}
        )
        self.assertFalse(course.is_full)

        self.env["academy.student"].create(
            {"name": "Student 1", "course_id": course.id}
        )
        self.env["academy.student"].create(
            {"name": "Student 2", "course_id": course.id}
        )
        self.assertFalse(course.is_full)

        course.student_ids[:2].action_enroll()
        self.assertTrue(course.is_full)

    def test_capacity_default(self):
        """Test that capacity defaults to 30."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        self.assertEqual(course.capacity, 30)

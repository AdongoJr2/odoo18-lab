from odoo.tests import HttpCase, tagged


@tagged('post_install', 'integration')
class TestAcademyIntegration(HttpCase):
    """Integration tests for the Academy Management module."""

    def setUp(self):
        super().setUp()
        self._create_test_data()

    def _create_test_data(self):
        """Create test data for integration tests."""
        self.Student = self.env['academy.student']
        self.course = self.env['academy.course'].create({
            'name': 'Advanced Python',
            'description': 'Advanced Python programming course',
        })
        self.subject = self.env['academy.subject'].create({
            'name': 'OOP Concepts',
            'description': 'Object-Oriented Programming',
        })
        self.student = self.Student.create({
            'name': 'Integration Test Student',
            'email': 'integration@example.com',
            'course_id': self.course.id,
        })
        self.student.subject_ids = [(4, self.subject.id)]

    def test_full_workflow(self):
        """Test the complete student management workflow."""
        self.assertEqual(self.student.course_id.name, 'Advanced Python')
        self.assertIn(self.subject, self.student.subject_ids)

    def test_data_relationships(self):
        """Test relationship integrity between models."""
        self.assertIn(self.student, self.course.student_ids)
        self.assertIn(self.student, self.subject.student_ids)

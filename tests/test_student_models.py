from odoo.tests import TransactionCase


class TestAcademyStudent(TransactionCase):
    """Test academy.student model."""

    def setUp(self):
        super().setUp()
        self.Student = self.env['academy.student']
        self.Course = self.env['academy.course']
        self.Subject = self.env['academy.subject']

    def test_student_creation(self):
        """Test basic student record creation."""
        student = self.Student.create({
            'name': 'Test Student',
            'email': 'test@example.com',
            'phone': '123-456-7890',
        })
        self.assertEqual(student.name, 'Test Student')
        self.assertTrue(student.active)
        self.assertEqual(student.student_id, 'STU0001')

    def test_student_id_sequence(self):
        """Test that student IDs are auto-generated."""
        students = self.Student.create([
            {'name': 'Student A'},
            {'name': 'Student B'},
        ])
        self.assertEqual(students[0].student_id, 'STU0001')
        self.assertEqual(students[1].student_id, 'STU0002')

    def test_student_age_computation(self):
        """Test age computation from date_of_birth."""
        student = self.Student.create({
            'name': 'Test Student',
            'date_of_birth': '1990-01-01',
        })
        self.assertGreater(student.age, 30)

    def test_student_course_restriction(self):
        """Test that course deletion is restricted."""
        course = self.Course.create({'name': 'Python Course'})
        student = self.Student.create({
            'name': 'Test Student',
            'course_id': course.id,
        })
        with self.assertRaises(Exception):
            course.unlink()

    def test_student_subject_many2many(self):
        """Test subject assignment via many2many relationship."""
        subject = self.Subject.create({'name': 'Math'})
        student = self.Student.create({'name': 'Test Student'})
        student.subject_ids = [(4, subject.id)]
        self.assertIn(subject, student.subject_ids)

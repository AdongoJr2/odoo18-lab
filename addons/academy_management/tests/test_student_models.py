from odoo.tests import TransactionCase


class TestAcademyStudent(TransactionCase):
    """Test academy.student model."""

    def setUp(self):
        super().setUp()
        self.Student = self.env["academy.student"]
        self.Course = self.env["academy.course"]
        self.Subject = self.env["academy.subject"]

    def test_student_creation(self):
        """Test basic student record creation."""
        student = self.Student.create(
            {
                "name": "Test Student",
                "email": "test@example.com",
                "phone": "123-456-7890",
            }
        )
        self.assertEqual(student.name, "Test Student")
        self.assertTrue(student.active)
        self.assertRegex(student.student_id, r"^STU\d{4}$")

    def test_student_id_sequence(self):
        """Test that student IDs are auto-generated."""
        students = self.Student.create(
            [
                {"name": "Student A"},
                {"name": "Student B"},
            ]
        )
        self.assertRegex(students[0].student_id, r"^STU\d{4}$")
        self.assertRegex(students[1].student_id, r"^STU\d{4}$")
        self.assertNotEqual(students[0].student_id, students[1].student_id)

    def test_student_age_computation(self):
        """Test age computation from date_of_birth."""
        student = self.Student.create(
            {
                "name": "Test Student",
                "date_of_birth": "1990-01-01",
            }
        )
        self.assertGreater(student.age, 30)

    def test_student_course_restriction(self):
        """Test that course deletion is restricted."""
        course = self.Course.create({"name": "Python Course"})
        self.Student.create(
            {
                "name": "Test Student",
                "course_id": course.id,
            }
        )
        with self.assertRaises(Exception):
            course.unlink()

    def test_student_subject_many2many(self):
        """Test subject assignment via many2many relationship."""
        subject = self.Subject.create({"name": "Math"})
        student = self.Student.create({"name": "Test Student"})
        student.subject_ids = [(4, subject.id)]
        self.assertIn(subject, student.subject_ids)


class TestAcademyStudentStateTransitions(TransactionCase):
    def test_enroll_student(self):
        """Test student enrollment workflow."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {"name": "Test Student", "course_id": course.id}
        )
        self.assertEqual(student.state, "draft")
        student.action_enroll()
        self.assertEqual(student.state, "enrolled")

    def test_graduate_student(self):
        """Test student graduation workflow."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {"name": "Test Student", "course_id": course.id}
        )
        student.action_enroll()
        student.action_graduate()
        self.assertEqual(student.state, "graduated")

    def test_drop_student(self):
        """Test student drop workflow."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {"name": "Test Student", "course_id": course.id}
        )
        student.action_enroll()
        student.action_drop()
        self.assertEqual(student.state, "dropped")

    def test_cannot_enroll_without_course(self):
        """Test that enrollment requires a course."""
        student = self.env["academy.student"].create({"name": "Test Student"})
        with self.assertRaises(Exception):
            student.action_enroll()

    def test_cannot_enroll_in_full_course(self):
        """Test that enrollment is blocked when course is full."""
        course = self.env["academy.course"].create(
            {"name": "Test Course", "capacity": 1}
        )
        student1 = self.env["academy.student"].create(
            {"name": "Student 1", "course_id": course.id}
        )
        student1.action_enroll()
        student2 = self.env["academy.student"].create(
            {"name": "Student 2", "course_id": course.id}
        )
        with self.assertRaises(Exception):
            student2.action_enroll()

    def test_reset_to_draft(self):
        """Test resetting student to draft."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {"name": "Test Student", "course_id": course.id}
        )
        student.action_enroll()
        student.action_drop()
        student.action_reset_to_draft()
        self.assertEqual(student.state, "draft")


class TestAcademyStudentViews(TransactionCase):
    def test_student_action_opens_kanban_first(self):
        action = self.env.ref("academy_management.academy_student_action")
        self.assertEqual(action.view_mode, "kanban,list,form")

    def test_student_kanban_view_groups_by_state(self):
        view = self.env.ref("academy_management.academy_student_view_kanban")
        self.assertIn('default_group_by="state"', view.arch_db)
        self.assertIn('<t t-name="card">', view.arch_db)

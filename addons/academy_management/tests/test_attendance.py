from datetime import date

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form, TransactionCase
from psycopg2 import IntegrityError


class TestAcademyAttendance(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Student = self.env["academy.student"]
        self.Course = self.env["academy.course"]
        self.Attendance = self.env["academy.attendance"]
        self.course = self.Course.create({"name": "Python"})
        self.student = self.Student.create(
            {"name": "Attendance Student", "course_id": self.course.id}
        )

    def test_attendance_defaults_and_creation(self):
        attendance = self.Attendance.create({"student_id": self.student.id})
        self.assertEqual(attendance.course_id, self.course)
        self.assertEqual(attendance.status, "present")
        self.assertEqual(attendance.attendance_date, date.today())

    def test_attendance_rejects_mismatched_course(self):
        other_course = self.Course.create({"name": "History"})
        with self.assertRaises(ValidationError):
            self.Attendance.create(
                {
                    "student_id": self.student.id,
                    "course_id": other_course.id,
                }
            )

    def test_attendance_requires_student_course(self):
        student = self.Student.create({"name": "Unassigned Student"})
        with self.assertRaises(UserError):
            self.Attendance.create({"student_id": student.id})

    def test_student_onchange_sets_course(self):
        other_course = self.Course.create({"name": "History"})
        other_student = self.Student.create(
            {"name": "History Student", "course_id": other_course.id}
        )
        with Form(self.Attendance) as attendance_form:
            attendance_form.student_id = other_student
            self.assertEqual(attendance_form.course_id, other_course)

    def test_attendance_is_unique_per_student_and_day(self):
        values = {"student_id": self.student.id, "attendance_date": "2000-01-01"}
        self.Attendance.create(values)
        with self.assertRaises(IntegrityError):
            self.Attendance.create(values)

    def test_student_cannot_create_attendance(self):
        student_group = self.env.ref("academy_management.group_academy_student")
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Attendance Student User",
                    "login": "attendance_student_user",
                    "groups_id": [(6, 0, [student_group.id])],
                }
            )
        )
        with self.assertRaises(AccessError):
            self.Attendance.with_user(user).create({"student_id": self.student.id})

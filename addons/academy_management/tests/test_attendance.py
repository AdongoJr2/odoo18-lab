from datetime import date

from odoo.exceptions import AccessError, ValidationError
from odoo.tests import TransactionCase


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

    def test_attendance_is_unique_per_student_and_day(self):
        values = {"student_id": self.student.id}
        self.Attendance.create(values)
        with self.assertRaises(Exception):
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

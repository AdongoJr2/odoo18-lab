from odoo.tests import TransactionCase


class TestAcademyMultiCompany(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Student = self.env["academy.student"]
        self.Attendance = self.env["academy.attendance"]
        self.company_a = self.env.company
        self.company_b = self.env["res.company"].create({"name": "Branch Campus B"})
        self.manager_group = self.env.ref("academy_management.group_academy_manager")
        self.teacher_group = self.env.ref("academy_management.group_academy_teacher")
        self.manager_both = self._create_user(
            "Both Companies Manager",
            self.manager_group,
            [self.company_a, self.company_b],
        )
        self.teacher_b = self._create_user(
            "Branch B Teacher", self.teacher_group, [self.company_b]
        )
        course = self.env.ref("academy_management.course_demo_python")
        self.student_a = self.Student.create(
            {"name": "Company A Student", "course_id": course.id}
        )
        self.student_b = self.Student.create(
            {
                "name": "Company B Student",
                "course_id": course.id,
                "company_id": self.company_b.id,
            }
        )

    def _create_user(self, name, group, companies):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "login": name.lower().replace(" ", "_"),
                    "email": f"{name.lower().replace(' ', '_')}@example.com",
                    "groups_id": [(6, 0, [group.id])],
                    "company_id": companies[0].id,
                    "company_ids": [(6, 0, [c.id for c in companies])],
                }
            )
        )

    def _attendance_for(self, student):
        return self.Attendance.create(
            {
                "student_id": student.id,
                "attendance_date": "2026-01-05",
                "status": "present",
            }
        )

    def test_student_company_defaults_to_current_company(self):
        student = self.Student.create({"name": "Default Company Student"})
        self.assertEqual(student.company_id, self.env.company)

    def test_attendance_company_follows_student(self):
        attendance = self._attendance_for(self.student_b)
        self.assertEqual(attendance.company_id, self.company_b)

    def test_branch_teacher_sees_only_own_company_students(self):
        visible = self.Student.with_user(self.teacher_b).search([])

        self.assertIn(self.student_b, visible)
        self.assertNotIn(self.student_a, visible)

    def test_branch_teacher_sees_only_own_company_attendance(self):
        attendance_a = self._attendance_for(self.student_a)
        attendance_b = self._attendance_for(self.student_b)

        visible = self.Attendance.with_user(self.teacher_b).search([])

        self.assertIn(attendance_b, visible)
        self.assertNotIn(attendance_a, visible)

    def test_manager_in_both_companies_sees_all_students(self):
        visible = self.Student.with_user(self.manager_both).search([])

        self.assertIn(self.student_a, visible)
        self.assertIn(self.student_b, visible)

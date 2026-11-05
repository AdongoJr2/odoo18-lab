from odoo.tests import TransactionCase


class TestAcademyDashboard(TransactionCase):
    def test_dashboard_kpis(self):
        course = self.env["academy.course"].create(
            {"name": "Dashboard Course", "capacity": 1}
        )
        student = self.env["academy.student"].create(
            {"name": "Dashboard Student", "course_id": course.id}
        )
        student.action_enroll()
        self.env["academy.attendance"].create(
            {"student_id": student.id, "status": "present"}
        )

        dashboard = self.env["academy.dashboard"].create({})

        students = self.env["academy.student"].search([])
        courses = self.env["academy.course"].search([])
        attendance = self.env["academy.attendance"].search([])
        present = attendance.filtered(lambda record: record.status == "present")

        self.assertEqual(dashboard.total_students, len(students))
        self.assertEqual(
            dashboard.enrolled_students,
            len(students.filtered(lambda s: s.state == "enrolled")),
        )
        self.assertEqual(dashboard.total_courses, len(courses))
        self.assertEqual(dashboard.full_courses, len(courses.filtered("is_full")))
        self.assertEqual(dashboard.attendance_records, len(attendance))
        expected_rate = len(present) / len(attendance) * 100 if attendance else 0
        self.assertAlmostEqual(dashboard.attendance_rate, expected_rate, places=1)

        self.assertIn(student, students)
        self.assertIn(course, courses)
        self.assertTrue(course.is_full)
        self.assertGreaterEqual(dashboard.full_courses, 1)

    def test_dashboard_actions_are_configured(self):
        dashboard = self.env["academy.dashboard"].create({})

        self.assertEqual(
            dashboard.action_open_students()["res_model"], "academy.student"
        )
        self.assertEqual(
            dashboard.action_open_attendance()["res_model"], "academy.attendance"
        )
        self.assertEqual(
            dashboard.action_open_attendance_analysis()["res_model"],
            "academy.attendance",
        )

    def test_owl_dashboard_client_action_is_registered(self):
        action = self.env.ref("academy_management.academy_dashboard_client_action")
        self.assertEqual(action.tag, "academy_management.dashboard")
        self.assertEqual(action.type, "ir.actions.client")

    def test_attendance_analysis_view_has_graph_and_pivot(self):
        action = self.env.ref("academy_management.academy_attendance_analysis_action")
        self.assertEqual(action.view_mode, "graph,pivot,list")

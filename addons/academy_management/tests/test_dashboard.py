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

        self.assertEqual(dashboard.total_students, 1)
        self.assertEqual(dashboard.enrolled_students, 1)
        self.assertEqual(dashboard.total_courses, 1)
        self.assertEqual(dashboard.full_courses, 1)
        self.assertEqual(dashboard.attendance_records, 1)
        self.assertEqual(dashboard.attendance_rate, 100)

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

    def test_attendance_analysis_view_has_graph_and_pivot(self):
        action = self.env.ref("academy_management.academy_attendance_analysis_action")
        self.assertEqual(action.view_mode, "graph,pivot,list")

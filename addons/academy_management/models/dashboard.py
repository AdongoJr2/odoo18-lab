from odoo import api, fields, models


class AcademyDashboard(models.Model):
    _name = "academy.dashboard"
    _description = "Academy Dashboard"

    name = fields.Char(default="Academy Overview", required=True)
    total_students = fields.Integer(compute="_compute_kpis")
    enrolled_students = fields.Integer(compute="_compute_kpis")
    total_courses = fields.Integer(compute="_compute_kpis")
    full_courses = fields.Integer(compute="_compute_kpis")
    attendance_records = fields.Integer(compute="_compute_kpis")
    attendance_rate = fields.Float(compute="_compute_kpis", digits=(16, 1))

    @api.depends_context("uid")
    def _compute_kpis(self):
        students = self.env["academy.student"].search([])
        courses = self.env["academy.course"].search([])
        attendance = self.env["academy.attendance"].search([])
        present = len(attendance.filtered(lambda record: record.status == "present"))
        for dashboard in self:
            dashboard.total_students = len(students)
            dashboard.enrolled_students = len(
                students.filtered(lambda student: student.state == "enrolled")
            )
            dashboard.total_courses = len(courses)
            dashboard.full_courses = len(courses.filtered("is_full"))
            dashboard.attendance_records = len(attendance)
            dashboard.attendance_rate = (
                present / len(attendance) * 100 if attendance else 0
            )

    def action_open_students(self):
        return self.env.ref("academy_management.academy_student_action").read()[0]

    def action_open_courses(self):
        return self.env.ref("academy_management.academy_course_action").read()[0]

    def action_open_attendance(self):
        return self.env.ref("academy_management.academy_attendance_action").read()[0]

    def action_open_attendance_analysis(self):
        return self.env.ref(
            "academy_management.academy_attendance_analysis_action"
        ).read()[0]

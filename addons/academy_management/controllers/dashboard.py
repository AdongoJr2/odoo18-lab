from odoo import http
from odoo.exceptions import AccessError
from odoo.http import request


class AcademyDashboardController(http.Controller):
    @http.route(
        "/academy_management/statistics",
        type="json",
        auth="user",
    )
    def statistics(self):
        if not (
            request.env.user.has_group("academy_management.group_academy_manager")
            or request.env.user.has_group("academy_management.group_academy_teacher")
        ):
            raise AccessError("Only academy staff can view dashboard statistics.")

        students = request.env["academy.student"].search([])
        courses = request.env["academy.course"].search([], order="name", limit=5)
        attendance = request.env["academy.attendance"].search([])
        present = len(attendance.filtered(lambda record: record.status == "present"))
        return {
            "total_students": len(students),
            "enrolled_students": len(
                students.filtered(lambda student: student.state == "enrolled")
            ),
            "total_courses": request.env["academy.course"].search_count([]),
            "full_courses": len(
                request.env["academy.course"].search([]).filtered("is_full")
            ),
            "attendance_records": len(attendance),
            "attendance_rate": present / len(attendance) * 100 if attendance else 0,
            "courses": [
                {
                    "id": course.id,
                    "name": course.name,
                    "enrolled": course.enrolled_student_count,
                    "capacity": course.capacity,
                }
                for course in courses
            ],
        }

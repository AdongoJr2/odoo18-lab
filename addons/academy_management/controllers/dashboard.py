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
        course_products = request.env["academy.course"].search([]).mapped("product_id")
        invoices = request.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("company_id", "=", request.env.company.id),
                ("invoice_line_ids.product_id", "in", course_products.ids),
            ]
        )
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
            "finance": {
                "invoiced": sum(invoices.mapped("amount_total")),
                "posted": sum(
                    invoices.filtered(lambda invoice: invoice.state == "posted").mapped(
                        "amount_total"
                    )
                ),
                "paid": sum(
                    invoices.filtered(
                        lambda invoice: invoice.payment_state == "paid"
                    ).mapped("amount_total")
                ),
                "outstanding": sum(invoices.mapped("amount_residual")),
                "currency": request.env.company.currency_id.symbol,
            },
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

from odoo import http
from odoo.http import request


class AcademyWebsiteController(http.Controller):
    @http.route("/academy", type="http", auth="public", website=True)
    def academy_home(self):
        courses = (
            request.env["academy.course"]
            .sudo()
            .search([("active", "=", True)], order="name")
        )
        return request.render(
            "academy_management.academy_website_home",
            {"courses": courses},
        )

    @http.route("/academy/courses", type="http", auth="public", website=True)
    def academy_courses(self):
        courses = (
            request.env["academy.course"]
            .sudo()
            .search([("active", "=", True)], order="name")
        )
        return request.render(
            "academy_management.academy_website_courses",
            {"courses": courses},
        )

    @http.route(
        "/academy/course/<int:course_id>",
        type="http",
        auth="public",
        website=True,
    )
    def academy_course(self, course_id, **kwargs):
        course = request.env["academy.course"].sudo().browse(course_id).exists()
        if not course or not course.active:
            return request.not_found()
        return request.render(
            "academy_management.academy_website_course_detail",
            {"course": course, "error": kwargs.get("error")},
        )

    @http.route(
        "/academy/course/<int:course_id>/enroll",
        type="http",
        auth="public",
        website=True,
        methods=["POST"],
    )
    def academy_enroll(self, course_id, **post):
        course = request.env["academy.course"].sudo().browse(course_id).exists()
        if not course or not course.active:
            return request.not_found()
        if course.is_full:
            return request.redirect(f"/academy/course/{course.id}?error=full")

        name = (post.get("name") or "").strip()
        email = (post.get("email") or "").strip().lower()
        if not name or not email:
            return request.redirect(f"/academy/course/{course.id}?error=required")

        students = request.env["academy.student"].sudo()
        if students.search_count(
            [
                ("course_id", "=", course.id),
                ("email", "=", email),
                ("state", "not in", ["dropped"]),
            ]
        ):
            return request.redirect(f"/academy/course/{course.id}?error=duplicate")

        partner = (
            request.env["res.partner"].sudo().search([("email", "=", email)], limit=1)
        )
        if not partner:
            partner = (
                request.env["res.partner"]
                .sudo()
                .create({"name": name, "email": email, "phone": post.get("phone")})
            )

        student = students.create(
            {
                "name": name,
                "email": email,
                "phone": post.get("phone"),
                "course_id": course.id,
            }
        )
        order = (
            request.env["sale.order"]
            .sudo()
            .create(
                {
                    "partner_id": partner.id,
                    "require_payment": True,
                    "prepayment_percent": 1.0,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "product_id": course.product_id.id,
                                "product_uom_qty": 1,
                                "price_unit": course.price,
                            },
                        )
                    ],
                }
            )
        )
        student.sale_order_id = order
        lead = (
            request.env["crm.lead"]
            .sudo()
            .create(
                {
                    "name": f"Course enrollment: {course.name}",
                    "type": "opportunity",
                    "partner_id": partner.id,
                    "contact_name": name,
                    "email_from": email,
                    "phone": post.get("phone"),
                    "course_id": course.id,
                    "student_id": student.id,
                    "sale_order_id": order.id,
                }
            )
        )
        student.crm_lead_id = lead
        payment_link = (
            request.env["payment.link.wizard"]
            .sudo()
            .create(
                {
                    "res_model": "sale.order",
                    "res_id": order.id,
                    **order._get_default_payment_link_values(),
                }
            )
            .link
        )
        return request.render(
            "academy_management.academy_website_enrollment_success",
            {"student": student, "course": course, "payment_link": payment_link},
        )

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

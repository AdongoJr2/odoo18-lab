from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        result = super().action_confirm()
        students = self.env["academy.student"].search(
            [("sale_order_id", "in", self.ids)]
        )
        students.filtered(lambda student: student.state == "draft").action_enroll()
        return result

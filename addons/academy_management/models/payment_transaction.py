from odoo import models


class AcademyPaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _post_process(self):
        result = super()._post_process()
        for transaction in self.filtered(lambda tx: tx.state == "done"):
            students = self.env["academy.student"].search(
                [("sale_order_id", "in", transaction.sale_order_ids.ids)]
            )
            students.filtered(lambda student: student.state == "draft").action_enroll()
            students.mapped("crm_lead_id").write(
                {
                    "stage_id": self.env.ref(
                        "academy_management.crm_stage_academy_enrolled"
                    ).id
                }
            )
        return result

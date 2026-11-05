from odoo import fields, models


class AcademyCrmLead(models.Model):
    _inherit = "crm.lead"

    course_id = fields.Many2one(
        comodel_name="academy.course",
        string="Academy Course",
        index=True,
    )
    student_id = fields.Many2one(
        comodel_name="academy.student",
        string="Academy Student",
        index=True,
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Enrollment Quotation",
        readonly=True,
    )

    def action_open_academy_student(self):
        self.ensure_one()
        return self.student_id.get_formview_action() if self.student_id else False

    def action_open_academy_course(self):
        self.ensure_one()
        return self.course_id.get_formview_action() if self.course_id else False

    def action_open_enrollment_order(self):
        self.ensure_one()
        return self.sale_order_id.get_formview_action() if self.sale_order_id else False

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

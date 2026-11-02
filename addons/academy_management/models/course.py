from odoo import models, fields


class AcademyCourse(models.Model):
    _name = 'academy.course'
    _description = 'Academy Course'
    _order = 'name'

    name = fields.Char(
        string='Course Name',
        required=True,
    )

    student_ids = fields.One2many(
        comodel_name='academy.student',
        inverse_name='course_id',
        string='Students',
    )

    description = fields.Text(
        string='Description',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

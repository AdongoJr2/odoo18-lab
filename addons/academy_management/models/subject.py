from odoo import fields, models


class AcademySubject(models.Model):
    _name = "academy.subject"
    _description = "Academy Subject"
    _order = "name"

    name = fields.Char(
        string="Subject Name",
        required=True,
    )

    student_ids = fields.Many2many(
        comodel_name="academy.student",
        relation="academy_student_subject_rel",
        column1="subject_id",
        column2="student_id",
        string="Students",
    )

    description = fields.Text(
        string="Description",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

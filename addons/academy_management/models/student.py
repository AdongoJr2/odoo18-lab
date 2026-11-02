from odoo import models, fields, api
from odoo.exceptions import UserError

class AcademyStudent(models.Model):
    _name = 'academy.student'
    _description = 'Academy Student'
    _order = 'name'

    _sql_constraints = [
        (
            'student_id_unique',
            'UNIQUE(student_id)',
            'Student registration numbers must be unique.',
        ),
    ]

    student_id = fields.Char(
        string='Registration Number',
        required=True,
        readonly=True,
        copy=False,
        default='New',
        index=True,
    )

    course_id = fields.Many2one(
        comodel_name='academy.course',
        string='Course',
        ondelete='restrict',
    )

    subject_ids = fields.Many2many(
        comodel_name='academy.subject',
        relation='academy_student_subject_rel',
        column1='student_id',
        column2='subject_id',
        string='Subjects',
    )

    name = fields.Char(
        string='Student Name',
        required=True,
        index=True,
    )

    email = fields.Char(
        string='Email Address',
    )

    phone = fields.Char(
        string='Phone Number',
    )

    date_of_birth = fields.Date(
        string='Date of Birth',
    )

    age = fields.Integer(
        string='Age',
        compute='_compute_age',
    )

    gender = fields.Selection(
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
        string='Gender',
    )

    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()

        for student in self:
            if student.date_of_birth:
                student.age = (
                    today.year - student.date_of_birth.year
                    - (
                        (today.month, today.day)
                        < (
                            student.date_of_birth.month,
                            student.date_of_birth.day,
                        )
                    )
                )
            else:
                student.age = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('student_id', 'New') == 'New':
                sequence = (
                    self.env['ir.sequence'].next_by_code('academy.student')
                    or 'New'
                )

                if not sequence:
                    raise UserError(
                        'The student registration sequence is not configured'
                    )

                vals['student_id'] = sequence

        return super().create(vals_list)


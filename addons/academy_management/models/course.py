from odoo import api, fields, models


class AcademyCourse(models.Model):
    _name = "academy.course"
    _description = "Academy Course"
    _order = "name"

    name = fields.Char(
        string="Course Name",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    capacity = fields.Integer(
        string="Capacity",
        default=30,
        help="Maximum number of students allowed in this course.",
    )

    student_ids = fields.One2many(
        comodel_name="academy.student",
        inverse_name="course_id",
        string="Students",
    )

    student_count = fields.Integer(
        string="Student Count",
        compute="_compute_student_count",
        store=True,
    )

    enrolled_student_count = fields.Integer(
        string="Enrolled Students",
        compute="_compute_enrolled_student_count",
        store=True,
    )

    is_full = fields.Boolean(
        string="Is Full",
        compute="_compute_is_full",
        store=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.depends("student_ids")
    def _compute_student_count(self):
        for course in self:
            course.student_count = len(course.student_ids)

    @api.depends("student_ids.state")
    def _compute_enrolled_student_count(self):
        for course in self:
            course.enrolled_student_count = len(
                course.student_ids.filtered(lambda student: student.state == "enrolled")
            )

    @api.depends("enrolled_student_count", "capacity")
    def _compute_is_full(self):
        for course in self:
            course.is_full = (
                course.capacity > 0 and course.enrolled_student_count >= course.capacity
            )

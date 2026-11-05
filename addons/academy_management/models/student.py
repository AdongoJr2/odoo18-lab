from odoo import api, fields, models
from odoo.exceptions import UserError


class AcademyStudent(models.Model):
    _name = "academy.student"
    _description = "Academy Student"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "student_id_unique",
            "UNIQUE(student_id)",
            "Student registration numbers must be unique.",
        ),
    ]

    student_id = fields.Char(
        string="Registration Number",
        required=True,
        readonly=True,
        copy=False,
        default="New",
        index=True,
    )

    course_id = fields.Many2one(
        comodel_name="academy.course",
        string="Course",
        ondelete="restrict",
        tracking=True,
    )

    subject_ids = fields.Many2many(
        comodel_name="academy.subject",
        relation="academy_student_subject_rel",
        column1="student_id",
        column2="subject_id",
        string="Subjects",
    )

    name = fields.Char(
        string="Student Name",
        required=True,
        index=True,
        tracking=True,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Portal User",
        help="Internal user who owns this student profile.",
        ondelete="set null",
        groups="academy_management.group_academy_manager",
    )

    email = fields.Char(
        string="Email Address",
    )

    phone = fields.Char(
        string="Phone Number",
    )

    date_of_birth = fields.Date(
        string="Date of Birth",
    )

    age = fields.Integer(
        string="Age",
        compute="_compute_age",
    )

    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("enrolled", "Enrolled"),
            ("graduated", "Graduated"),
            ("dropped", "Dropped"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Enrollment Quotation",
        readonly=True,
        copy=False,
    )

    @api.depends("date_of_birth")
    def _compute_age(self):
        today = fields.Date.today()

        for student in self:
            if student.date_of_birth:
                student.age = (
                    today.year
                    - student.date_of_birth.year
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
            if vals.get("student_id", "New") == "New":
                sequence_model = self.env["ir.sequence"]
                sequence = sequence_model.next_by_code("academy.student") or "New"
                while self.search_count([("student_id", "=", sequence)]):
                    sequence = sequence_model.next_by_code("academy.student") or "New"

                if not sequence:
                    raise UserError(
                        "The student registration sequence is not configured"
                    )

                vals["student_id"] = sequence

        return super().create(vals_list)

    def action_enroll(self):
        """Enroll the student in their assigned course."""
        for student in self:
            if not student.course_id:
                raise UserError("Please assign a course before enrolling.")
            enrolled_count = self.search_count(
                [
                    ("course_id", "=", student.course_id.id),
                    ("state", "=", "enrolled"),
                    ("id", "!=", student.id),
                ]
            )
            if (
                student.course_id.capacity > 0
                and enrolled_count >= student.course_id.capacity
            ):
                raise UserError("This course is full. Cannot enroll more students.")
            student.state = "enrolled"

    def action_graduate(self):
        """Mark the student as graduated."""
        for student in self:
            if student.state != "enrolled":
                raise UserError("Only enrolled students can graduate.")
            student.state = "graduated"

    def action_drop(self):
        """Mark the student as dropped."""
        for student in self:
            if student.state not in ("enrolled", "draft"):
                raise UserError("Only draft or enrolled students can be dropped.")
            student.state = "dropped"

    def action_reset_to_draft(self):
        """Reset student to draft state."""
        for student in self:
            student.state = "draft"

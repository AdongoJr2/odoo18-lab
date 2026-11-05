from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class AcademyAttendance(models.Model):
    _name = "academy.attendance"
    _description = "Academy Attendance"
    _order = "attendance_date desc, student_id"

    _sql_constraints = [
        (
            "attendance_unique",
            "UNIQUE(student_id, attendance_date)",
            "A student can only have one attendance record per day.",
        ),
    ]

    student_id = fields.Many2one(
        comodel_name="academy.student",
        string="Student",
        required=True,
        ondelete="cascade",
    )

    course_id = fields.Many2one(
        comodel_name="academy.course",
        string="Course",
        required=True,
        ondelete="restrict",
    )

    attendance_date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.today,
        index=True,
    )

    status = fields.Selection(
        selection=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("excused", "Excused"),
        ],
        string="Status",
        required=True,
        default="present",
    )

    notes = fields.Text(string="Notes")

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        related="student_id.company_id",
        store=True,
        readonly=True,
    )

    @api.constrains("student_id", "course_id")
    def _check_student_course(self):
        for attendance in self:
            if attendance.student_id.course_id != attendance.course_id:
                raise ValidationError(
                    "The attendance course must match the student's course."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if not values.get("course_id") and values.get("student_id"):
                student = self.env["academy.student"].browse(values["student_id"])
                if not student.course_id:
                    raise UserError("Attendance requires a student with a course.")
                values["course_id"] = student.course_id.id
        return super().create(vals_list)

    @api.onchange("student_id")
    def _onchange_student_id(self):
        if self.student_id.course_id:
            self.course_id = self.student_id.course_id

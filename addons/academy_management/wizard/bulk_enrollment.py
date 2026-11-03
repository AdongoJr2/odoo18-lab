from odoo import api, fields, models
from odoo.exceptions import UserError


class AcademyBulkEnrollment(models.TransientModel):
    _name = "academy.bulk.enrollment"
    _description = "Bulk Student Enrollment"

    course_id = fields.Many2one(
        comodel_name="academy.course",
        string="Course",
        required=True,
    )

    student_ids = fields.Many2many(
        comodel_name="academy.student",
        string="Students",
        required=True,
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if "student_ids" in fields_list:
            active_ids = self.env.context.get("active_ids", [])
            students = self.env["academy.student"].browse(active_ids).exists()
            values["student_ids"] = [(6, 0, students.ids)]
        return values

    def action_confirm(self):
        self.ensure_one()
        students = self.student_ids

        if not students:
            raise UserError("Select at least one student to enroll.")
        if any(student.state != "draft" for student in students):
            raise UserError("Only draft students can be enrolled in bulk.")

        available_capacity = (
            self.course_id.capacity - self.course_id.enrolled_student_count
        )
        if self.course_id.capacity > 0 and len(students) > available_capacity:
            raise UserError(
                "The selected students exceed the available course capacity."
            )

        students.write({"course_id": self.course_id.id, "state": "enrolled"})
        return {"type": "ir.actions.act_window_close"}

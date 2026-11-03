from odoo.tests import TransactionCase


class TestAcademyStudentReport(TransactionCase):
    def test_student_transcript_report_is_bound_to_student(self):
        report = self.env.ref("academy_management.action_report_student_transcript")
        self.assertEqual(report.model, "academy.student")
        self.assertEqual(report.report_type, "qweb-pdf")
        self.assertEqual(report.binding_model_id.model, "academy.student")

    def test_student_transcript_report_contains_student_data(self):
        student = self.env["academy.student"].create(
            {
                "name": "Transcript Student",
                "email": "transcript@example.com",
            }
        )
        report = self.env.ref("academy_management.action_report_student_transcript")
        html, _ = report._render_qweb_html(report.report_name, student.ids)
        rendered = html.decode() if isinstance(html, bytes) else html

        self.assertIn("Transcript Student", rendered)
        self.assertIn(student.student_id, rendered)
        self.assertIn("Student Transcript", rendered)

        pdf, _ = report._render_qweb_pdf(report.report_name, student.ids)
        self.assertTrue(pdf)

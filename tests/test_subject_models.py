from odoo.tests import TransactionCase


class TestAcademySubject(TransactionCase):
    def test_subject_creation(self):
        subject = self.env['academy.subject'].create({
            'name': 'Test Subject',
            'description': 'Test description',
        })
        self.assertTrue(subject.active)

    def test_subject_student_relationship(self):
        subject = self.env['academy.subject'].create({'name': 'Test Subject'})
        student = self.env['academy.student'].create({'name': 'Test Student'})
        student.write({'subject_ids': [(4, subject.id)]})
        self.assertIn(student, subject.student_ids)

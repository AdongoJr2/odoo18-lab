from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class TestAcademySecurity(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Student = self.env["academy.student"]
        self.manager_group = self.env.ref("academy_management.group_academy_manager")
        self.teacher_group = self.env.ref("academy_management.group_academy_teacher")
        self.student_group = self.env.ref("academy_management.group_academy_student")

    def _create_user(self, name, group):
        return (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": name,
                    "login": name.lower().replace(" ", "_"),
                    "email": f"{name.lower().replace(' ', '_')}@example.com",
                    "groups_id": [(6, 0, [group.id])],
                }
            )
        )

    def test_manager_can_read_all_students(self):
        manager = self._create_user("Academy Manager", self.manager_group)
        first = self.Student.create({"name": "First Student"})
        second = self.Student.create({"name": "Second Student"})

        visible = self.Student.with_user(manager).search([])

        self.assertIn(first, visible)
        self.assertIn(second, visible)

    def test_student_can_read_only_owned_profile(self):
        user = self._create_user("Academy Student", self.student_group)
        owned = self.Student.create({"name": "Owned Student", "user_id": user.id})
        other = self.Student.create({"name": "Other Student"})

        visible = self.Student.with_user(user).search([])

        self.assertIn(owned, visible)
        self.assertNotIn(other, visible)

    def test_student_cannot_modify_profile(self):
        user = self._create_user("Readonly Student", self.student_group)
        owned = self.Student.create({"name": "Owned Student", "user_id": user.id})

        with self.assertRaises(AccessError):
            self.Student.with_user(user).browse(owned.id).write({"phone": "555-0100"})

    def test_teacher_can_modify_but_not_delete(self):
        teacher = self._create_user("Academy Teacher", self.teacher_group)
        student = self.Student.create({"name": "Teacher Student"})

        self.Student.with_user(teacher).browse(student.id).write({"phone": "555-0100"})
        with self.assertRaises(AccessError):
            self.Student.with_user(teacher).browse(student.id).unlink()

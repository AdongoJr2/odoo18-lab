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

    def test_manager_implies_teacher_group(self):
        self.assertIn(self.teacher_group, self.manager_group.implied_ids)
        manager = self._create_user("Implied Manager", self.manager_group)
        self.assertIn(self.teacher_group, manager.groups_id)

    def test_portal_user_field_restricted_to_managers(self):
        teacher = self._create_user("Portal Teacher", self.teacher_group)
        student = self.Student.create({"name": "Portal Student"})

        with self.assertRaises(AccessError):
            self.Student.with_user(teacher).browse(student.id).write(
                {"user_id": teacher.id}
            )

    def test_student_cannot_read_portal_user_field(self):
        user = self._create_user("Own Portal User", self.student_group)
        owned = self.Student.create({"name": "Owned Portal", "user_id": user.id})

        with self.assertRaises(AccessError):
            self.Student.with_user(user).browse(owned.id).read(["user_id"])

    def test_bulk_enrollment_wizard_denied_for_students(self):
        user = self._create_user("Wizard Student", self.student_group)

        with self.assertRaises(AccessError):
            self.env["academy.bulk.enrollment"].with_user(user).create({})

    def test_academy_menu_hidden_without_academy_group(self):
        plain = self._create_user("Plain Employee", self.env.ref("base.group_user"))
        root = self.env.ref("academy_management.academy_management_menu_root")

        self.assertFalse(root.with_user(plain)._filter_visible_menus())

    def test_dashboard_menu_hidden_from_students(self):
        user = self._create_user("Dashboard Student", self.student_group)
        dashboard = self.env.ref("academy_management.academy_dashboard_menu")
        students_menu = self.env.ref("academy_management.academy_student_menu")

        self.assertFalse(dashboard.with_user(user)._filter_visible_menus())
        self.assertTrue(students_menu.with_user(user)._filter_visible_menus())

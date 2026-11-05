from odoo import fields
from odoo.tests import TransactionCase

COURSE_XML_IDS = (
    "academy_management.course_demo_python",
    "academy_management.course_demo_web",
    "academy_management.course_demo_data",
)

SUBJECT_XML_IDS = (
    "academy_management.subject_prog_basics",
    "academy_management.subject_web_fundamentals",
    "academy_management.subject_data_analysis",
    "academy_management.subject_databases",
)

ALL_XML_IDS = COURSE_XML_IDS + SUBJECT_XML_IDS

DEMO_STUDENTS = {
    "academy_management.student_demo_1": {
        "name": "Amina Yusuf",
        "email": "amina.yusuf@example.com",
        "phone": "+254700000001",
        "date_of_birth": "2001-03-12",
        "gender": "female",
        "course": "academy_management.course_demo_python",
        "state": "enrolled",
    },
    "academy_management.student_demo_2": {
        "name": "Brian Okello",
        "email": "brian.okello@example.com",
        "phone": "+254700000002",
        "date_of_birth": "2000-07-25",
        "gender": "male",
        "course": "academy_management.course_demo_web",
        "state": "enrolled",
    },
    "academy_management.student_demo_3": {
        "name": "Chloe Martin",
        "email": "chloe.martin@example.com",
        "phone": "+254700000003",
        "date_of_birth": "2002-01-08",
        "gender": "female",
        "course": "academy_management.course_demo_data",
        "state": "enrolled",
    },
    "academy_management.student_demo_4": {
        "name": "Daniel Kim",
        "email": "daniel.kim@example.com",
        "phone": "+254700000004",
        "date_of_birth": "1999-11-30",
        "gender": "male",
        "course": "academy_management.course_demo_python",
        "state": "enrolled",
    },
    "academy_management.student_demo_5": {
        "name": "Elise Fontaine",
        "email": "elise.fontaine@example.com",
        "phone": "+254700000005",
        "date_of_birth": "2001-09-17",
        "gender": "other",
        "course": None,
        "state": "draft",
    },
}


class TestAcademyMasterData(TransactionCase):
    """Master seed data loaded from data/academy_data.xml."""

    def test_master_courses_loaded(self):
        for xml_id in COURSE_XML_IDS:
            with self.subTest(xml_id=xml_id):
                course = self.env.ref(xml_id)
                self.assertEqual(course._name, "academy.course")
                self.assertTrue(course.name)
                self.assertTrue(course.active)

    def test_master_subjects_loaded(self):
        for xml_id in SUBJECT_XML_IDS:
            with self.subTest(xml_id=xml_id):
                subject = self.env.ref(xml_id)
                self.assertEqual(subject._name, "academy.subject")
                self.assertTrue(subject.name)
                self.assertTrue(subject.active)

    def test_course_field_values(self):
        course = self.env.ref("academy_management.course_demo_python")
        self.assertEqual(course.name, "Intro to Python")
        self.assertEqual(course.capacity, 25)
        self.assertIn("Python", course.description)

    def test_capacities_are_positive(self):
        for xml_id in COURSE_XML_IDS:
            with self.subTest(xml_id=xml_id):
                course = self.env.ref(xml_id)
                self.assertGreater(course.capacity, 0)

    def test_seed_records_are_noupdate(self):
        for xml_id in ALL_XML_IDS:
            with self.subTest(xml_id=xml_id):
                module, _, name = xml_id.partition(".")
                imd = (
                    self.env["ir.model.data"]
                    .sudo()
                    .search(
                        [("module", "=", module), ("name", "=", name)],
                        limit=2,
                    )
                )
                self.assertEqual(len(imd), 1)
                self.assertTrue(imd.noupdate)

    def test_no_duplicate_seed_records(self):
        for xml_id in ALL_XML_IDS:
            with self.subTest(xml_id=xml_id):
                record = self.env.ref(xml_id)
                matches = self.env[record._name].search([("name", "=", record.name)])
                self.assertEqual(len(matches), 1)

    def test_seed_names_are_unique(self):
        for model_xml_ids in (COURSE_XML_IDS, SUBJECT_XML_IDS):
            names = [self.env.ref(xml_id).name for xml_id in model_xml_ids]
            self.assertEqual(len(names), len(set(names)))

    def test_seed_courses_contain_only_demo_students(self):
        demo = {self.env.ref(xml_id) for xml_id in DEMO_STUDENTS}
        for xml_id in COURSE_XML_IDS:
            with self.subTest(xml_id=xml_id):
                course = self.env.ref(xml_id)
                self.assertTrue(all(s in demo for s in course.student_ids))
                self.assertEqual(
                    course.enrolled_student_count,
                    len(course.student_ids.filtered(lambda s: s.state == "enrolled")),
                )
                self.assertFalse(course.is_full)

    def test_seeds_visible_in_default_search(self):
        courses = self.env["academy.course"].search(
            [("name", "=", "Web Development Basics")]
        )
        subjects = self.env["academy.subject"].search([("name", "=", "Databases")])
        self.assertEqual(len(courses), 1)
        self.assertEqual(len(subjects), 1)

    def test_unknown_xml_id_raises(self):
        with self.assertRaises(ValueError):
            self.env.ref("academy_management.course_does_not_exist")


class TestAcademyDemoData(TransactionCase):
    """Demo students loaded from demo/academy.student.csv."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        names = [xml_id.partition(".")[2] for xml_id in DEMO_STUDENTS]
        found = (
            cls.env["ir.model.data"]
            .sudo()
            .search_count(
                [
                    ("module", "=", "academy_management"),
                    ("name", "in", names),
                ]
            )
        )
        cls.has_demo_data = found == len(names)

    def setUp(self):
        super().setUp()
        if not self.has_demo_data:
            self.skipTest("demo data not loaded (database installed without demo)")

    def test_demo_students_loaded(self):
        for xml_id in DEMO_STUDENTS:
            with self.subTest(xml_id=xml_id):
                student = self.env.ref(xml_id)
                self.assertEqual(student._name, "academy.student")
                self.assertTrue(student.active)

    def test_demo_student_field_values(self):
        for xml_id, expected in DEMO_STUDENTS.items():
            with self.subTest(xml_id=xml_id):
                student = self.env.ref(xml_id)
                self.assertEqual(student.name, expected["name"])
                self.assertEqual(student.email, expected["email"])
                self.assertEqual(student.phone, expected["phone"])
                self.assertEqual(student.gender, expected["gender"])
                self.assertEqual(
                    student.date_of_birth,
                    fields.Date.to_date(expected["date_of_birth"]),
                )

    def test_demo_student_states_and_courses(self):
        for xml_id, expected in DEMO_STUDENTS.items():
            with self.subTest(xml_id=xml_id):
                student = self.env.ref(xml_id)
                self.assertEqual(student.state, expected["state"])
                if expected["course"]:
                    self.assertEqual(
                        student.course_id, self.env.ref(expected["course"])
                    )
                else:
                    self.assertFalse(student.course_id)

    def test_demo_enrollments_respect_capacity(self):
        for xml_id in COURSE_XML_IDS:
            with self.subTest(xml_id=xml_id):
                course = self.env.ref(xml_id)
                self.assertLessEqual(course.enrolled_student_count, course.capacity)

    def test_demo_registration_numbers_use_sequence(self):
        numbers = [self.env.ref(xml_id).student_id for xml_id in DEMO_STUDENTS]
        for number in numbers:
            with self.subTest(student_id=number):
                self.assertRegex(number, r"^STU\d{4}$")
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_sequence_continues_after_demo_data(self):
        """New students must not collide with demo registration numbers."""
        demo_numbers = {self.env.ref(xml_id).student_id for xml_id in DEMO_STUDENTS}
        student = self.env["academy.student"].create({"name": "Post-Demo Student"})
        self.assertRegex(student.student_id, r"^STU\d{4}$")
        self.assertNotIn(student.student_id, demo_numbers)

    def test_demo_csv_records_are_noupdate(self):
        """Odoo's loader forces noupdate=True for CSV files.

        XML demo data can opt out with ``<data noupdate="0">`` (as Odoo
        core does), but CSV files cannot express the flag, so the
        loader always sets it for both demo and init CSV imports.
        """
        for xml_id in DEMO_STUDENTS:
            with self.subTest(xml_id=xml_id):
                module, _, name = xml_id.partition(".")
                imd = (
                    self.env["ir.model.data"]
                    .sudo()
                    .search(
                        [("module", "=", module), ("name", "=", name)],
                        limit=2,
                    )
                )
                self.assertEqual(len(imd), 1)
                self.assertTrue(imd.noupdate)

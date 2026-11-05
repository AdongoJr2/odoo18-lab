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

    def test_seed_courses_have_no_students(self):
        for xml_id in COURSE_XML_IDS:
            with self.subTest(xml_id=xml_id):
                course = self.env.ref(xml_id)
                self.assertEqual(course.student_count, 0)
                self.assertEqual(course.enrolled_student_count, 0)
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

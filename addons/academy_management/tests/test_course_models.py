from odoo.tests import TransactionCase


class TestAcademyCourse(TransactionCase):
    def test_course_creation(self):
        course = self.env["academy.course"].create(
            {
                "name": "New Course",
                "description": "Test description",
            }
        )
        self.assertTrue(course.active)
        self.assertEqual(course.name, "New Course")

    def test_course_student_relationship(self):
        course = self.env["academy.course"].create({"name": "Test Course"})
        student = self.env["academy.student"].create(
            {
                "name": "Test Student",
                "course_id": course.id,
            }
        )
        self.assertIn(student, course.student_ids)

    def test_course_creates_sellable_service_product(self):
        course = self.env["academy.course"].create(
            {"name": "Sales Course", "price": 250}
        )
        self.assertTrue(course.product_id)
        self.assertEqual(course.product_id.name, "Sales Course")
        self.assertEqual(course.product_id.type, "service")
        self.assertTrue(course.product_id.sale_ok)
        self.assertEqual(course.price, 250)

        course.name = "Updated Sales Course"
        self.assertEqual(course.product_id.name, "Updated Sales Course")

        sales_action = course.action_open_sales()
        self.assertEqual(sales_action["res_model"], "sale.order")
        self.assertIn(
            ("order_line.product_id", "=", course.product_id.id),
            sales_action["domain"],
        )

    def test_course_creates_customer_invoice(self):
        customer = self.env["res.partner"].create({"name": "Course Customer"})
        course = self.env["academy.course"].create(
            {
                "name": "Invoice Course",
                "price": 125,
                "customer_id": customer.id,
            }
        )
        action = course.action_create_invoice()
        invoice = self.env["account.move"].browse(action["res_id"])
        self.assertEqual(invoice.move_type, "out_invoice")
        self.assertEqual(invoice.partner_id, customer)
        self.assertEqual(invoice.invoice_line_ids.product_id, course.product_id)
        self.assertEqual(invoice.invoice_line_ids.price_unit, 125)

        course.action_post_invoice()
        self.assertEqual(invoice.state, "posted")
        course.action_register_invoice_payment()
        self.assertEqual(invoice.payment_state, "paid")

    def test_enrollment_order_confirmation_enrolls_student(self):
        course = self.env["academy.course"].create(
            {"name": "Confirmed Course", "price": 50}
        )
        student = self.env["academy.student"].create(
            {"name": "Quotation Student", "course_id": course.id}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.env.user.partner_id.id,
                "require_payment": True,
                "prepayment_percent": 1.0,
                "order_line": [
                    (
                        0,
                        0,
                        {"product_id": course.product_id.id, "product_uom_qty": 1},
                    )
                ],
            }
        )
        student.sale_order_id = order
        order.action_confirm()
        self.assertEqual(student.state, "enrolled")


class TestAcademyCourseComputedFields(TransactionCase):
    def test_student_count_computation(self):
        """Test that student_count is computed correctly."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        self.assertEqual(course.student_count, 0)

        self.env["academy.student"].create(
            {"name": "Student 1", "course_id": course.id}
        )
        self.env["academy.student"].create(
            {"name": "Student 2", "course_id": course.id}
        )
        self.assertEqual(course.student_count, 2)

    def test_is_full_computation(self):
        """Test that is_full is computed correctly."""
        course = self.env["academy.course"].create(
            {"name": "Test Course", "capacity": 2}
        )
        self.assertFalse(course.is_full)

        self.env["academy.student"].create(
            {"name": "Student 1", "course_id": course.id}
        )
        self.env["academy.student"].create(
            {"name": "Student 2", "course_id": course.id}
        )
        self.assertFalse(course.is_full)

        course.student_ids[:2].action_enroll()
        self.assertTrue(course.is_full)

    def test_capacity_default(self):
        """Test that capacity defaults to 30."""
        course = self.env["academy.course"].create({"name": "Test Course"})
        self.assertEqual(course.capacity, 30)

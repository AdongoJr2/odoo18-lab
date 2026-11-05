from odoo import api, fields, models


class AcademyCourse(models.Model):
    _name = "academy.course"
    _description = "Academy Course"
    _order = "name"

    name = fields.Char(
        string="Course Name",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    capacity = fields.Integer(
        string="Capacity",
        default=30,
        help="Maximum number of students allowed in this course.",
    )

    student_ids = fields.One2many(
        comodel_name="academy.student",
        inverse_name="course_id",
        string="Students",
    )

    student_count = fields.Integer(
        string="Student Count",
        compute="_compute_student_count",
        store=True,
    )

    enrolled_student_count = fields.Integer(
        string="Enrolled Students",
        compute="_compute_enrolled_student_count",
        store=True,
    )

    is_full = fields.Boolean(
        string="Is Full",
        compute="_compute_is_full",
        store=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Sellable Product",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )

    price = fields.Float(
        string="Course Price",
        related="product_id.list_price",
        readonly=False,
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Invoice Customer",
        help="Customer used when creating a course invoice.",
    )

    crm_lead_count = fields.Integer(
        string="Admissions Opportunities",
        compute="_compute_crm_lead_count",
    )

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Latest Invoice",
        compute="_compute_invoice_id",
        search="_search_invoice_id",
    )

    invoice_state = fields.Selection(
        related="invoice_id.state",
        string="Invoice Status",
        readonly=True,
    )

    invoice_payment_state = fields.Selection(
        related="invoice_id.payment_state",
        string="Payment Status",
        readonly=True,
    )

    @api.depends("student_ids")
    def _compute_student_count(self):
        for course in self:
            course.student_count = len(course.student_ids)

    @api.depends("student_ids.state")
    def _compute_enrolled_student_count(self):
        for course in self:
            course.enrolled_student_count = len(
                course.student_ids.filtered(lambda student: student.state == "enrolled")
            )

    @api.depends("enrolled_student_count", "capacity")
    def _compute_is_full(self):
        for course in self:
            course.is_full = (
                course.capacity > 0 and course.enrolled_student_count >= course.capacity
            )

    def _compute_crm_lead_count(self):
        counts = dict(
            self.env["crm.lead"].read_group(
                [("course_id", "in", self.ids)], ["course_id"], ["course_id"]
            )
        )
        for course in self:
            course.crm_lead_count = counts.get(course.id, 0)

    @api.model_create_multi
    def create(self, vals_list):
        courses = super().create(vals_list)
        courses._ensure_sellable_products()
        return courses

    def init(self):
        self.search([("product_id", "=", False)])._ensure_sellable_products()

    def _ensure_sellable_products(self):
        for course in self.filtered(lambda record: not record.product_id):
            course.product_id = self.env["product.product"].create(
                {
                    "name": course.name,
                    "type": "service",
                    "list_price": course.price or 0,
                    "sale_ok": True,
                    "purchase_ok": False,
                }
            )

    def write(self, vals):
        result = super().write(vals)
        if "name" in vals:
            self.mapped("product_id").write({"name": vals["name"]})
        return result

    def action_open_sales(self):
        self.ensure_one()
        action = self.env.ref("sale.action_orders").read()[0]
        action.pop("id", None)
        action["domain"] = [("order_line.product_id", "=", self.product_id.id)]
        return action

    def action_create_invoice(self):
        self.ensure_one()
        if not self.customer_id:
            return {
                "type": "ir.actions.act_window",
                "name": "Select Invoice Customer",
                "res_model": "academy.course",
                "view_mode": "form",
                "res_id": self.id,
                "target": "current",
            }
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product_id.id,
                            "quantity": 1,
                            "price_unit": self.price,
                        },
                    )
                ],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Course Invoice",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": invoice.id,
            "target": "current",
        }

    def _compute_invoice_id(self):
        invoices = self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("invoice_line_ids.product_id", "in", self.mapped("product_id").ids),
            ],
            order="invoice_date desc, id desc",
        )
        for course in self:
            course.invoice_id = invoices.filtered(
                lambda invoice: course.product_id in invoice.invoice_line_ids.product_id
            )[:1]

    def _search_invoice_id(self, operator, value):
        invoices = self.env["account.move"].search(
            [("id", operator, value)] if operator in ("=", "!=") else []
        )
        return [("product_id", "in", invoices.invoice_line_ids.product_id.ids)]

    def action_open_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            return self.action_create_invoice()
        return {
            "type": "ir.actions.act_window",
            "name": "Course Invoice",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
            "target": "current",
        }

    def action_post_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            self.action_create_invoice()
        if self.invoice_id.state == "draft":
            self.invoice_id.action_post()
        return self.action_open_invoice()

    def action_register_invoice_payment(self):
        self.ensure_one()
        if not self.invoice_id:
            self.action_create_invoice()
        if self.invoice_id.state == "draft":
            self.invoice_id.action_post()
        return (
            self.env["account.payment.register"]
            .with_context(
                active_model="account.move",
                active_ids=self.invoice_id.ids,
            )
            .create({})
            .action_create_payments()
        )

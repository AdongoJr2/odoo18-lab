{
    "name": "Academy Management",
    "version": "18.0.1.0.0",
    "summary": "Basic academy and school management",
    "description": """
        Academy Management
        ==================

        A custom Odoo module for managing academy operations.

        Features:
        - Student management
    """,
    "category": "Education",
    "author": "Moses Adongo",
    "license": "LGPL-3",
    "depends": [
        "account",
        "base",
        "crm",
        "mail",
        "product",
        "sale",
        "web",
        "website",
        "website_payment",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/student_sequence.xml",
        "data/academy_data.xml",
        "data/crm_data.xml",
        "views/student_views.xml",
        "views/course_views.xml",
        "views/subject_views.xml",
        "views/attendance_views.xml",
        "views/dashboard_views.xml",
        "wizard/bulk_enrollment_views.xml",
        "reports/student_transcript_templates.xml",
        "reports/student_transcript_reports.xml",
        "views/academy_website_templates.xml",
        "views/crm_lead_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "academy_management/static/src/js/dashboard.js",
            "academy_management/static/src/xml/dashboard.xml",
            "academy_management/static/src/scss/dashboard.scss",
            "academy_management/static/src/scss/academy_website.scss",
        ],
    },
    "demo": [
        "demo/academy.student.csv",
        "demo/academy_crm_leads.xml",
    ],
    "installable": True,
    "application": True,
}

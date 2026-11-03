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
    "depends": ["base", "web"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/student_sequence.xml",
        "views/student_views.xml",
        "views/course_views.xml",
        "views/subject_views.xml",
        "wizard/bulk_enrollment_views.xml",
        "reports/student_transcript_templates.xml",
        "reports/student_transcript_reports.xml",
    ],
    "installable": True,
    "application": True,
}

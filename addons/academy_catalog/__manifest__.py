{
    "name": "Academy Catalog (Data Module)",
    "version": "18.0.1.0.0",
    "summary": "XML-defined academy catalog example",
    "description": "An importable-style data module defined without Python models.",
    "category": "Education",
    "author": "Moses Adongo",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "models/catalog_course.xml",
        "security/ir.model.access.csv",
        "views/catalog_course_views.xml",
    ],
    "installable": True,
    "application": False,
}

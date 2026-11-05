# Academy Management for Odoo 18

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Odoo 18](https://img.shields.io/badge/Odoo-18.0-purple.svg)](https://www.odoo.com)
[![Tests](https://github.com/AdongoJr2/odoo18-lab/actions/workflows/test.yml/badge.svg)](https://github.com/AdongoJr2/odoo18-lab/actions/workflows/test.yml)

A custom Odoo 18 module for managing academy/school operations, paired with a
ready-to-run Docker Compose stack (PostgreSQL 16 + Odoo 18).

## Features

- **Student management** — registration numbers auto-generated (STU0001, ...),
  name, email, phone, date of birth, computed age, gender, active flag.
- **Course management** — courses with descriptions and enrolled students.
- **Enrollment workflow** — draft, enrolled, graduated, and dropped student states.
- **Course capacity** — computed student counts and enrollment blocking when a course is full.
- **Student transcripts** — printable QWeb PDF reports with enrollment and subject details.
- **Attendance tracking** — daily present, absent, late, and excused records with calendar and list views.
- **Academy dashboard** — student, enrollment, course-capacity, and attendance KPIs with drill-down actions.
- **Subject management** — subjects linked to students (many-to-many).
- **Seed & demo data** — master courses/subjects plus enrolled demo students for instant evaluation.
- **Role-based security** — Academy Manager, Academy Teacher, and Academy Student groups with ownership rules, menu/field restrictions, and multi-company siloing.
- **XML data module** — `academy_catalog` demonstrates an importable-style module with models, fields, defaults, views, and ACLs defined entirely in XML/CSV.

## Data model

| Model | Key fields |
|---|---|
| `academy.student` | `student_id` (unique), `name`, `email`, `phone`, `user_id` (managers only), `date_of_birth`, `age` (computed), `gender`, `state`, `active`, `company_id`, `course_id` (M2one), `subject_ids` (M2many) |
| `academy.course` | `name`, `description`, `capacity`, `student_count`, `is_full`, `active`, `student_ids` (O2many) |
| `academy.subject` | `name`, `description`, `active`, `student_ids` (M2many) |
| `academy.attendance` | `student_id`, `course_id`, `attendance_date`, `status`, `notes`, `company_id` (from student); unique per student and date |

## Prerequisites

- Docker & Docker Compose
- Python 3.10+ (for local development)
- Git, GitHub CLI for development

## Quick start

```bash
git clone https://github.com/AdongoJr2/odoo18-lab.git
cd odoo18-lab
docker compose up -d
```

Open http://localhost:8069, create a database, then install the
**Academy Management** app from the Apps menu.

Default master password is set in `config/odoo.conf` (`admin_passwd`).
Change it before exposing the instance publicly.

## Project layout

```
odoo18-lab/
├── addons/academy_management/   # custom Odoo addon
│   ├── __manifest__.py
│   ├── models/                  # student, course, subject
│   ├── views/                   # list & form views + menus
│   ├── security/                # access rights (CSV)
│   ├── data/                    # master seed data + student sequence
│   ├── demo/                    # demo students (CSV, install only)
│   ├── reports/                 # QWeb transcript report
│   ├── wizard/                  # bulk enrollment wizard
│   └── tests/                   # unit & integration tests
├── addons/academy_catalog/      # XML-only data module example
│   ├── models/                  # ir.model and ir.model.fields records
│   ├── views/                   # XML-defined model UI
│   ├── security/                # ACLs for the dynamic model
│   └── tests/                   # data-module tests
├── config/odoo.conf             # Odoo configuration
├── docker-compose.yml           # Postgres 16 + Odoo 18
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pyproject.toml              # Tool configuration
├── Makefile                    # Development commands
├── .gitignore
├── LICENSE                      # LGPL-3.0
└── README.md
```

## XML Data Modules

Tutorial 4 introduces importable-style modules that define Odoo models through
XML data instead of Python classes. The small `academy_catalog` addon is the
project's equivalent example:

- `models/catalog_course.xml` creates `x_academy.catalog.course` through an
  `ir.model` record, then defines its `x_` fields through `ir.model.fields`.
- `ir.default` records provide static defaults for capacity and active status.
- The manifest loads model definitions before ACLs and views, because XML data
  files are processed sequentially.
- `security/ir.model.access.csv` and `views/catalog_course_views.xml` work the
  same way as in a conventional Python module.

This approach is useful when a hosting environment accepts module archives but
does not allow custom Python deployment. Its tradeoffs are verbosity and
limited business logic: computed fields, constraints, dynamic defaults, and
complex workflows still belong in a normal Python module such as
`academy_management`.

Install and test it in Docker with:

```bash
docker compose exec odoo odoo -d odoo_test -i academy_catalog \
  --test-enable --test-tags /academy_catalog --stop-after-init --http-port=8099
```

## Development

The addon is mounted into the container at `/mnt/extra-addons`, so code changes
are picked up by restarting Odoo and upgrading the module.

**Upgrade via CLI** (recommended after changing models, views, security, or
data files — this syncs the PostgreSQL schema with the Python registry; skip it
and you get errors like `column academy_course.capacity does not exist`):

```bash
# Dev database
docker compose exec odoo odoo -d odoo18_dev --stop-after-init \
  --update=academy_management --http-port=8099

# Test database
docker compose exec odoo odoo -d odoo_test --stop-after-init \
  --update=academy_management --http-port=8099
```

`--http-port=8099` avoids clashing with the server already listening on 8069.
Restart the long-running server afterwards so it reloads the registry:

```bash
docker compose restart odoo
```

**Upgrade via UI**: `docker compose restart odoo`, then in Odoo:
Apps → Update Apps List → Upgrade "Academy Management".

Logs:

```bash
docker compose logs -f odoo
```

## Module data

The addon ships two kinds of data files, declared in `__manifest__.py`:

- **`data/academy_data.xml`** — master seed data (3 courses, 4 subjects) wrapped
  in `<data noupdate="1">` so upgrades never clobber local edits. Capacities use
  `eval="25"` to store integers instead of strings. Loaded on install *and*
  upgrade.
- **`demo/academy.student.csv`** — 5 demo students, 4 of them enrolled in seed
  courses. Loaded only when the database is created **with demo data** and only
  on install (never on upgrade).

Rules worth remembering for CSV data files:

- The filename must be the model name: `academy.student.csv` loads into
  `academy.student` (the loader does `filename.split('-')[0]`, so
  `academy.student-batch2.csv` also works). A name like `students_demo.csv`
  fails with `KeyError`.
- Many-to-one columns that reference records by XML ID need the `:id` suffix
  (`course_id:id`); without it the value is treated as a display name and
  looked up with `name_search`.
- The loader forces `noupdate=True` for CSV files (demo and init alike), since
  CSV cannot express the flag the way `<data noupdate="0">` can.
- Demo CSV rows omit `student_id`; the `create()` override assigns the next
  sequence number (STU0001, ...) so demo rows never collide with the sequence.

## Testing

### Run tests with Docker

Prefer focused runs while developing. The test file runner loads the current
Python code and executes only the requested files, without running unrelated
tests or updating the module:

```bash
# Fastest path for Python-only changes
make test-focused FILES="test_attendance.py test_student_models.py"

# Use this when module data, views, security records, or schema changed
make test-focused-update FILES="test_security.py"

# The same target can run the XML-only data module tests
make test-focused MODULE=academy_catalog FILES="test_catalog_course.py"
```

Relevant test files are grouped by area:

- `models/student.py`: `test_student_models.py`, `test_multi_company.py`,
  `test_security.py`, `test_wizards.py`, `test_reports.py`
- `models/course.py`: `test_course_models.py`, `test_data_files.py`,
  `test_dashboard.py`
- `models/attendance.py`: `test_attendance.py`, `test_multi_company.py`
- `models/subject.py`: `test_subject_models.py`, `test_data_files.py`
- `security/`: `test_security.py`, `test_multi_company.py`
- `wizard/`: `test_wizards.py`
- `report/`: `test_reports.py`
- `data/`, `demo/`, or `__manifest__.py`: `test_data_files.py` with a fresh
  install, because demo data is loaded only during installation

For a fresh database and the complete addon suite:

```bash
# Create a fresh test database
docker compose exec db psql -U odoo -d postgres -c \
  "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='odoo_test';"
docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo_test;"
docker compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo_test OWNER odoo;"

# Run Odoo tests (scoped to this addon to avoid base-module failures)
docker compose exec odoo odoo -d odoo_test --test-enable \
  --test-tags /academy_management --stop-after-init \
  --init=academy_management --http-port=8099
```

### Test coverage

- **Unit tests**: Student, Course, and Subject model tests
- **Integration tests**: End-to-end workflow verification
- **Data-file tests**: master seed data (XML) and demo student CSV integrity
- **Total**: 67 Odoo tests covering model creation, relationships, constraints, sequences, capacity, workflows, wizards, reports, security rules, multi-company rules, attendance, dashboard KPIs, and data files

### Student transcript

Select one or more students from the Students list, open **Print**, and choose
**Student Transcript**. Odoo generates a QWeb PDF containing the student's
registration details, status, course, and subjects.

### Security

The security model follows Odoo's layered approach (groups → ACLs → record
rules → visibility), mirroring the official *Restrict access to data* tutorial:

- **Groups** (`security/security.xml`) — *Academy Manager*, *Academy Teacher*,
  and *Academy Student*, all implying `base.group_user` and categorized under
  Education. The manager group implies the teacher group, so managers inherit
  every teacher-level rule and access right.
- **Access rights** (`security/ir.model.access.csv`) — managers get full CRUD;
  teachers get read/write/create but never delete; students get read-only
  access to students, courses, subjects, and their own attendance. The bulk
  enrollment wizard and dashboard are staff-only (students have no ACL).
- **Record rules** — teachers and managers see all students and attendance;
  students are limited to the profile linked to their user (and that profile's
  attendance). Two **global** multi-company rules additionally restrict
  `academy.student` and `academy.attendance` to the companies the current user
  belongs to (`company_id in company_ids`), so each branch/campus is siloed.
  Courses and subjects are intentionally **shared** across companies (catalog
  data, like products in Odoo's own multi-company apps).
- **Visibility ≠ security** — the Academy root menu requires one of the three
  groups (plain internal users see no Academy app at all), the Dashboard menu
  is staff-only, the Bulk Enroll action is staff-only, and the **Portal User**
  field is restricted to managers both in Python (`groups=` on the field) and
  in the form view. These hide UI elements but are not security boundaries;
  the ACLs and record rules above enforce actual access.
- **No security bypasses** — business code never calls `sudo()`; the wizard,
  reports, and workflow buttons all run with the caller's rights, so the ORM
  access checks apply everywhere.

After installing on a fresh database, add yourself to **Academy Manager**
(Settings → Users) to see the Academy app.

Assign a student's internal user through the **Portal User** field (managers
only). The student record rule then limits that user to their own profile.

### Attendance tracking

Open **Academy Management → Attendance** to record daily attendance. Each entry
must match the student's course, and duplicate entries for the same student and
date are rejected. Attendance is available in calendar, list, and form views.

### Dashboard

Open **Academy Management → Dashboard** for live KPI cards. The cards link to
the underlying Students, Courses, Attendance, and Attendance Analysis views.

## Linting

### Prerequisites

```bash
# Install development dependencies
pip install -r requirements-test.txt
```

### Run linting

```bash
# Using Makefile (recommended)
make lint

# Or manually
ruff check .                    # Fast Python linting
black --check .                 # Code formatting
isort --check .                 # Import sorting
mypy .                          # Type checking
```

### Auto-format code

```bash
make lint-fix
# Or manually
ruff check . --fix
black .
isort .
```

### Pre-commit hooks

```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## CI/CD

GitHub Actions automatically runs on every push to `main` and pull requests:

- **Linting**: ruff, black, isort, mypy
- **Python versions**: 3.10

Odoo tests run locally via Docker (see [Testing](#testing)); the Odoo image is
not pip-installable, so CI does not execute the test suite.

View workflow: [GitHub Actions](https://github.com/AdongoJr2/odoo18-lab/actions)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the GNU Lesser General Public License v3.0 — see
[LICENSE](LICENSE). The addon itself declares `LGPL-3` in its manifest.

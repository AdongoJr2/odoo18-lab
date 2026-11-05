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
- **Role-based security** — Academy Manager, Academy Teacher, and Academy Student groups with ownership rules.

## Data model

| Model | Key fields |
|---|---|
| `academy.student` | `student_id` (unique), `name`, `email`, `phone`, `user_id`, `date_of_birth`, `age` (computed), `gender`, `state`, `active`, `course_id` (M2one), `subject_ids` (M2many) |
| `academy.course` | `name`, `description`, `capacity`, `student_count`, `is_full`, `active`, `student_ids` (O2many) |
| `academy.subject` | `name`, `description`, `active`, `student_ids` (M2many) |
| `academy.attendance` | `student_id`, `course_id`, `attendance_date`, `status`, `notes`; unique per student and date |

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
│   ├── data/                    # student sequence
│   ├── reports/                 # QWeb transcript report
│   ├── wizard/                  # bulk enrollment wizard
│   └── tests/                   # unit & integration tests
├── config/odoo.conf             # Odoo configuration
├── docker-compose.yml           # Postgres 16 + Odoo 18
├── .pre-commit-config.yaml     # Pre-commit hooks
├── pyproject.toml              # Tool configuration
├── Makefile                    # Development commands
├── .gitignore
├── LICENSE                      # LGPL-3.0
└── README.md
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

## Testing

### Run tests with Docker

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
- **Total**: 41 Odoo tests covering model creation, relationships, constraints, sequences, capacity, workflows, wizards, reports, security rules, attendance, and dashboard KPIs

### Student transcript

Select one or more students from the Students list, open **Print**, and choose
**Student Transcript**. Odoo generates a QWeb PDF containing the student's
registration details, status, course, and subjects.

### Security roles

- **Academy Manager** — full student, course, subject, and wizard access.
- **Academy Teacher** — read/write access without deleting core records.
- **Academy Student** — read-only access to the student profile linked to their user.

Assign a student's internal user through the **Portal User** field. The student
record rule then limits that user to their own profile.

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

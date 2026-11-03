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
- **Subject management** — subjects linked to students (many-to-many).
- **Access control** — full CRUD for internal users (`base.group_user`).

## Data model

| Model | Key fields |
|---|---|
| `academy.student` | `student_id` (unique), `name`, `email`, `phone`, `date_of_birth`, `age` (computed), `gender`, `state`, `active`, `course_id` (M2one), `subject_ids` (M2many) |
| `academy.course` | `name`, `description`, `capacity`, `student_count`, `is_full`, `active`, `student_ids` (O2many) |
| `academy.subject` | `name`, `description`, `active`, `student_ids` (M2many) |

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
are picked up after restarting Odoo or updating the module:

```bash
docker compose restart odoo
# then in Odoo: Apps → Update Apps List → Upgrade "Academy Management"
```

Logs:

```bash
docker compose logs -f odoo
```

## Testing

### Run tests with Docker

```bash
# Create a fresh test database
docker compose exec db psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS odoo_test;"
docker compose exec db psql -U odoo -d postgres -c "CREATE DATABASE odoo_test OWNER odoo;"

# Run Odoo tests
docker compose exec odoo odoo -d odoo_test --test-enable --stop-after-init \
  --init=academy_management --http-port=8099
```

### Test coverage

- **Unit tests**: Student, Course, and Subject model tests
- **Integration tests**: End-to-end workflow verification
- **Total**: 22 Odoo tests covering model creation, relationships, constraints, sequences, capacity, and workflow transitions

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
- **Testing**: Odoo test suite with PostgreSQL service
- **Python versions**: 3.10

View workflow: [GitHub Actions](https://github.com/AdongoJr2/odoo18-lab/actions)

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the GNU Lesser General Public License v3.0 — see
[LICENSE](LICENSE). The addon itself declares `LGPL-3` in its manifest.
EOF
echo "README updated"

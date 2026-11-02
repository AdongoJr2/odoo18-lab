# Academy Management for Odoo 18

[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](LICENSE)
[![Odoo 18](https://img.shields.io/badge/Odoo-18.0-purple.svg)](https://www.odoo.com)

A custom Odoo 18 module for managing academy/school operations, paired with a
ready-to-run Docker Compose stack (PostgreSQL 16 + Odoo 18).

## Features

- **Student management** — registration numbers auto-generated (STU0001, ...),
  name, email, phone, date of birth, computed age, gender, active flag.
- **Course management** — courses with descriptions and enrolled students.
- **Subject management** — subjects linked to students (many-to-many).
- **Access control** — full CRUD for internal users (`base.group_user`).

## Data model

| Model | Key fields |
|---|---|
| `academy.student` | `student_id` (unique), `name`, `email`, `phone`, `date_of_birth`, `age` (computed), `gender`, `active`, `course_id` (M2one), `subject_ids` (M2many) |
| `academy.course` | `name`, `description`, `active`, `student_ids` (O2many) |
| `academy.subject` | `name`, `description`, `active`, `student_ids` (M2many) |

## Prerequisites

- Docker & Docker Compose
- (Optional) Git, GitHub CLI for development

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
│   └── data/                    # student sequence
├── config/odoo.conf             # Odoo configuration
├── docker-compose.yml           # Postgres 16 + Odoo 18
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

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and
follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the GNU Lesser General Public License v3.0 — see
[LICENSE](LICENSE). The addon itself declares `LGPL-3` in its manifest.

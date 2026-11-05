/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

export class AcademyDashboard extends Component {
    static template = "academy_management.AcademyDashboard";

    setup() {
        this.action = useService("action");
        this.state = useState({ loading: true, error: false, statistics: null });
        onWillStart(async () => {
            try {
                this.state.statistics = await rpc("/academy_management/statistics");
            } catch {
                this.state.error = true;
            } finally {
                this.state.loading = false;
            }
        });
    }

    openStudents() {
        this.action.doAction("academy_management.academy_student_action");
    }

    openCourses() {
        this.action.doAction("academy_management.academy_course_action");
    }

    openAttendance() {
        this.action.doAction("academy_management.academy_attendance_action");
    }
}

registry.category("actions").add("academy_management.dashboard", AcademyDashboard);

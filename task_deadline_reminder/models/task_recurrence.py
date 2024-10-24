from odoo import api, models, fields
from datetime import datetime, timedelta


class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    def _create_next_task(self):
        for recurrence in self:
            task = max(recurrence.sudo().task_ids, key=lambda t: t.id)
            deadline_days = task.deadline_days_count

            create_values = recurrence._new_task_values(task)
            create_values['deadline_days_count'] = deadline_days

            new_task = self.env['project.task'].sudo().create(create_values)
            new_task.date_deadline = new_task.create_date.date()

            if deadline_days:
                new_task.date_deadline = new_task.create_date.date() + timedelta(days=deadline_days)

            recurrence._create_subtasks(task, new_task, depth=3)

# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError

class TimesheetEntry(models.Model):
    _name = 'sh.start.timesheet'
    _description = 'Timesheet Start'

    def _get_employee(self):
        employee = self.env['hr.employee'].sudo().search(
            [('user_id', '=', self.env.user.id)], limit=1)
        if employee:
            return employee

    project_id = fields.Many2one(
        'project.project', string="Project", required=False)
    task_id = fields.Many2one('project.task', string="Task",
                              domain="[('project_id','=',project_id)]")
    start_date = fields.Datetime(
        "Start Date", default=lambda self: fields.datetime.now(), readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', required=True, default=_get_employee)

    def button_start_task(self):
        if not self.employee_id:
            raise UserError("Only Employee can start task !")
        if not self.task_id:
            raise UserError("Please Select Task !")
        self.task_id.action_task_start()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

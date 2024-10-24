# Copyright (C) Softhealer Technologies.

from odoo import models, fields
from datetime import datetime
from odoo.exceptions import ValidationError
class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    start_date = fields.Datetime("Start Time", readonly=True)
    end_date = fields.Datetime("End Time", readonly=True)

        
    def auto_end_task_timer(self):
        # return
        users = self.env['res.users'].search([('task_id', '!=', False)])
        auto_time = float(self.env['ir.config_parameter'].sudo().get_param('sh_task_time_adv.auto_time', default=1.0))
        # print('---------------autotime----------',auto_time, type(auto_time))
        for user in users:
            task_name = user.task_id.name

            user.sudo().write({'end_time': datetime.now()})

            task = user.task_id
            duration = 0.0
            if user.start_time and user.end_time:
                duration = (user.end_time - user.start_time).total_seconds() / 3600.0
                
                if auto_time and duration > auto_time:
                    if user.work_email:
                        self.auto_end_task_mail(user.name, user.work_email)
                    vals = {
                    'name': 'Task Ended Auto',
                    'unit_amount': duration,
                    'amount': duration,
                    'end_date': user.end_time,
                    'task_id': task.id,
                    }

                    if task.project_id:
                        vals.update({'project_id': task.project_id.id})
                        analytic_account = task.project_id.analytic_account_id
                        if analytic_account:
                            vals.update({'account_id': analytic_account.id})

                    timesheet_lines = self.env['account.analytic.line'].search([
                        ('task_id', '=', task.id),
                        ('end_date', '=', False)
                    ])

                    for timesheet_line in timesheet_lines:
                        timesheet_line.sudo().write(vals)

                    task.sudo().write({
                        'task_running': False,
                    })

                    # raise ValidationError(auto_time)
                    self.sudo()._cr.commit()
                    user.sudo().write({'task_id': False})

                else:
                    return
                
    def auto_end_task_mail(self, user, email):
        subject = "Alert! Your Task Timer has ended automatically."
        body_html = f"""\
                  <p>Hi <strong>{user}</strong>,</p>
                  <p>The task timer has ended automatically. If you are still working, please restart it.</p>
                  """

        mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': 'support@technians.com',
                'email_to': email,
                'reply_to': email
            }

        self.env['mail.mail'].create(mail_values).send()

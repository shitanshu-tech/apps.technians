from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = 'project.task'
    deadline_days_count = fields.Integer(string="No. of days",help="This will set the deadline of Recurring task for N days later from the date of creation")
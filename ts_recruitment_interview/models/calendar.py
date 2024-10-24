from odoo import fields, models

class CalendarEvent(models.Model):

    _inherit = 'calendar.event'

    interview_id = fields.Many2one('hr.interview', string="Interview", index='btree_not_null', ondelete='set null')

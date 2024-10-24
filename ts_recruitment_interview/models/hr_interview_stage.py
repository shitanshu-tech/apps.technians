from odoo import fields, models, api
from odoo.exceptions import ValidationError

# class InterviewTaskType(models.Model):
#     _name = 'interview.task.type'
#
#     name = fields.Char(string='Stage Name', required=True)
#     user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, required=True,
#                               help="The user who owns this stage")
#     sequence = fields.Integer(string='Sequence', default=10)
class InterviewStage(models.Model):
    _name = "hr.interview.stage"
    _description = "Interview Stages"
    _order = 'sequence'

    name = fields.Char("Stage Name", required=True)
    sequence = fields.Integer(
        "Sequence", default=10)
    job_ids = fields.Many2many(
        'hr.job', string='Job Specific',
        help='Specific jobs that uses this stage. Other jobs will not use this stage.')

    is_default = fields.Boolean(string='Scheduled')
    # is_held = fields.Boolean(string='Held')
    is_shortlisted = fields.Boolean(string='Shortlisted')
    is_rejected = fields.Boolean(string='Rejected')
    is_cancelled = fields.Boolean(string='Cancelled')

    @api.model
    def create(self, vals):
        if sum([vals.get('is_default', False), vals.get('is_shortlisted', False), vals.get('is_cancelled', False)]) > 1:
            raise ValidationError("Only one of 'Draft', 'Held', or 'Cancelled' can be set to True for a Stage!!")
        res = super(InterviewStage, self).create(vals)
        if vals.get('is_default', False):
            self.search([('is_default', '=', True), ('id', '!=', res.id)]).write({'is_default': False})
        if vals.get('is_shortlisted', False):
            self.search([('is_shortlisted', '=', True), ('id', '!=', res.id)]).write({'is_shortlisted': False})
        if vals.get('is_rejected', False):
            self.search([('is_rejected', '=', True), ('id', '!=', res.id)]).write({'is_rejected': False})
        if vals.get('is_cancelled', False):
            self.search([('is_cancelled', '=', True), ('id', '!=', res.id)]).write({'is_cancelled': False})
        return res
        
    def write(self, vals):
        if vals.get('is_default', False):
            self.search([('is_default', '=', True)]).write({'is_default': False})
        if vals.get('is_shortlisted', False):
            self.search([('is_shortlisted', '=', True)]).write({'is_shortlisted': False})
        if vals.get('is_rejected', False):
            self.search([('is_rejected', '=', True)]).write({'is_rejected': False})
        if vals.get('is_cancelled', False):
            self.search([('is_cancelled', '=', True)]).write({'is_cancelled': False})
        return super(InterviewStage, self).write(vals)

from odoo import models, fields, api

class Job(models.Model):
    _inherit = 'hr.job'

    # skill_ids =  fields.One2many('hr.skill', 'job_id', string='Skill')

    job_skill_ids = fields.One2many('hr.job.skill', 'job_id', string="Skills")
    # skill_ids = fields.Many2many('hr.skill', compute='_compute_skill_ids', store=True)
    #
    # @api.depends('job_skill_ids.skill_id')
    # def _compute_skill_ids(self):
    #     for job in self:
    #         job.skill_ids = job.job_skill_ids.skill_id

from odoo import models, fields, api

class HrJobChannel(models.Model):
    _name = 'hr.job.course'

    job_id = fields.Many2one(
        comodel_name='hr.job',
        required=True,
        ondelete='cascade')

    course_id = fields.Many2one(comodel_name='slide.channel', string='Courses')

    subject_ids = fields.Many2many(comodel_name='slide.slide', string='Subject')


class Job(models.Model):
    _inherit = 'hr.job'

    job_skill_ids = fields.One2many('hr.job.skill', 'job_id', string="Skills")

    job_course_ids = fields.One2many('hr.job.course', 'job_id', string="Course")



    # def schedule_interview(self):
    #     for job in self:
    #
    #         job_vals = {
    #             'job_id': job.id,
    #             'interviewer_ids': job.interviewer_ids.ids,
    #             'recruiter_id': job.user_id.id,
    #         }
    #
    #         interview = self.env['hr.interview'].create(job_vals)
    #
    #         for job_skill in job.job_skill_ids:
    #             self.env['hr.interview.skill'].create({
    #                 'applicant_id': interview.id,
    #                 'skill_id': job_skill.skill_id.id,
    #                 'skill_level_id': job_skill.skill_level_id.id,
    #                 'skill_type_id': job_skill.skill_type_id.id,
    #             })
    #
    #         return {
    #             'name': "Schedule an Interview",
    #             'type': 'ir.actions.act_window',
    #             'view_mode': 'form',
    #             'res_model': 'hr.interview',
    #             'res_id': interview.id,
    #             'target': 'new',
    #         }


    # def schedule_interview(self):
    #     # print('print context', self.env.context['params']['id'])
    #
    #     job = self.env['hr.job'].browse(self.env.context['params']['id'])
    #     job_vals = {
    #         'job_id': job.id,
    #         'interviewer_ids': job.interviewer_ids.ids,
    #         'recruiter_id': job.user_id,
    #     }
    #     form = self.env['hr.interview'].create(job_vals)
    #
    #     job_skills = self.env['hr.job.skill'].search([('job_id', '=', self.job_id.id)])
    #
    #     for job_skill in job_skills:
    #         self.env['hr.interview.skill'].create({
    #             'applicant_id': self.id,
    #             'skill_id': job_skill.skill_id.id,
    #             'skill_level_id': job_skill.skill_level_id.id,
    #             'skill_type_id': job_skill.skill_type_id.id,
    #         })
    #
    #     return {
    #         'name': "Schedule an Interview",
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'hr.interview',
    #         'res_id': form.id,
    #         'target': 'new',
    #     }

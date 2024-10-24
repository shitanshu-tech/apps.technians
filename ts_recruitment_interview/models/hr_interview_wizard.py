from datetime import timedelta

from odoo import api, fields, models


class HrInterviewWizard(models.Model):
    _name = 'hr.interview.wizard'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Interview Wizard"

    name = fields.Many2one(
        string='Applicant name',
        comodel_name='hr.applicant',
        # required=True,
        # store=True
    )
    job_id = fields.Many2one(
        string="Job Position",
        comodel_name='hr.job',
        required=True)
    interviewer_id = fields.Many2one(
        comodel_name='res.users',
        string="Interviewer",
        required=True,
        domain="[('share', '=', False)]"
    )
    recruiter_id = fields.Many2one(
        comodel_name='res.users',
        string="Recruiter",
        required=True,
        domain="[('share', '=', False)]"
    )
    time_in = fields.Datetime(string='Interview Start', required=True)
    duration = fields.Float(string='Duration (HH:MM)', required=True, default=0.5)
    time_out = fields.Datetime(string='Interview End', compute='_compute_time_out')
    hr_note = fields.Text(string='HR Note')
    # feedback = fields.Text(string='Feedback')

    applicant_skill_ids = fields.One2many('hr.interview.skill', 'wizard_id', string="Skills", ondelete='cascade')
    interview_question_ids = fields.One2many('hr.interview.questions', 'wizard_id', ondelete='cascade')

    attachment_ids = fields.Many2many(comodel_name='ir.attachment')

    _sql_constraints = [
        ('check_time_out_after_time_in_wizard',
         'CHECK(time_out > time_in)',
         'Interview End must be after Interview Start.')
    ]

    @api.depends('time_in', 'duration')
    def _compute_time_out(self):
        for interview in self:
            if interview.time_in:
                interview.time_out = interview.time_in + timedelta(hours=interview.duration)
            else:
                interview.time_out = False

    def _get_duration(self, start, stop):
        if not start or not stop:
            return 0
        duration = (stop - start).total_seconds() / 3600
        return round(duration, 2)


    def create_interviews(self):
        self.ensure_one()
        interviewer = self.interviewer_id
        vals = {
            'name': self.name.id,
            'job_id': self.job_id.id,
            'interviewer_id': interviewer.id,
            'recruiter_id': self.recruiter_id.id,
            'time_in': self.time_in,
            'duration': self.duration,
            'time_out': self.time_out,
            'hr_note': self.hr_note,
            'applicant_skill_ids': [
                (0, 0, {
                    'skill_id': skill.skill_id.id,
                    'skill_level_id': skill.skill_level_id.id,
                    'skill_type_id': skill.skill_type_id.id,
                })
                for skill in self.applicant_skill_ids
            ],
            'interview_question_ids': [
                (0, 0, {
                    'name': question.name.id,
                })
                for question in self.interview_question_ids
            ],
        }

        interview = self.env['hr.interview'].create(vals)
        if interview:
            applicant_stage = self.env['hr.recruitment.stage'].search([('name','ilike','interview')], limit=1)
            interview.name.stage_id = applicant_stage.id if applicant_stage else False

        if self.attachment_ids:
            for attachment in self.attachment_ids:
                attachment.copy({'res_model': 'hr.interview', 'res_id': interview.id})

        return interview

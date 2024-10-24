from odoo import models, fields, api
from odoo.exceptions import ValidationError

class HRApplicant(models.Model):
    _inherit = "hr.applicant"

    interview_ids = fields.One2many('hr.interview', 'name')
    interview_count = fields.Integer(compute='_compute_interview_count')

    def name_get(self):
        res = []
        for rec in self:
            name = rec.partner_name
            res.append((rec.id, name))
        return res

    def schedule_interview(self):
        for record in self:
            project_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_interview.project_id', default=False))
            if project_id == 0:
                raise ValidationError("Please select a Project for Task in Recruitment Settings")
            elif record.job_id:
                job = record.job_id
                context = {
                    'default_name': record.id,
                    'default_job_id': job.id,
                    # 'default_interviewer_ids': record.interviewer_ids.ids,
                    'default_recruiter_id': record.user_id.id,
                    'default_applicant_skill_ids': [
                        (0, 0, {
                            'skill_id': job_skill.skill_id.id,
                            'skill_level_id': job_skill.skill_level_id.id,
                            'skill_type_id': job_skill.skill_type_id.id,
                        })
                        for job_skill in job.job_skill_ids
                    ],
                }

                subject_ids = job.job_course_ids.subject_ids.ids
                if subject_ids:
                    subjects = self.env['slide.slide'].search([('id','in',subject_ids)])

                    context.update({
                        'default_interview_question_ids': [
                            (0, 0, {
                                'name': subject.id,
                            })
                            for subject in subjects
                        ],
                    })

                attachments = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', record.id)])
                context.update({
                    'default_attachment_ids': [(6, 0, attachments.ids)],
                })

                log_notes = self.env['mail.message'].search([
                    ('model', '=', 'hr.applicant'),
                    ('res_id', '=', record.id),
                    ('message_type', '=', 'comment')
                ])

                log_data = ''
                for note in log_notes:
                    log_data += f"[{note.create_date.date()}]  [{note.author_id.name if note.author_id else 'Unknown'}]\n {note.preview}\n"
                if log_data:
                    context.update({
                            'default_hr_note': log_data
                        })

                return {
                    'name': "Schedule an Interview",
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'hr.interview.wizard',
                    'target': 'new',
                    'context': context,
                }
            else:
                raise ValidationError('Select a Job Position to Schedule an Interview!!')


    @api.depends('interview_ids')
    def _compute_interview_count(self):
        for record in self:
            scheduled_interviews = self.env['hr.interview'].search_count([('name','=',record.id)])
            record.interview_count = scheduled_interviews

    def display_interview_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interviews',
            'view_mode': 'tree,form',
            'res_model': 'hr.interview',
            # 'search_view_id': 858,
            'context': {
                'search_default_name': self.id,
            },
        }

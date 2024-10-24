from odoo import api, fields, models, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    interview_id = fields.Many2one('hr.interview')


class HrInterview(models.Model):
    _name = 'hr.interview'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Interview of applicant"
    _order = 'create_date desc'

    name = fields.Many2one(
        string='Applicant name',
        comodel_name='hr.applicant',
        required=True,
        store=True,)
    job_id = fields.Many2one(
        string="Job Position",
        comodel_name='hr.job',
        required=True,
        ondelete='cascade')
    # interviewer_ids = fields.Many2many(related='job_id.interviewer_ids', required=True, store=True)
    # recruiter_id = fields.Many2one(related='job_id.user_id')
    interviewer_id = fields.Many2one(
        comodel_name='res.users',
        string="Interviewer",
        required=True,
        domain="[('share', '=', False)]"
        # default=lambda self: self._default_interviewers()
    )
    recruiter_id = fields.Many2one(
        comodel_name='res.users',
        string="Recruiter",
        required=True,
        domain="[('share', '=', False)]"
        # default=lambda self: self._default_recruiter()
    )
    time_in = fields.Datetime(string='Interview Start',required=True)
    duration = fields.Float(string='Duration (HH:MM)', readline=True, required=True, default=0.5)
    time_out = fields.Datetime(string='Interview End')
    feedback = fields.Text(string='Feedback')
    hr_note = fields.Text(string='HR Note')

    # stage_id = fields.Many2one(related='job_id.stage_id')

    applicant_skill_ids = fields.One2many('hr.interview.skill', 'applicant_id', string="Skills")

    interview_question_ids = fields.One2many('hr.interview.questions', 'interview_id')

    # shortlisted = fields.Boolean(string='Shortlisted')

    stage_id = fields.Many2one('hr.interview.stage', 'Stage', tracking=True,
                               compute='_compute_stage',
                               store=True,
                               readonly=False,
                               domain="['|', ('job_ids', '=', False), ('job_ids', '=', job_id)]",
                               copy=False,
                               group_expand='_group_expand_stages',
                               index=True,)
    is_stage_held = fields.Boolean(string='Is Stage Held', compute='_compute_is_stage_held', store=True)

    is_stage_shortlisted = fields.Boolean(related='stage_id.is_shortlisted', store=True)
    is_stage_rejected = fields.Boolean(related='stage_id.is_rejected', store=True)
    is_stage_cancelled = fields.Boolean(related='stage_id.is_cancelled', store=True)

    meeting_ids = fields.One2many('calendar.event', 'interview_id', string='Interview Meetings')

    active = fields.Boolean(default=True)

    # is_default = fields.Boolean(string='Default', default=True)
    # is_held = fields.Boolean(string='Held')
    # is_cancelled = fields.Boolean(string='Cancelled')

    # task_id = fields.Many2one('project.task')

    # user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    # personal_stage_id = fields.Many2one(
    #     'interview.task.type',
    #     domain="[('user_id', '=', uid)]",
    #     # required=True,
    #     ondelete='cascade',
    #     group_expand='_group_expand_stages',
    #     default=lambda self: self._default_personal_stage_id())

    _sql_constraints = [
        ('check_time_out_after_time_in',
         'CHECK(time_out > time_in)',
         'Interview End must be after Interview Start.')
    ]

    def _group_expand_stages(self, stages, domain, order):
        return self.env['hr.interview.stage'].search([])

    # @api.model
    # def _default_personal_stage_id(self):
    #     personal_stage = self.env['interview.task.type'].search([('user_id', '=', self.env.user.id)], order='sequence ASC', limit=1)
    #     return personal_stage.id if personal_stage else False

    # @api.model
    # def _get_default_personal_stage_create_vals(self, user_id):
    #     return [
    #         {'sequence': 1, 'name': _('Inbox'), 'user_id': user_id},
    #         {'sequence': 2, 'name': _('Today'), 'user_id': user_id},
    #         {'sequence': 3, 'name': _('This Week'), 'user_id': user_id},
    #         {'sequence': 4, 'name': _('This Month'), 'user_id': user_id},
    #         {'sequence': 5, 'name': _('Done'), 'user_id': user_id},
    #         {'sequence': 6, 'name': _('Canceled'), 'user_id': user_id},
    #     ]
    #
    # def _populate_missing_personal_stages(self):
    #     user_id = self.env.uid
    #     personal_stages = self.env['interview.task.type'].sudo().search([('user_id','=',user_id)])
    #     if not personal_stages:
    #         self.env['interview.task.type'].sudo().create(self._get_default_personal_stage_create_vals(user_id))

    # @api.model
    # def _default_interviewers(self):
    #     if self.job_id and self.job_id.interviewer_ids:
    #         return self.job_id.interviewer_ids
    #     return False
    #
    # @api.model
    # def _default_recruiter(self):
    #     if self.job_id and self.job_id.user_id:
    #         return self.job_id.user_id
    #     return False



    @api.depends('stage_id')
    def _compute_is_stage_held(self):
        for record in self:
            if record.stage_id and record.stage_id.is_shortlisted:
                record.is_stage_held = record.stage_id.is_shortlisted or False
            elif record.stage_id and record.stage_id.is_rejected:
                record.is_stage_held = record.stage_id.is_rejected or False
            elif record.stage_id and record.stage_id.is_cancelled:
                record.is_stage_held = record.stage_id.is_cancelled or False
            elif record.stage_id:
                record.is_stage_held = record.stage_id.is_shortlisted or False


    @api.depends('time_in','duration')
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

    def mark_shortlisted(self):
        for record in self:
            record.set_stage(search_stage='is_shortlisted')

    def mark_rejected(self):
        for record in self:
            record.set_stage(search_stage='is_rejected')

    def set_stage(self, search_stage):
        if self.time_in > datetime.now():
            raise ValidationError(_("Interview cannot be marked before Interview Start Time!!"))
        stages = self.env['hr.interview.stage'].search([])
        if stages:
            duration = self.duration
            # interviewers = record.interviewer_ids
            # for interviewer in interviewers:
            #     if interviewer.employee_id.id and record.task_id.id:
            # unfound_employees = []

            tasks = self.env['project.task'].search([('interview_id', '=', self.id)])
            # print('taskkkkkkkkkkkkkkkkkkkkkkkkk',tasks)
            for task in tasks:

                assignees = task.user_ids
                for assignee in assignees:
                    if assignee.employee_id.id:
                        existing_timesheet = self.env['account.analytic.line'].search([('task_id', '=', task.id),
                                                                                       ('date', '=', self.time_in),
                                                                                       ('employee_id', '=',
                                                                                        assignee.employee_id.id)])
                        if not existing_timesheet:
                            timesheet = {
                                'name': 'Interview Meeting Task ',
                                'unit_amount': duration,
                                'amount': duration,
                                'date': self.time_in,
                                'employee_id': assignee.employee_id.id,
                                'task_id': task.id,
                            }
                            if hasattr(existing_timesheet, 'start_date') and hasattr(existing_timesheet, 'end_date'):
                                timesheet.update({
                                    'start_date': self.time_in,
                                    'end_date': self.time_out,
                                })
                            self.env['account.analytic.line'].sudo().create(timesheet)
                    # else:
                    #     unfound_employees.append(assignee.name)

            questions = self.interview_question_ids
            for question in questions:
                if not question.rating or question.rating == '0':
                    question.unlink()

            stage_set = self.env['hr.interview.stage'].search([(search_stage, '=', True)], limit=1)
            self.stage_id = stage_set
            # self.active = False

            # if unfound_employees:
            #     # record.notify(unfound_employees)
            #     return{
            #         'type': 'ir.actions.client',
            #         'tag': 'display_notification',
            #         'params':{
            #             'title': 'Warning!!',
            #             'message': f"Employee does not exists for User(s) {', '.join(unfound_employees)}",
            #             'sticky': False,
            #         }
            #     }

        else:
            raise ValidationError(_('Create Interview Stages from Configuration first!!'))



    def mark_cancelled(self):
        for record in self:
            stages = self.env['hr.interview.stage'].search([])
            if stages:
                is_cancelled_stage = self.env['hr.interview.stage'].search([('is_cancelled','=',True)], limit=1)
                record.stage_id = is_cancelled_stage
            else:
                raise ValidationError(_('Create Interview Stages from Configuration first!!'))

    @api.depends('job_id')
    def _compute_stage(self):
        for applicant in self:
            # if not applicant.active:
            #     shortlisted_stage = self.env['hr.interview.stage'].search([('is_shortlisted','=',True)], limit=1)
            #     applicant.stage_id = shortlisted_stage
            if applicant.job_id:
                if not applicant.stage_id:
                    stage = self.env['hr.interview.stage'].search([
                        ('is_default','=',True),
                        '|',
                        ('job_ids', '=', False),
                        ('job_ids', '=', applicant.job_id.id),
                    ], limit=1).id
                    applicant.stage_id = stage if stage else False
            else:
                applicant.stage_id = False


    @api.model
    def create(self, vals_list):
        # self._populate_missing_personal_stages()
        res = super(HrInterview, self).create(vals_list)
        # res._populate_missing_personal_stages()
        # print('----------------',vals_list['recruiter_id'])

        project_id = int(self.env['ir.config_parameter'].sudo().get_param('ts_recruitment_interview.project_id', default=False))
        # print('-------------project',project_id,type(project_id))
        interviewer = res.interviewer_id
        # unfound_employees = []

        if project_id:
            task = {
                'name': f"Interview | {res.name.partner_name} | {res.job_id.name} | {interviewer.name}",
                'project_id': project_id, # or 4, #id for INTERNAL project
                'user_ids': [interviewer.id],
                'interview_id': res.id,
            }
            self.env['project.task'].sudo().create(task)

        #     else:
        #         unfound_employees.append(interviewer.name)
        #
        # if unfound_employees:
        #     res.notify(unfound_employees)

        calendar = {
            'interview_id': res.id,
            'name': f"Interview | {res.name.partner_name} | {res.job_id.name} | {interviewer.name}",
            'user_id': self.env.uid,
            'start': res.time_in or False,
            'stop': res.time_out or res.time_in + timedelta(hours=res.duration) or False,
            # 'partner_ids': [interviewer.partner_id.id],
            'partner_ids': [(6, 0, [interviewer.partner_id.id])],
        }
        self.env['calendar.event'].sudo().create(calendar)

        # self.move_attachment(res)

        # interviewers_in_applicant = self.env['hr.applicant'].search([('id','=',res.name.id)],limit=1).interviewer_ids
        # existing_interviewers = interviewers_in_applicant.ids or []
        # existing_interviewers.append(interviewer.id)
        # res.name.interviewer_ids = existing_interviewers

        inters = self.env['hr.interview'].search([('name','=',res.name.id)])
        existing_interviewers = []
        for inter in inters:
            if inter.interviewer_id.id and inter.interviewer_id.id not in existing_interviewers:
                existing_interviewers.append(inter.interviewer_id.id)
            # print('ooooooooooooooooooooooooooooooo',existing_interviewers)
        res.name.interviewer_ids = existing_interviewers
        return res
        # self.env['calendar.event'].sudo().with_context(default_applicant_id=applicant.id).create({


    # def notify(self,unfound_employees):
    #     print('---------------------------------------notify-called------------------------------------------')
    #     return{
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params':{
    #             'title': 'Warning!!',
    #             'message': f"Employee does not exists for User(s) {', '.join(unfound_employees)}",
    #             'sticky': False,
    #         }
    #     }

    # def move_attachment(self,res):
    #     attachments = self.env['ir.attachment'].search([('res_model', '=', 'hr.applicant'), ('res_id', '=', res.name.id)])
    #     for attachment in attachments:
    #         attachment.copy({
    #             'res_model': 'hr.interview',
    #             'res_id': res.id
    #         })



    # def write(self, vals):
    #     if vals.get('is_default', False):
    #         vals.update({'is_held': False, 'is_cancelled': False})
    #     elif vals.get('is_held', False):
    #         vals.update({'is_default': False, 'is_cancelled': False})
    #     elif vals.get('is_cancelled', False):
    #         vals.update({'is_default': False, 'is_held': False})
    #     elif 'is_held' in vals and not vals.get('is_held'):
    #         vals.update({'is_default': True})
    #     elif 'is_cancelled' in vals and not vals.get('is_cancelled'):
    #         vals.update({'is_default': True})
    #     return super(HrInterview, self).write(vals)

from odoo import fields, models, api


class UserExit(models.TransientModel):
    _name = "user.exit"
    _description = "Remove User from Task, Project, Courses, Teams"

    user_id = fields.Many2one('res.users', string='User', readonly=True)
    # Replacement fields
    task_replacement_user_id = fields.Many2one('res.users', string="Task Replacement User",
                                               help="Select a user to replace the exiting user in tasks")
    project_replacement_user_id = fields.Many2one('res.users', string="Project Replacement User",
                                                  help="Select a user to replace the exiting user in projects")
    course_replacement_user_id = fields.Many2one('res.users', string="Course Replacement User",
                                                 help="Select a user to replace the exiting user in courses")
    team_replacement_user_id = fields.Many2one('res.users', string="Team Replacement User",
                                               help="Select a user to replace the exiting user in teams")
    remove_from_task = fields.Boolean(string='Remove from Tasks', default=True)
    remove_from_project = fields.Boolean(string='Remove from Projects', default=True)
    remove_from_course = fields.Boolean(string='Remove from Courses', default=True)
    remove_from_project_team = fields.Boolean(string='Remove from Teams', default=True)
    task_count = fields.Integer(string='Tasks', compute='_compute_user_tasks')
    # project_count = fields.Integer(string='Projects', compute='_compute_user_projects')
    course_count = fields.Integer(string='Courses', compute='_compute_user_courses')
    team_count = fields.Integer(string='Teams', compute='_compute_user_teams')
    project_manager_count = fields.Integer(string="Project(PM)", compute='_compute_project_manager_count')
    account_manager_count = fields.Integer(string="Project(AM)", compute='_compute_account_manager_count')
    follower_count = fields.Integer(string="Project(Follower)", compute='_compute_follower_count')

    archive_user = fields.Boolean(string="Archive Employee", help="Archive the employee when they exit")


    @api.depends('user_id')
    def _compute_project_manager_count(self):
        for record in self:
            stage_ids = self.env['project.project.stage'].search([('fold', '=', False)]).ids

            # Count where the user is the project manager
            projects_as_manager = self.env['project.project'].search(
                [('user_id', '=', record.user_id.id), ('stage_id', 'in', stage_ids)])
            record.project_manager_count = len(projects_as_manager)

    @api.depends('user_id')
    def _compute_account_manager_count(self):
        for record in self:
            stage_ids = self.env['project.project.stage'].search([('fold', '=', False)]).ids

            projects_as_account_manager = self.env['project.project'].search(
                [('account_manager_id', '=', record.user_id.id), ('stage_id', 'in', stage_ids)])
            record.account_manager_count = len(projects_as_account_manager)

    @api.depends('user_id')
    def _compute_follower_count(self):
        for record in self:
            stage_ids = self.env['project.project.stage'].search([('fold', '=', False)]).ids

            follower_projects = self.env['project.project'].search(
                [('message_follower_ids.partner_id', '=', record.user_id.partner_id.id), ('stage_id', 'in', stage_ids)]
            )
            record.follower_count = len(follower_projects)

    # thissis the end of now date

    @api.depends('user_id')
    def _compute_user_tasks(self):
        for record in self:
            stage_ids = self.env['project.task.type'].search([('fold', '=', False)]).ids
            tasks = self.env['project.task'].search(
                [('user_ids', 'in', record.user_id.id), ('stage_id', 'in', stage_ids)])
            follower_tasks = self.env['project.task'].search(
                [('message_follower_ids.partner_id', '=', record.user_id.partner_id.id)]
            )
            record.task_count = len(tasks) + len(follower_tasks)

    @api.depends('user_id')
    def _compute_user_courses(self):
        for record in self:
            owned_courses = self.env['slide.channel'].search([('user_id', '=', record.user_id.id)])
            follower_courses = self.env['slide.channel'].search(
                [('message_follower_ids.partner_id', '=', record.user_id.partner_id.id)]
            )
            record.course_count = len(owned_courses) + len(follower_courses)

    @api.depends('user_id')
    def _compute_user_teams(self):
        for record in self:
            teams = self.env['project.team.technians'].search(['|', '|',
                                                               ('team_member_ids', 'in', record.user_id.id),
                                                               ('account_manager_id', '=', record.user_id.id),
                                                               ('project_manager_id', '=', record.user_id.id)])
            record.team_count = len(teams)

    def exit_user(self):
        self.ensure_one()
        user = self.user_id

        # Handle tasks
        if self.remove_from_task:
            stage_ids = self.env['project.task.type'].search([('fold', '=', False)]).ids
            tasks = self.env['project.task'].search([('user_ids', 'in', user.id), ('stage_id', 'in', stage_ids)])
            for task in tasks:
                task.user_ids = [(3, user.id)]  # Remove user from task
                if self.task_replacement_user_id:
                    task.user_ids = [(4, self.task_replacement_user_id.id)]  # Add replacement user

            follower_tasks = self.env['mail.followers'].search([('res_model', '=', 'project.task'),
                                                                ('partner_id', '=', user.partner_id.id)])
            follower_tasks.unlink()

        # Handle projects
        if self.remove_from_project:
            stage_ids = self.env['project.project.stage'].search([('fold', '=', False)]).ids

            projects = self.env['project.project'].search(
                [('stage_id', 'in', stage_ids), '|', ('user_id', '=', user.id),
                 ('account_manager_id', '=', user.id)])
            for project in projects:
                if project.account_manager_id == user:
                    project.write({
                        'account_manager_id': self.project_replacement_user_id.id if self.project_replacement_user_id else False})
                if project.user_id == user:
                    project.write(
                        {'user_id': self.project_replacement_user_id.id if self.project_replacement_user_id else False})

            follower_projects = self.env['mail.followers'].search([('res_model', '=', 'project.project'),
                                                                   ('partner_id', '=', user.partner_id.id)])
            follower_projects.unlink()

        # Handle courses
        if self.remove_from_course:
            courses = self.env['slide.channel'].search([('user_id', '=', user.id)])
            for course in courses:
                if course.user_id == user:
                    course.write(
                        {'user_id': self.course_replacement_user_id.id if self.course_replacement_user_id else False})

            follower_courses = self.env['mail.followers'].search([('res_model', '=', 'slide.channel'),
                                                                  ('partner_id', '=', user.partner_id.id)])
            follower_courses.unlink()

        # Handle teams
        if self.remove_from_project_team:
            project_teams = self.env['project.team.technians'].search([('team_member_ids', 'in', user.id)])
            for team in project_teams:
                if user.id in team.team_member_ids.ids:
                    new_team_member_ids = team.team_member_ids - user
                    team.write({'team_member_ids': [(6, 0, new_team_member_ids.ids)]})

                if self.team_replacement_user_id:
                    team.write({'team_member_ids': [(4, self.team_replacement_user_id.id)]})

                if team.account_manager_id == user:
                    team.write({
                        'account_manager_id': self.team_replacement_user_id.id if self.team_replacement_user_id else False})
                if team.project_manager_id == user:
                    team.write({
                        'project_manager_id': self.team_replacement_user_id.id if self.team_replacement_user_id else False})

        if self.archive_user:
            user.active = False

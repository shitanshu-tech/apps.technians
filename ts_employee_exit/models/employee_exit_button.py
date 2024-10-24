from odoo import fields, models, api

class EmployeeExit(models.TransientModel):
    _name = "employee.exit"
    _description = "Remove Employee from Task, Project, Courses, Teams"


    archive_employee = fields.Boolean(string="Archive Employee", help="Archive the employee when they exit")


    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    # Replacement fields
    task_replacement_user_id = fields.Many2one('res.users', string="Task Replacement User",
                                               help="Select a user to replace the exiting employee in tasks")
    project_replacement_user_id = fields.Many2one('res.users', string="Project Replacement User",
                                                  help="Select a user to replace the exiting employee in projects")
    course_replacement_user_id = fields.Many2one('res.users', string="Course Replacement User",
                                                 help="Select a user to replace the exiting employee in courses")
    team_replacement_user_id = fields.Many2one('res.users', string="Team Replacement User",
                                               help="Select a user to replace the exiting employee in teams")

    remove_from_task = fields.Boolean(string='Remove from Tasks', default=True)
    remove_from_project = fields.Boolean(string='Remove from Projects', default=True)
    remove_from_course = fields.Boolean(string='Remove from Courses', default=True)
    remove_from_project_team = fields.Boolean(string='Remove from Teams', default=True)

    task_count = fields.Integer(string='Tasks', compute='_compute_employee_tasks')
    project_count = fields.Integer(string='Projects', compute='_compute_employee_projects')
    course_count = fields.Integer(string='Courses', compute='_compute_employee_courses')
    team_count = fields.Integer(string='Teams', compute='_compute_employee_teams')

    @api.depends('employee_id')
    def _compute_employee_tasks(self):
        for record in self:
            tasks = self.env['project.task'].search([('user_ids', 'in', record.employee_id.user_id.id)])
            follower_tasks = self.env['project.task'].search(
                [('message_follower_ids.partner_id', '=', record.employee_id.user_id.partner_id.id)]
            )
            record.task_count = len(tasks) + len(follower_tasks)

    @api.depends('employee_id')
    def _compute_employee_projects(self):
        for record in self:
            projects = self.env['project.project'].search(['|', ('user_id', '=', record.employee_id.user_id.id),
                                                           ('account_manager_id', '=', record.employee_id.user_id.id)])
            follower_projects = self.env['project.project'].search(
                [('message_follower_ids.partner_id', '=', record.employee_id.user_id.partner_id.id)]
            )
            record.project_count = len(projects) + len(follower_projects)

    @api.depends('employee_id')
    def _compute_employee_courses(self):
        for record in self:
            owned_courses = self.env['slide.channel'].search([('user_id', '=', record.employee_id.user_id.id)])
            follower_courses = self.env['slide.channel'].search(
                [('message_follower_ids.partner_id', '=', record.employee_id.user_id.partner_id.id)]
            )
            record.course_count = len(owned_courses) + len(follower_courses)

    @api.depends('employee_id')
    def _compute_employee_teams(self):
        for record in self:
            teams = self.env['project.team.technians'].search(['|', '|',
                                                               ('team_member_ids', 'in', record.employee_id.user_id.id),
                                                               ('account_manager_id', '=', record.employee_id.user_id.id),
                                                               ('project_manager_id', '=', record.employee_id.user_id.id)])
            record.team_count = len(teams)

    def exit_employee(self):
        self.ensure_one()
        employee = self.employee_id
        user = employee.user_id

        # Handle tasks
        if self.remove_from_task:
            tasks = self.env['project.task'].search([('user_ids', 'in', user.id)])
            for task in tasks:
                task.user_ids = [(3, user.id)]  # Remove user from task
                if self.task_replacement_user_id:
                    task.user_ids = [(4, self.task_replacement_user_id.id)]  # Add replacement user

            follower_tasks = self.env['mail.followers'].search([('res_model', '=', 'project.task'),
                                                                ('partner_id', '=', user.partner_id.id)])
            follower_tasks.unlink()

        # Handle projects
        if self.remove_from_project:
            projects = self.env['project.project'].search(['|', ('user_id', '=', user.id),
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

        if self.archive_employee:
            employee.active = False

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


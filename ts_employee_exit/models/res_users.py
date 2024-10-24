from odoo import fields, models, api
from odoo.tools.populate import compute


class ResUsers(models.Model):
    _inherit = 'res.users'

    def open_user_exit_wizard(self):
        self.ensure_one()
        return {
            'name': 'User Exit',
            'type': 'ir.actions.act_window',
            'res_model': 'user.exit',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_user_id': self.id,
            }
        }

    assigned_task_count = fields.Integer(compute="compute_number_task")
    project_pm_count = fields.Integer(compute="compute_managed_projects")
    project_am_count = fields.Integer(compute="compute_account_manager_projects")
    project_follower_count = fields.Integer(compute="compute_follower_projects")

    # compute number of task in the form view of the user button

    def compute_number_task(self):
        self.ensure_one()
        user_id = self.id
        partner_id = self.partner_id.id
        stages = self.env['project.task.type'].search([('fold', '=', False)]).ids

        assigned_task_count = self.env['project.task'].search_count(
            [('user_ids', 'in', [user_id]), ('stage_id', 'in', stages)])

        follower_task_count = self.env['project.task'].search_count([
            ('message_follower_ids.partner_id', '=', partner_id),
            ('user_ids', 'not in', [user_id]),
            ('stage_id', 'in', stages)
        ])

        self.assigned_task_count = assigned_task_count + follower_task_count

    def compute_managed_projects(self):
        self.ensure_one()
        user_id = self.id
        stages = self.env['project.project.stage'].search([('fold', '=', False)]).ids
        managed_projects_count = self.env['project.project'].search_count(
            [('user_id', '=', user_id), ('stage_id', 'in', stages)])
        self.project_pm_count = managed_projects_count

    def compute_account_manager_projects(self):
        self.ensure_one()
        user_id = self.id
        stages = self.env['project.project.stage'].search([('fold', '=', False)]).ids
        account_manager_projects_count = self.env['project.project'].search_count(
            [('account_manager_id', '=', user_id), ('stage_id', 'in', stages)])
        self.project_am_count = account_manager_projects_count

    def compute_follower_projects(self):
        self.ensure_one()
        # user_id = self.id
        partner_id = self.partner_id.id
        stages = self.env['project.project.stage'].search([('fold', '=', False)]).ids
        follower_projects_count = self.env['project.project'].search_count(
            [('message_follower_ids.partner_id', '=', partner_id), ('stage_id', 'in', stages)])
        self.project_follower_count = follower_projects_count

    def action_assignes(self):
        self.ensure_one()

        user_id = self.id
        partner_id = self.partner_id.id

        task_names = []

        assigned_tasks = self.env['project.task'].search([('user_ids', 'in', [user_id])])

        task_names.extend(assigned_tasks.mapped('name'))

        follower_tasks = self.env['project.task'].search([('message_follower_ids.partner_id', '=', partner_id)])

        follower_task_names = follower_tasks.filtered(lambda t: user_id not in t.user_ids.ids).mapped('name')
        task_names.extend(follower_task_names)

        task_names = list(set(task_names))

        if not task_names:
            task_names.append('No tasks found')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Assigned Tasks',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [
                ('stage_id.name', '!=', 'Done'),
                ('id', 'in', assigned_tasks.ids + follower_tasks.ids),
            ],
            'target': 'current',
        }

    def action_project_manager(self):
        self.ensure_one()

        user_id = self.id

        managed_projects = self.env['project.project'].search([('user_id', '=', user_id)])

        project_names = managed_projects.mapped('name')

        project_names = list(set(project_names))

        active_projects = managed_projects.filtered(lambda p: p.stage_id.name != 'Done')

        if not active_projects:
            project_names = ['No projects found']
        else:
            project_names = active_projects.mapped('name')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Managed Projects',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [
                ('id', 'in', active_projects.ids),
            ],
            'target': 'current',
        }

    def action_account_manager_project(self):
        self.ensure_one()

        user_id = self.id

        managed_projects = self.env['project.project'].search([('account_manager_id', '=', user_id)])

        # Filter out active projects
        active_projects = managed_projects.filtered(lambda p: p.stage_id.name != 'Done')

        if not active_projects:
            project_names = ['No projects found']
        else:
            project_names = active_projects.mapped('name')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Managed Projects',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [
                ('id', 'in', active_projects.ids),
            ],
            'target': 'current',
        }

    def action_follower_projects(self):
        self.ensure_one()

        user_id = self.id
        partner_id = self.partner_id.id

        follower_projects = self.env['project.project'].search([('message_follower_ids.partner_id', '=', partner_id)])

        active_follower_projects = follower_projects.filtered(lambda p: p.stage_id.name != 'Done')

        project_ids = active_follower_projects.ids

        if not project_ids:
            project_ids = [0]

        return {
            'type': 'ir.actions.act_window',
            'name': 'Follower Projects',
            'res_model': 'project.project',
            'view_mode': 'tree,form',
            'domain': [
                ('id', 'in', project_ids),
            ],
            'target': 'current',
        }

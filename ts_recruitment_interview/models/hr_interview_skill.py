from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InterviewSkill(models.Model):
    _name = 'hr.interview.skill'
    _rec_name = 'skill_id'
    _order = "skill_level_id"

    wizard_id = fields.Many2one(
        comodel_name='hr.interview.wizard',
        # required=True,
        ondelete='cascade')
    applicant_id = fields.Many2one(
        comodel_name='hr.interview',
        # required=True,
        ondelete='cascade')
    skill_id = fields.Many2one(
        comodel_name='hr.skill',
        compute='_compute_skill_id',
        store=True,
        domain="[('skill_type_id', '=', skill_type_id)]",
        readonly=False,
        required=True)
    skill_level_id = fields.Many2one(
        comodel_name='hr.skill.level',
        compute='_compute_skill_level_id',
        domain="[('skill_type_id', '=', skill_type_id)]",
        store=True,
        readonly=False,
        required=True)
    skill_type_id = fields.Many2one(
        comodel_name='hr.skill.type',
        required=True)
    level_progress = fields.Integer(
        related='skill_level_id.level_progress')

    applicant_skill_level_id = fields.Many2one(
        comodel_name='hr.skill.level',
        compute='_compute_applicant_skill_level_id',
        domain="[('skill_type_id', '=', skill_type_id)]",
        store=True,
        readonly=False)

    applicant_level_progress = fields.Integer(
        related='applicant_skill_level_id.level_progress')

    reported_skill_level_id = fields.Many2one(
        comodel_name='hr.skill.level',
        compute='_compute_reported_skill_level_id',
        domain="[('skill_type_id', '=', skill_type_id)]",
        store=True,
        readonly=False)

    reported_level_progress = fields.Integer(
        related='reported_skill_level_id.level_progress')


    _sql_constraints = [
        ('_unique_skill_interview', 'unique (applicant_id, skill_id)', "Two levels for the same skill is not allowed"),
    ]

    @api.constrains('skill_id', 'skill_type_id')
    def _check_skill_type(self):
        for applicant in self:
            if applicant.skill_id not in applicant.skill_type_id.skill_ids:
                raise ValidationError(_("The skill %(name)s and skill type %(type)s doesn't match", name=applicant.skill_id.name, type=applicant.skill_type_id.name))

    @api.constrains('skill_type_id', 'skill_level_id')
    def _check_skill_level(self):
        for applicant in self:
            if applicant.skill_level_id not in applicant.skill_type_id.skill_level_ids:
                raise ValidationError(_("The skill level %(level)s is not valid for skill type: %(type)s", level=applicant.skill_level_id.name, type=applicant.skill_type_id.name))

    @api.depends('skill_type_id')
    def _compute_skill_id(self):
        for applicant in self:
            if applicant.skill_id.skill_type_id != applicant.skill_type_id:
                applicant.skill_id = False

    @api.depends('skill_id')
    def _compute_skill_level_id(self):
        for applicant in self:
            if not applicant.skill_id:
                applicant.skill_level_id = False
            else:
                skill_levels = applicant.skill_type_id.skill_level_ids
                applicant.skill_level_id = skill_levels.filtered('default_level') or skill_levels[0] if skill_levels else False

    @api.depends('skill_id')
    def _compute_applicant_skill_level_id(self):
        for applicant in self:
            if not applicant.skill_id:
                applicant.applicant_skill_level_id = False
            else:
                skill_levels = applicant.skill_type_id.skill_level_ids
                applicant.applicant_skill_level_id = skill_levels.filtered('default_level') or skill_levels[0] if skill_levels else False

    @api.depends('skill_id')
    def _compute_reported_skill_level_id(self):
        for applicant in self:
            if not applicant.skill_id:
                applicant.reported_skill_level_id = False
            else:
                skill_levels = applicant.skill_type_id.skill_level_ids
                applicant.reported_skill_level_id = skill_levels.filtered('default_level') or skill_levels[0] if skill_levels else False

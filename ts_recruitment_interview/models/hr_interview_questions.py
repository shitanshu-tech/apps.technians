from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

AVAILABLE_RATINGS = [
    ('0', 'Average'),
    ('1', 'Normal'),
    ('2', 'Good'),
    ('3', 'Very Good'),
    ('4', 'Brilliant'),
    ('5', 'Excellent')
]

class HrInterviewQuestions(models.Model):
    _name = 'hr.interview.questions'
    _description = "Interview Questions"

    wizard_id = fields.Many2one(
        comodel_name='hr.interview.wizard',
        # required=True,
        ondelete='cascade')

    interview_id = fields.Many2one(
        comodel_name='hr.interview',
        # required=True,
        ondelete='cascade')

    name = fields.Many2one(
        comodel_name='slide.slide',
        string='Chapters',)

    rating = fields.Selection(AVAILABLE_RATINGS, string='Rating', default='0')

    feedback = fields.Char(string='Feedback')

    @api.onchange('name')
    def _change_chapter(self):
        self.rating = self.feedback = False


    # @api.model
    # def default_get(self, fields):
    #     defaults = super(HrInterviewQuestions, self).default_get(fields)
    #
    #     if 'params' in self.env.context:
    #         interview = self.env.context['params'].get('id')
    #         if interview:
    #             defaults['interview_id'] = interview
    #
    #     return defaults

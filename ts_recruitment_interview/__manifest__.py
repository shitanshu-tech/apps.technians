{
    'name': 'Recruitment Interview',
    'version': '1.0',
    'category': 'Recruiting',
    'sequence': 1,
    'website': '',
    'summary': 'linking Skills and Job',
    'description': 'Recruitment extension',
    'author': 'Rahul',
    # 'depends': ['hr_recruitment','hr_skills'],
    'depends': ['base', 'mail', 'hr_skills', 'hr', 'hr_recruitment', 'website_slides', 'hr_timesheet',],

    'data': [
        'security/hr_interview_security.xml',
        'security/ir.model.access.csv',
        'views/hr_job.xml',
        'views/hr_job_skill.xml',
        'views/hr_interview.xml',
        'views/hr_interview_skill.xml',
        'views/hr_applicant.xml',
        'views/hr_interview_questions.xml',
        'views/hr_interview_stage.xml',
        'views/res_config_settings.xml',
        'views/hr_interview_wizard.xml',

    ],
    'demo': [
        'demo/demo_data.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': "Task Deadline Reminder",
    'version': '16.0',
    'author': 'Technians',
    'company': 'Technians',
    'maintainer': 'Technians',
    'website': 'https://www.technians.com',
    'summary': '''Automatically Send Mail To Responsible User if Deadline Of Task is Today''',
    'category': "Project",
    'depends': ['project'],
    'license': 'AGPL-3',
    'data': [
            'views/deadline_reminder_cron.xml',
            'views/project_task.xml',
             ],
    'installable': True,
    'auto_install': False
}



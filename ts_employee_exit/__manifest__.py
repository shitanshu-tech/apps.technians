{
    'name': 'Employee Exit',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'sequence': 1,
    'website': 'https://technians.com',
    'description': 'Employee Exit',
    'author': 'shitanshu',
    'depends':['base','hr','project','website_slides','project_team_technians'],

    'data': [
        'security/ir.model.access.csv',
        'views/employee_exit.xml',
        'views/user_exit.xml',
    ],

    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

{
    'name': 'Technians Apps Customization',
    'version': '2.3',
    'summary': 'Added Equipment Sequence',
    'description': '',
    'category': 'CRM',
    'author': ' Technians',
    'website': 'www.technians.com',
    'license': '',
    'depends': ['base','crm','maintenance','sale_management','hr_recruitment','hr_employee_updation','project','sales_team','whatsapp_integration_technians'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/crm_lead.xml',
        'views/lead_status.xml',
        'views/job_roles.xml',
        'views/hr_applicant.xml',
        'views/hr_employer.xml',
        'views/hr_timesheet.xml',
        #'views/account_move.xml',
        'views/project_project.xml',
        'views/maintenance_equipment.xml',
        'views/sales_order.xml',
        'views/hr_employee.xml',
        # 'views/product_template.xml',
        # 'views/product_product.xml',
        'views/mail_activity.xml',
        'data/sequence.xml',
        'report/sales_order_report.xml',
        'views/mass_mailing_templates.xml',
        'views/feedback_mailers.xml',
        'views/hr_recruitment.xml',
        'views/utm_source.xml',
        'views/mail_templates.xml',
        'views/ir_cron.xml',
        'views/hr_department.xml'
    ],
    'assets': {
    'web.assets_backend': [
                'technians_apps_customization/static/src/js/color_picker.js'
                ]
                    },
    'auto_install': False,
}


#-*- coding:utf-8 -*-

{
    'name': 'KUH7 - Odoo 13 Payroll',
    'category': 'Human Resources',
    'version': '1.0',
    'sequence': 1,
    'author': 'KUH7',
    'summary': 'KUH7 - Payroll For Odoo 13 Community Edition',
    'description': "",
    'depends': [
        'om_hr_payroll',
        'nomina_cfdi',
    ],
    'data': [
        'security/security.xml',
        'wizard/hr_payroll_payslips_by_employees_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_payroll_payslip_view.xml',
    ],
    'application': False,
}

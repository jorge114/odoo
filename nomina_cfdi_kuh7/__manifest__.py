# -*- coding: utf-8 -*-

{
    'name': 'KUH7 - Nomina Electrónica para México CFDI v1.2',
    'summary': 'KUH7 - Agrega funcionalidades para timbrar la nómina electrónica en México.',
    'description': '''
    KUH7 - Nomina CFDI Module
    ''',
    'author': 'KUH7',
    'version': '1.0',
    'category': 'Employees',
    'depends': [
        'nomina_cfdi_ee',
    ],
    'data': [
        'views/hr_contract_view.xml',
        'views/hr_payroll_payslip_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}

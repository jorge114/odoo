# -*- coding: utf-8 -*-

{
    'name': 'Nomina Electrónica 4/3 ',
    'summary': 'Agrega modificacion para una nomina de 4 dias trabajo x 3 descanso.',
    'description': '''
    Nomina CFDI Module
    ''',
    'author': 'IT Admin',
    'version': '12.01',
    'category': 'Employees',
    'depends': [
        'om_hr_payroll','nomina_cfdi_ee'
    ],
    'data': [
        'views/hr_contract_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}

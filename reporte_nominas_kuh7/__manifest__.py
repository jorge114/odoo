# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Reportes nómina',
    'summary': 'Agregar nuevo formato de listado de nómina',
    'description': '''
    * Agregar nuevo formato de listado de nómina
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. de C.V.',
    'version': '1.7',
    'category': 'reports',
    'depends': [
        'nomina_cfdi_ee',
        'nomina_cfdi_extras_ee',
    ],
    'data': [
        'views/hr_payslip_run_view.xml',
    ],
    'installable': True,
    'application': False
}
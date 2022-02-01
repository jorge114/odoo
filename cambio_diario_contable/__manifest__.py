# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Cambio de dominio cuentas diario contable',
    'summary': 'Cambiar dominio campo de diario contable',
    'description': '''
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. DE C.V.',
    'version': '1.1',
    'category': 'Account',
    'depends': [
        'nomina_cfdi_ee',
        'nomina_cfdi_extras_ee',
        'nomina_cfdi_conta_ee',
    ],
    'data': [
        'views/account_journal_view.xml',
        'views/hr_paylip_view.xml',
    ],
    'installable': True,
    'application': False
}
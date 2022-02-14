# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - filtro reglas salariales',
    'summary': 'KUH7 - filtro para reglas salariales por compañia',
    'description': '''
    KUH7 - filtro reglas salariales por compañia
    ''',
    "website": "https://www.kuh7.mx/",
    'author': 'KUH7 SOLUCIONES S.A. de C.V.',
    'version': '1.0',
    'category': 'kuh7',
    'depends': [
        'nomina_cfdi_ee',
        'nomina_cfdi_extras_ee',
        'hr_contract',
        'om_hr_payroll',
    ],
    'data': [
        'views/hr_salary_rule_views.xml',

    ],
}
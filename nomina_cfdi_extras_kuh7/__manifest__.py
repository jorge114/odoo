# -*- coding: utf-8 -*-

{
    'name': 'KUH7 - Nomina CFDI Extras',
    'summary': '',
    'description': '''
KUH7
====
Personalizaciones para nomina_cfdi_extras. 
    ''',
    'author': 'KUH7',
    'version': '1.0',
    'category': 'Employees',
    'depends': [
        'nomina_cfdi_ee',
        'nomina_cfdi_extras_ee',
    ],
    'data': [
        'security/security.xml',
        'wizard/importar_movimientos_faltas_view.xml',
        'wizard/importar_movimientos_vacaciones_view.xml',
        'wizard/importar_movimientos_horas_extras_view.xml',
        'wizard/importar_movimientos_retardos_view.xml',
        'wizard/importar_movimientos_incapacidades_view.xml',
        'wizard/importar_movimientos_feriados_view.xml',
        'views/hr_employee_view.xml',
        'views/menu.xml',
    ],
}

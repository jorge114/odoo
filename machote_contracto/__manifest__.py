# -*- coding: utf-8 -*-
{
    'name': "KUH7 - Crea machote para contracto",
    'version': '1.1',
    'depends': [
        'hr',
    ],
    'website': 'https://www.kuh7.mx/',
    'author': "KUH7 SOLUCIONES S.A. de C.V.",
    'category': 'Tools',
    'description': """
        Este modulo crea un machote para los contractos que se genera en la empresa.
    """,
    # data files always loaded at installation
    'data': [
        'views/view_machote_contracto.xml',
        'views/view_new_campos_contracto.xml',
        'views/view_new_campos_empleado.xml',
    ],
}
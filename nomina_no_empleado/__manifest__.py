# -*- coding: utf-8 -*-
{
    'name': "KUH7 - Agrega nueva columna en Nomina",
    'version': '1.0',
    'depends': [
        'nomina_cfdi_ee',
    ],
    'website': 'https://www.kuh7.mx/',
    'author': "KUH7 SOLUCIONES S.A. de C.V.",
    'category': 'Tools',
    'description': """
        Este modulo agrega nueva columna en procesamiento de nomina. El campo a llamarse es No. empleado.
    """,
    # data files always loaded at installation
    'data': [
        'views/view_mostrar_no_empleado.xml',
    ],
}
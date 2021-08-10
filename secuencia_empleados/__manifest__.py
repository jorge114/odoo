# -*- coding: utf-8 -*-
{
    'name': 'KUH7 - Secuencia por número de nómina empleados',
    'summary': 'Agregar secuancia para los números de empleados',
    'description': '''
    * Generar secuencia por números de nómina de los empleados
    * Validar que no se pueda generar un nuevo empleado con un RFC y dado de alta
    ''',
    "website": "http://www.kuh7.mx",
    'author': 'Kuh7 Soluciones S.A. de C.V.',
    'version': '1.2',
    'category': 'employees',
    'depends': [
        'hr',
    ],
    'data': [
        'data/secuencia_empleados.xml',
    ],
    'installable': True,
    'application': False
}
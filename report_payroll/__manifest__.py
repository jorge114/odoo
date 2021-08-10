# -*- encoding: utf-8 -*-
{
    'name': "Modulo para generar reporte de incidencias encontradas en el periodo nómina",
    'version': '1.0',
    'depends': ['nomina_cfdi_ee'],
    'website': 'https://www.kuh7.mx',
    'author': "JOSÉ MARÍA HERIBERTO ALVARADO SOLÓRZANO",
    'category': 'Report',
    'description': """
    Este módulo servirá para generar reporte de incidencias que se tuvieron los empleados durante el periodo de nómina para incidencias de Faltas, Incapacidades, Vacaciones, Dias festivos, Retardos y Horas Extra, se genera un reporte por incidencia.
    """,
    'data': [
        'reports/reporte_incidencia_h_e.xml',
        'reports/reporte_incidencias_df.xml',
        'reports/reporte_incidencias_faltas.xml',
        'reports/reporte_incidencias_inc.xml',
        'reports/reporte_incidencias_ret.xml',
        'reports/reporte_incidencias_vac.xml'
    ],
}
# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _validate_low_first_week_month(self):
        # Se requiere obtener siempre la segunda semana de cada mes
        # Obtenemos la  fecha actual
        tz_mx = pytz.timezone('America/Mexico_City')
        today = datetime.now(tz_mx)
        current_year = today.strftime('%Y')
        current_month = today.strftime('%m')
        current_date = today.strptime((today.strftime('%Y') + '-' + today.strftime('%m') + '-' + today.strftime('%d')),
                                      '%Y-%m-%d')

        # Formamos el primer día del cada mes
        first_week_month = current_year + "-" + current_month + "-01"
        # convertimos la variable de inicio del mes a tipo fecha
        dt = datetime.strptime(first_week_month, '%Y-%m-%d')
        # Obtenemos el primer de la semana
        r_week_start = dt - timedelta(days=dt.weekday())

        # Sumamos una semana al incio de sem
        week_start = r_week_start + timedelta(days=7)
        # Sumamos ahora 6 días para obtener el fin de sem
        week_end = week_start + timedelta(days=6)

        # current_date = today.strptime("2021-02-24", '%Y-%m-%d')
        # Obtener los días de antiguedad
        now_date = today.strftime('%Y-%m-%d')
        v_start_date = self.date_start.strftime('%Y-%m-%d')
        start_date = datetime.strptime(v_start_date, '%Y-%m-%d')
        v_today = datetime.strptime(now_date, '%Y-%m-%d')

        dias_antiguedad = int((v_today - start_date) / timedelta(days=1))

        # Pasamos a string el inicio de la primera semana del mes
        v_primer_sem_mes = r_week_start.strftime("%Y-%m-%d")
        # Convertimos string a tipo fecha
        r_primer_sem_mes = datetime.strptime(v_primer_sem_mes, '%Y-%m-%d')

        # Restamos 1 día a la fecha anterior
        v_fecha_ultima_sem_mes = r_primer_sem_mes + timedelta(days=-1)
        fecha_ultima_sem_mes = v_fecha_ultima_sem_mes.date()

        periodo_nomina = False
        if self.tablas_cfdi_id:
            periodos = self.env['tablas.periodo.semanal'].search(
                [('form_id', '=', self.tablas_cfdi_id.id)],
                order='dia_inicio asc')

            ini_periodo = ""
            fin_periodo = ""
            if periodos:
                for line in periodos:
                    if fecha_ultima_sem_mes == line.dia_fin or fecha_ultima_sem_mes > line.dia_fin:
                        ini_periodo = line.dia_inicio
                        fin_periodo = line.dia_fin
                    elif fecha_ultima_sem_mes < line.dia_fin:
                        break
            # print("Inicio periodo:", ini_periodo)
            # print("Fin periodo:", fin_periodo)
            if ini_periodo != "":
                if self.date_start < ini_periodo or self.date_start == ini_periodo:
                    periodo_nomina = True

        if periodo_nomina:
            if current_date >= week_start and current_date <= week_end:
                if self.department_id.parent_id != "340":
                    if self.job_id.name == 'OPERADOR' or self.job_id.name == 'ASISTENTE' or self.job_id.name == 'OPERADOR LIDER' or self.job_id.name == 'AUXILIAR':
                        self.first_week_month = True
                    else:
                        self.first_week_month = False
                else:
                    self.first_week_month = False
            else:
                self.first_week_month = False
        else:
            self.first_week_month = False

    low_first_week_month = fields.Boolean(string="Baja primer semana del mes", compute="_validate_low_first_week_month")

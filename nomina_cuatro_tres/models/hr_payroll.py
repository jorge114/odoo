# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import timedelta, date
import datetime
from pytz import timezone
import logging
_logger = logging.getLogger(__name__)
from collections import defaultdict

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        horas_obj = self.env['horas.nomina']
        tipo_de_hora_mapping = {'1':'HEX1', '2':'HEX2', '3':'HEX3'}
        
        def is_number(s):
            try:
                return float(s)
            except ValueError:
                return 0

        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.datetime.combine(fields.Date.from_string(date_from), datetime.time.min)
            day_to = datetime.datetime.combine(fields.Date.from_string(date_to), datetime.time.max)
            nb_of_days = (day_to - day_from).days + 1

            # compute Prima vacacional en fecha correcta
            if contract.tipo_prima_vacacional == '01':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)
                
                    date_start = fields.Date.from_string(date_start)
                    if datetime.datetime.today().year > date_start.year:
                        if str(date_start.day) == '29' and str(date_start.month) == '2':
                            date_start -=  datetime.timedelta(days=1)
                        date_start = date_start.replace(d_to.year)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - datetime.datetime.combine(contract.date_start, datetime.time.max)
                            years = diff_date.days /365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(lambda x:x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                 'name': 'Prima vacacional',
                                 'sequence': 2,
                                 'code': 'PVC',
                                 'number_of_days': vacaciones * prima_vac / 100.0, #work_data['days'],
                                 'number_of_hours': vacaciones * prima_vac / 100.0 * 8,
                                 'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima vacacional
            if contract.tipo_prima_vacacional == '03':
                date_start = contract.date_start
                if date_start:
                    d_from = fields.Date.from_string(date_from)
                    d_to = fields.Date.from_string(date_to)

                    date_start = fields.Date.from_string(date_start)
                    if datetime.datetime.today().year > date_start.year and d_from.day > 15:
                        if str(date_start.day) == '29' and str(date_start.month) == '2':
                            date_start -=  datetime.timedelta(days=1)
                        date_start = date_start.replace(d_to.year)
                        d_from = d_from.replace(day=1)

                        if d_from <= date_start <= d_to:
                            diff_date = day_to - datetime.datetime.combine(contract.date_start, datetime.time.max)
                            years = diff_date.days /365.0
                            antiguedad_anos = int(years)
                            tabla_antiguedades = contract.tablas_cfdi_id.tabla_antiguedades.filtered(lambda x: x.antiguedad <= antiguedad_anos)
                            tabla_antiguedades = tabla_antiguedades.sorted(lambda x:x.antiguedad, reverse=True)
                            vacaciones = tabla_antiguedades and tabla_antiguedades[0].vacaciones or 0
                            prima_vac = tabla_antiguedades and tabla_antiguedades[0].prima_vac or 0
                            attendances = {
                                 'name': 'Prima vacacional',
                                 'sequence': 2,
                                 'code': 'PVC',
                                 'number_of_days': vacaciones * prima_vac / 100.0, #work_data['days'],
                                 'number_of_hours': vacaciones * prima_vac / 100.0 * 8,
                                 'contract_id': contract.id,
                            }
                            res.append(attendances)

            # compute Prima dominical
            if contract.prima_dominical:
                domingos = 0
                d_from = fields.Date.from_string(date_from)
                d_to = fields.Date.from_string(date_to)
                for i in range((d_to - d_from).days + 1):
                    if (d_from + datetime.timedelta(days=i+1)).weekday() == 0:
                        domingos = domingos + 1
                attendances = {
                            'name': 'Prima dominical',
                            'sequence': 2,
                            'code': 'PDM',
                            'number_of_days': domingos, #work_data['days'],
                            'number_of_hours': domingos * 8,
                            'contract_id': contract.id,
                     }
                res.append(attendances)

            # compute leave days
            leaves = {}
            leave_days = 0
            inc_days = 0
            vac_days = 0
            factor = 0
            if contract.tipo_semana == '01':
                factor = 7.0/6.0
            elif contract.tipo_semana == '02':
                factor = 7.0/5.0
            else:
                factor = 6.0/4.0

            if contract.periodicidad_pago == '04':
                dias_pagar = 15
            elif contract.periodicidad_pago == '02':
                dias_pagar = 7
            else:
                dias_pagar = (date_to - date_from).days + 1

            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day, hours, leave in day_leave_intervals:
                holiday = leave.holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.name or 'GLOBAL',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                })
                #current_leave_struct['number_of_hours'] += hours
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.datetime.combine(day, datetime.time.min)),
                    tz.localize(datetime.datetime.combine(day, datetime.time.max)),
                    compute_leaves=False,
                )
                if work_hours and contract.septimo_dia:
                        if contract.incapa_sept_dia:
                           if holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR':
                              leave_days += (hours / work_hours)*factor
                              current_leave_struct['number_of_days'] += (hours / work_hours)*factor
                              if leave_days > dias_pagar:
                                 leave_days = dias_pagar
                              if current_leave_struct['number_of_days'] > dias_pagar:
                                 current_leave_struct['number_of_days'] = dias_pagar
                           elif holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT':
                              leave_days += hours / work_hours * factor
                              inc_days += 1
                              current_leave_struct['number_of_days'] += (hours / work_hours)*factor
                           else:
                              if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                                 leave_days += hours / work_hours
                              current_leave_struct['number_of_days'] += hours / work_hours
                              if holiday.holiday_status_id.name == 'VAC' or holiday.holiday_status_id.name == 'FJC':
                                 vac_days += 1
                        else:
                           if holiday.holiday_status_id.name == 'FJS' or holiday.holiday_status_id.name == 'FI' or holiday.holiday_status_id.name == 'FR':
                              leave_days += (hours / work_hours)*factor
                              current_leave_struct['number_of_days'] += (hours / work_hours)*factor
                              if leave_days > dias_pagar:
                                 leave_days = dias_pagar
                              if current_leave_struct['number_of_days'] > dias_pagar:
                                 current_leave_struct['number_of_days'] = dias_pagar
                           elif holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT':
                              leave_days += hours / work_hours * factor
                              inc_days += 1
                              current_leave_struct['number_of_days'] += (hours / work_hours)*factor
                           else:
                              if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                                 leave_days += hours / work_hours
                              current_leave_struct['number_of_days'] += hours / work_hours
                              if holiday.holiday_status_id.name == 'VAC' or holiday.holiday_status_id.name == 'FJC':
                                 vac_days += 1
                elif work_hours:
                        if contract.incapa_sept_dia:
                           if holiday.holiday_status_id.name == 'INC_EG' or holiday.holiday_status_id.name == 'INC_RT' or holiday.holiday_status_id.name == 'INC_MAT':
                              leave_days += (hours / work_hours)*factor
                              current_leave_struct['number_of_days'] += (hours / work_hours)*factor
                           else:
                              if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                                 leave_days += hours / work_hours
                              current_leave_struct['number_of_days'] += hours / work_hours
                              if holiday.holiday_status_id.name == 'VAC' or holiday.holiday_status_id.name == 'FJC':
                                 vac_days += 1
                        else:
                           if holiday.holiday_status_id.name != 'DFES' and holiday.holiday_status_id.name != 'DFES_3':
                              leave_days += hours / work_hours
                           current_leave_struct['number_of_days'] += hours / work_hours
                           if holiday.holiday_status_id.name == 'VAC' or holiday.holiday_status_id.name == 'FJC':
                              vac_days += 1

            # compute worked days
            work_data = contract.employee_id._get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            number_of_days = 0

            # ajuste en caso de nuevo ingreso
            nvo_ingreso = False
            date_start_1 = contract.date_start
            d_from_1 = fields.Date.from_string(date_from)
            d_to_1 = fields.Date.from_string(date_to)
            if date_start_1 > d_from_1:
                   work_data['days'] =  (date_to - date_start_1).days + 1
                   nvo_ingreso = True
            if contract.date_end:
               if d_to_1 > date_start_1:
                   work_data['days'] =  (contract.date_end - date_from).days + 1
                   nvo_ingreso = True

            #dias_a_pagar = contract.dias_pagar
            _logger.info('dias trabajados %s  dias incidencia %s', work_data['days'], leave_days)

            if work_data['days'] < 100:
            #periodo para nómina quincenal
               if contract.periodicidad_pago == '04':
                   if contract.tipo_pago == '01' and nb_of_days < 17:
                      total_days = work_data['days'] + leave_days
                      if total_days != 15 or leave_days != 0:
                         if leave_days == 0 and not nvo_ingreso:
                            number_of_days = 15
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] - leave_days
                         else:
                            number_of_days = 15 - leave_days
                      else:
                         number_of_days = work_data['days']
                      if contract.sept_dia:
                         aux = 2.5
                         number_of_days -=  aux
                         attendances = {
                             'name': _("Séptimo día"),
                             'sequence': 3,
                             'code': "SEPT",
                             'number_of_days': aux, 
                             'number_of_hours': 0.0,
                             'contract_id': contract.id,
                         }
                         res.append(attendances)
                   elif contract.tipo_pago == '03' and nb_of_days < 17:
                      total_days = work_data['days'] + leave_days
                      if total_days != 15.21 or leave_days != 0:
                         if leave_days == 0  and not nvo_ingreso:
                            number_of_days = 15.21
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] * 15.21 / 15 - leave_days
                         else:
                            number_of_days = 15.21 - leave_days
                      else:
                         number_of_days = work_data['days'] * 15.21 / 15
                      if number_of_days < 0:
                         number_of_days = 0
                      if contract.sept_dia:
                         aux = 2.21
                         number_of_days -=  aux
                         attendances = {
                             'name': _("Séptimo día"),
                             'sequence': 3,
                             'code': "SEPT",
                             'number_of_days': aux, 
                             'number_of_hours': 0.0,
                             'contract_id': contract.id,
                         }
                         res.append(attendances)
                   else:
                      dias_periodo = (date_to - date_from).days + 1
                      total_days = work_data['days'] + leave_days
                      if total_days != dias_periodo or leave_days != 0:
                         if leave_days == 0  and not nvo_ingreso:
                            number_of_days = dias_periodo
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] - leave_days
                         else:
                            number_of_days = dias_periodo - leave_days
                      else:
                         number_of_days = work_data['days']
               #calculo para nóminas semanales
               elif contract.periodicidad_pago == '02' and nb_of_days < 8:
                   if nvo_ingreso:
                      number_of_days = work_data['days'] - leave_days # dias desde inicio de contrato - otras incidencias
                   else:
                      number_of_days = 6 - leave_days
                   if number_of_days < 0:
                         number_of_days = 0
                   if contract.sept_dia: # septimo día
                      if contract.incapa_sept_dia:
                          aux = number_of_days + inc_days + vac_days
                      else:
                          aux = number_of_days + vac_days
                      if contract.tipo_semana == '02':
                          aux = aux / 6
                      elif contract.tipo_semana == '03':
                          aux = aux / 6
                      else:
                          aux = aux / 6
                      if aux < 0:
                          aux = 0
                      attendances = {
                          'name': _("Séptimo día"),
                          'sequence': 3,
                          'code': "SEPT",
                          'number_of_days': aux, 
                          'number_of_hours': round(aux*8,2),
                          'contract_id': contract.id,
                      }
                      res.append(attendances)
                   else:
                      if falta_days >= 6 or inc_days >= 6:
                         number_of_days = 0

               #calculo para nóminas mensuales
               elif contract.periodicidad_pago == '05':
                  if contract.tipo_pago == '01':
                      total_days = work_data['days'] + leave_days
                      if total_days != 30:
                         if leave_days == 0 and not nvo_ingreso:
                            number_of_days = 30
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] - leave_days
                         else:
                            number_of_days = 30 - leave_days
                  elif contract.tipo_pago == '03':
                      total_days = work_data['days'] + leave_days
                      if total_days != 30.42:
                         if leave_days == 0  and not nvo_ingreso:
                            number_of_days = 30.42
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] * 30.42 / 30 - leave_days
                         else:
                            number_of_days = 30.42 - leave_days
                      else:
                         number_of_days = work_data['days'] * 30.42 / 30
                  else:
                      dias_periodo = (date_to - contract.date_start).days + 1
                      total_days = work_data['days'] + leave_days
                      if total_days != dias_periodo:
                         if leave_days == 0  and not nvo_ingreso:
                            number_of_days = dias_periodo
                         elif nvo_ingreso:
                            number_of_days = work_data['days'] - leave_days
                         else:
                            number_of_days = dias_periodo - leave_days
                      else:
                         number_of_days = work_data['days']
               else:
                  number_of_days = work_data['days']
            else:
               date_start = contract.date_start
               if date_start:
                   d_from = fields.Date.from_string(date_from)
                   d_to = fields.Date.from_string(date_to)
               if date_start > d_from:
                   number_of_days =  (date_to - date_start).days + 1 - leave_days
               else:
                   number_of_days =  (date_to - date_from).days + 1 - leave_days
            attendances = {
                'name': _("Días de trabajo"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': number_of_days, #work_data['days'],
                'number_of_hours': round(number_of_days*8,2), # work_data['hours'],
                'contract_id': contract.id,
            }
            res.append(attendances)

            #Compute horas extas
            horas = horas_obj.search([('employee_id','=',contract.employee_id.id),('fecha','>=',date_from), ('fecha', '<=', date_to),('state','=','done')])
            horas_by_tipo_de_horaextra = defaultdict(list)
            for h in horas:
                horas_by_tipo_de_horaextra[h.tipo_de_hora].append(h.horas)
            
            for tipo_de_hora, horas_set in horas_by_tipo_de_horaextra.items():
                work_code = tipo_de_hora_mapping.get(tipo_de_hora,'')
                number_of_days = len(horas_set)
                number_of_hours = sum(is_number(hs) for hs in horas_set)
                     
                attendances = {
                    'name': _("Horas extras"),
                    'sequence': 2,
                    'code': work_code,
                    'number_of_days': number_of_days, 
                    'number_of_hours': number_of_hours,
                    'contract_id': contract.id,
                }
                res.append(attendances)
                
            res.extend(leaves.values())
        
        return res

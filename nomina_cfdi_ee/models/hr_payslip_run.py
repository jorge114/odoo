# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from calendar import monthrange
import logging
_logger = logging.getLogger(__name__)

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    
    def action_confirmar_nomina(self):
        for rec in self:
            slip_ids = rec.slip_ids.filtered(lambda r: r.state == 'draft')
            for slip_id in slip_ids:
                slip_id.action_payslip_done()

    def action_cancelar_nomina(self):
        for rec in self:
            slip_ids = rec.slip_ids.filtered(lambda r: r.state == 'done')
            for slip_id in slip_ids:
                slip_id.write({'state': 'cancel'})
    
    tipo_configuracion = fields.Many2one('configuracion.nomina', string='Configuración')
    all_payslip_generated = fields.Boolean("Payslip Generated",compute='_compute_payslip_cgdi_generated')
    all_payslip_generated_draft = fields.Boolean("Payslip Generated draft",compute='_compute_payslip_cgdi_generated_draft')
    tipo_nomina = fields.Selection(
        selection=[('O', 'Nómina ordinaria'), ('E', 'Nómina extraordinaria'),], string=_('Tipo de nómina'), required=True, default='O')
    estructura = fields.Many2one('hr.payroll.structure', string='Estructura')
    tabla_otras_entradas = fields.One2many('otras.entradas', 'form_id')
    dias_pagar = fields.Float(string='Dias a pagar', store=True)
    imss_dias = fields.Float(string='Dias a cotizar en la nómina', store=True)
    imss_mes = fields.Float(string='Dias en el mes', store=True)
    ultima_nomina = fields.Boolean(string='Última nómina del mes')
    nominas_mes = fields.Integer('Nóminas a pagar en el mes')
    concepto_periodico = fields.Boolean('Conceptos periódicos', default = True)
    isr_ajustar = fields.Boolean(string='Ajustar ISR en nómina')
    isr_devolver = fields.Boolean(string='Devolver ISR')
    periodicidad_pago = fields.Selection(
        selection=[('01', 'Diario'), 
                   ('02', 'Semanal'), 
                   ('03', 'Catorcenal'),
                   ('04', 'Quincenal'), 
                   ('05', 'Mensual'),
                   ('06', 'Bimensual'), 
                   ('07', 'Unidad obra'),
                   ('08', 'Comisión'), 
                   ('09', 'Precio alzado'), 
                   ('10', 'Pago por consignación'), 
                   ('99', 'Otra periodicidad'),],
        string=_('Frecuencia de pago'), required=True
    )
    fecha_pago = fields.Date(string=_('Fecha de pago'), required=True)
    isr_anual = fields.Boolean(string='ISR anual')
    no_periodo = fields.Selection(
        selection=[('1', 'Periodo 1'), 
                   ('2', 'Periodo 2'), 
                   ('3', 'Periodo 3'),
                   ('4', 'Periodo 4'), 
                   ('5', 'Periodo 5'),
                   ('6', 'Periodo 6'),
                   ('7', 'Periodo 7'),
                   ('8', 'Periodo 8'),
                   ('9', 'Periodo 9'),
                   ('10', 'Periodo 10'),
                   ('11', 'Periodo 11'),
                   ('12', 'Periodo 12'),
                   ],
        string=_('No. Periodo'),)

    @api.onchange('tipo_configuracion')
    def _set_periodicidad(self):
        if self.tipo_configuracion:
            if self.tipo_configuracion.fijo_imss:
                values = {
                   'periodicidad_pago': self.tipo_configuracion.periodicidad_pago,
                   'isr_ajustar': self.tipo_configuracion.isr_ajustar,
                   'isr_devolver': self.tipo_configuracion.isr_devolver,
                   'imss_mes': self.tipo_configuracion.imss_mes,
                   'imss_dias': self.tipo_configuracion.imss_dias,
                   }
            else:
                values = {
                   'periodicidad_pago': self.tipo_configuracion.periodicidad_pago,
                   'isr_ajustar': self.tipo_configuracion.isr_ajustar,
                   'isr_devolver': self.tipo_configuracion.isr_devolver,
               }
            self.update(values)


    @api.onchange('periodicidad_pago', 'tipo_configuracion')
    def _dias_pagar(self):
        if self.periodicidad_pago:
            if self.periodicidad_pago == '01':
                self.dias_pagar = 1
            elif self.periodicidad_pago == '02':
                self.dias_pagar = 7
            elif self.periodicidad_pago == '03':
                self.dias_pagar = 14
            elif self.periodicidad_pago == '04':
                if self.tipo_configuracion.tipo_pago == '01':
                    self.dias_pagar = 15
                    self.imss_dias = self.imss_mes / 2
                elif self.tipo_configuracion.tipo_pago == '02':
                    delta = self.date_end - self.date_start
                    self.dias_pagar = delta.days + 1
                    self.imss_dias = delta.days + 1
                else:
                    self.dias_pagar = 15.21
                    self.imss_dias = 15.21
            elif self.periodicidad_pago == '05':
                if self.tipo_configuracion.tipo_pago == '01':
                    self.dias_pagar = 30
                elif self.tipo_configuracion.tipo_pago == '02':
                    delta = self.date_end - self.date_start
                    self.dias_pagar = delta.days + 1
                else:
                    self.dias_pagar = 30.42
            else:
                delta = self.date_end - self.date_start
                self.dias_pagar = delta.days + 1

    @api.onchange('periodicidad_pago', 'date_end')
    def _compute_imss_mes(self):
        for batch in self:
            if batch.date_end:
                if self.tipo_configuracion:
                    if not self.tipo_configuracion.fijo_imss:
                        date_end = batch.date_end
                        batch.imss_mes = monthrange(date_end.year,date_end.month)[1]
                    else:
                        batch.imss_mes = self.tipo_configuracion.imss_mes
                else:
                    date_end = batch.date_end
                    batch.imss_mes = monthrange(date_end.year,date_end.month)[1]

    @api.onchange('nominas_mes')
    def _get_imss_dias(self):
        if self.nominas_mes and self.periodicidad_pago != '04':
            if self.tipo_configuracion:
                if not self.tipo_configuracion.fijo_imss:
                    values = {
                       'imss_dias': self.imss_mes / self.nominas_mes
                   }
                    self.update(values)
                else:
                    values = {
                       'imss_dias': self.tipo_configuracion.imss_dias
                   }
                    self.update(values)
            else:
                values = {
                     'imss_dias': self.imss_mes / self.nominas_mes
                 }
                self.update(values)

    @api.onchange('periodicidad_pago')
    def _update_nominas_mes(self):
        for batch in self:
            if self.periodicidad_pago:
                if self.periodicidad_pago == '02':
                    batch.nominas_mes = 4
                if self.periodicidad_pago == '04':
                    batch.nominas_mes = 2

    def recalcular_nomina_payslip_batch(self):
        for batch in self:
            for slip in batch.slip_ids:
                if slip.state == 'draft':
                    slip.compute_sheet()
        return True
     
    @api.depends('slip_ids.state','slip_ids.nomina_cfdi')
    def _compute_payslip_cgdi_generated(self):
        cfdi_generated = True
        for payslip in self.slip_ids:
            if payslip.state in ['draft','verify'] or not payslip.nomina_cfdi:
                cfdi_generated=False
                break
        self.all_payslip_generated = cfdi_generated 
   
    
    @api.depends('slip_ids.state')
    def _compute_payslip_cgdi_generated_draft(self):
        cfdi_generated_draft = True
        for payslip in self.slip_ids:
            if payslip.state not in ['draft']:
                cfdi_generated_draft=False
                break
        self.all_payslip_generated_draft = cfdi_generated_draft 
       
        
    def enviar_nomina(self):
        self.ensure_one()
        ctx = self._context.copy()
        template = self.env.ref('nomina_cfdi_ee.email_template_payroll', False)
        for payslip in self.slip_ids: 
            ctx.update({
                'default_model': 'hr.payslip',
                'default_res_id': payslip.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
            })
            
            vals = self.env['mail.compose.message'].onchange_template_id(template.id, 'comment', 'hr.payslip', payslip.id)
            mail_message  = self.env['mail.compose.message'].with_context(ctx).create(vals.get('value',{}))
            mail_message.send_mail()
        return True
    
    def enviar_prenomina(self):
        self.ensure_one()
        ctx = self._context.copy()
        template = self.env.ref('nomina_cfdi_ee.email_template_payroll', False)
        for payslip in self.slip_ids: 
            ctx.update({
                'default_model': 'hr.payslip',
                'default_res_id': payslip.id,
                'default_use_template': bool(template),
                'default_template_id': template.id,
                'default_composition_mode': 'comment',
            })
            
            vals = self.env['mail.compose.message'].onchange_template_id(template.id, 'comment', 'hr.payslip', payslip.id)
            mail_message  = self.env['mail.compose.message'].with_context(ctx).create(vals.get('value',{}))
            mail_message.send_mail()
        return True
    
    def timbrar_nomina(self):
        self.ensure_one()
        view = self.env.ref('nomina_cfdi_ee.timbrado_nomina_wizard')
        ctx = self.env.context.copy()
        ctx .update({'default_payslip_batch_id':self.id})
        return {
            'name': 'Timbrado De Nomina',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'timbrado.de.nomina',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

    def timbrar_nomina_wizard(self):
        self.ensure_one()
        #cr = self._cr
        payslip_obj = self.env['hr.payslip']
        start_range = self._context.get('start_range')
        end_range = self._context.get('end_range')
        for payslip_id in self.slip_ids.ids:
            payslip = payslip_obj.browse(payslip_id)
            if start_range and end_range:
                emp_no = int(payslip.employee_id.no_empleado)
                if emp_no >= start_range and emp_no <= end_range:
                    if payslip.state in ['draft','verify']:
                        payslip.action_payslip_done()
                    try:
                        if not payslip.nomina_cfdi:
                           payslip.action_cfdi_nomina_generate()
                    except Exception as e:
                       pass
            else:
                if payslip.state in ['draft','verify']:
                   payslip.action_payslip_done()
                try:
                   if not payslip.nomina_cfdi:
                      payslip.action_cfdi_nomina_generate()
                except Exception as e:
                   pass
        return

    def confirmar_nomina(self):
        self.ensure_one()
        view = self.env.ref('nomina_cfdi_ee.confirmado_nomina_wizard')
        ctx = self.env.context.copy()
        ctx .update({'default_payslip_batch_id':self.id})
        return {
            'name': 'Confirmar Nomina',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'confirmado.de.nomina',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }

    def confirmar_nomina_wizard(self):
        self.ensure_one()
        #cr = self._cr
        payslip_obj = self.env['hr.payslip']
        start_range = self._context.get('start_range')
        end_range = self._context.get('end_range')
        for payslip_id in self.slip_ids.ids:
            payslip = payslip_obj.browse(payslip_id)
            if start_range and end_range:
                emp_no = int(payslip.employee_id.no_empleado)
                if emp_no >= start_range and emp_no <= end_range:
                    if payslip.state in ['draft','verify']:
                        payslip.action_payslip_done()
            else:
                if payslip.state in ['draft','verify']:
                   payslip.action_payslip_done()
        return

    @api.onchange('periodicidad_pago', 'date_start')
    def _get_frecuencia_pago(self):
        values = {}
        #if self.freq_pago:
        #    values.update({
        #        'dias_pagar': self.freq_pago.dias_pago,
        #        #'imss_dias': self.freq_pago.dias_cotizar,
        #        })
        if self.date_start and self.dias_pagar:
            fecha_fin = self.date_start + relativedelta(days=self.dias_pagar-1)
            if self.periodicidad_pago == '04':
                if self.date_start.day > 15:
                    date = self.date_start
                    date = date+relativedelta(days=15)
                    month_last_day = monthrange(date.year,date.month)[1]
                    items = [date+relativedelta(day=month_last_day), date+relativedelta(day=15)]
                    previous_month_date = date+relativedelta(months=-1)
                    previous_month_last_day = monthrange(previous_month_date.year,previous_month_date.month)[1]
                    items.append(previous_month_date+relativedelta(day=previous_month_last_day),)
                    if date.day>15:
                        items.append(date+relativedelta(months=1,day=15))
                    fecha_fin = self.nearest_date(items,date)
            values.update({'date_end': fecha_fin})
            self.update(values)
        #if values:
        #    self.update(values)

    @api.model
    def nearest_date(self, items, pivot):
        return min(items, key=lambda x: abs(x - pivot))

    @api.onchange('estructura')
    def _set_aguinaldo_dates(self):
        if self.estructura:
            if self.estructura.name == 'Aguinaldo':
                fecha_fin = datetime(date.today().year, 12, 31)
                fecha_inicio = datetime(date.today().year, 1, 1)
                values = {
                    'date_end': fecha_fin.strftime('%Y-%m-%d'),
                    'date_start': fecha_inicio.strftime('%Y-%m-%d'),
                }
                self.update(values)


class OtrasEntradas(models.Model):
    _name = 'otras.entradas'
    _description = 'OtrasEntradas'

    form_id = fields.Many2one('hr.payslip.run', required=True) 
    monto = fields.Float('Monto') 
    descripcion = fields.Char('Descripcion') 
    codigo = fields.Char('Codigo')

class ConfiguracionNomina(models.Model):
    _name = 'configuracion.nomina'
    _rec_name = "name"
    _description = 'ConfiguracionNomina'

    name = fields.Char(string='Nombre', required=True)
    tipo_pago = fields.Selection(
        selection=[('01', 'Por periodo'), 
                   ('02', 'Por día'),
                   ('03', 'Mes proporcional'),],
        string=_('Conteo de días'),
    )
    fijo_imss = fields.Boolean(string='Dias fijos')
    imss_dias = fields.Float(string='Dias a cotizar en la nómina', store=True)
    imss_mes = fields.Float(string='Dias en el mes', store=True)
    isr_ajustar = fields.Boolean(string='Ajustar ISR en cada nómina', default= True)
    isr_devolver = fields.Boolean(string='Devolver ISR')
    periodicidad_pago = fields.Selection(
        selection=[('01', 'Diario'), 
                   ('02', 'Semanal'), 
                   ('03', 'Catorcenal'),
                   ('04', 'Quincenal'), 
                   ('05', 'Mensual'),
                   ('06', 'Bimensual'), 
                   ('07', 'Unidad obra'),
                   ('08', 'Comisión'), 
                   ('09', 'Precio alzado'), 
                   ('10', 'Pago por consignación'), 
                   ('99', 'Otra periodicidad'),],
        string=_('Periodicidad de pago CFDI'), required=True
    )

# -*- encoding: utf-8 -*-
#
import sys
if sys.version_info[0] >= 3:
    unicode = str
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from base64 import b64decode as b64dec, b64encode as b64enc
from lxml import etree as et
from zipfile import ZipFile
import requests
import json
import urllib
import time
import os
import zipfile
import tempfile
import re
import io
import base64
import lxml.etree
import calendar
import datetime
from xml.dom.minidom import parse, parseString
import logging

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    filename = fields.Char(string='Archivo', size=128)
    primary_file= fields.Binary(string='Archivo Plano', filename="filename")

    def generate_file_zip(self):
        
        #rutaarchivo = "/tmp/"
        self.filename = self.name +  '-' + str(self.date_start) + '-' + str(self.date_end) + '.zip'
        
        zipDoc = ZipFile(self.filename, 'w')
        for nominas in self.slip_ids:
            adjuntos = self.env['ir.attachment'].search([('res_model', '=', 'hr.payslip'), ('res_id', '=', nominas.id), ('name', 'ilike', '.xml')])
            for att in adjuntos:

                xml_data = base64.b64decode(att.datas)
                zipDoc.writestr(att.name, xml_data, zipfile.ZIP_DEFLATED)              
                

        zipDoc.close()
        
        self.write({'primary_file':  b64enc(open(self.filename, 'rb').read()), 'filename': self.filename})

# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class StockPicking(osv.Model):
    _inherit = 'stock.picking'
    
    _columns = {
        'xx_delivery_date': fields.date(string='Delivery date'),
        #'xx_payment_method': fields.selection([('cash', 'Cash'),
        #                                       ('visa', 'Visa')],
        #                                      string='Payment method')
        'xx_payment_method': fields.many2one('xx.payment.method',
                                             string='Payment method'),
                'xx_warranty_period': fields.many2one('xx.warranty.period',
                                              string='Warranty period'),
        'xx_insurance_method': fields.many2one('xx.insurance.method',
                                              string='Insurance method')
    }
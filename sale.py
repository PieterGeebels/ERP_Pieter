# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow

class SaleOrder(osv.Model):
    _inherit = 'sale.order'

    _columns = {
        'xx_delivery_date': fields.date(string='Delivery date'),
        #'xx_payment_method': fields.selection([('cash', 'Cash'),
        #                                       ('visa', 'Visa')],
        #                                      string='Payment method')
        'xx_payment_method': fields.many2one('xx.payment.method',
                                             string='Payment method'),
        'xx_warranty_method': fields.many2one('xx.warranty.method',
                                              string='Warranty method')
    }
    
class PaymentMethod(osv.Model):
    _name = 'xx.payment.method'
    
    _columns = {
        'name': fields.char(size=128, string='Name'),
        'writeoff': fields.boolean(string='Writeoff'),
        'sale_ids': fields.one2many('sale.order', 'xx_payment_method', 
                                    string='Sale orders')
    }
    
    _defaults = {
        'writeoff': False,
    }
    
class WarrantyMethod(osv.Model):
    _name = 'xx.warranty.method'
    
    _rec_name = 'xx_name'
    
    _columns = {
        'xx_name': fields.char(size=128, string='Manufacturer'),
        'xx_warranty': fields.selection([('1', '1 Jaar'),
                                         ('2', '2 Jaar')], string='Period'),
        'xx_amount': fields.float(string='Amount')
    }
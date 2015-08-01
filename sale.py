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
 
        'xx_payment_method': fields.many2one('xx.payment.method',
                                             string='Payment method'),

        'xx_insurance_method': fields.many2one('xx.insurance.method',
                                              string='Insurance method'),
 
}
class InsuranceMethod(osv.Model):
    _name = 'xx.insurance.method'
   
    _rec_name = 'xx_insurance_name'
   
    _columns = {
        'xx_insurance_name': fields.char(size=128, string='Insurance'),
        'xx_insurance_percentage': fields.float(string='Percentage'),
        'xx_sale_ids': fields.one2many('sale.order', 'xx_insurance_method',
                                        string='Sale orders')
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
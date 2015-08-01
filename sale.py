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
 
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
    for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
        result[line.order_id.id] = True
        return result.keys()
    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                             'amount_untaxed': 0.0,
                             'amount_tax': 0.0,
                             #aangepast
                             'xx_insurance_percentage':0.0,
                             'xx_insurance_percentages':0.0,
                             'xx_insurance_cost':0.0,
                             'xx_insurance_costs':0.0,
                             'amount_total': 0.0,
                             }
            val = val1 = val2= 0.0
            cur = order.pricelist_id.currency_id
            #aangepast
            res[order.id]['xx_insurance_percentage'] = cur_obj.round(cr,uid,cur,order.xx_insurance_method.xx_insurance_percentage)
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
                val2 +=( res[order.id]['amount_untaxed'] ) * ( res[order.id]['xx_insurance_percentage']/100) + res[order.id]['amount_tax']
                res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
                res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
                #tonen van percentage en kost op sale order
                order.xx_insurance_percentages=order.xx_insurance_method.xx_insurance_percentage
                order.xx_insurance_costs=res[order.id]['amount_untaxed'] * ( res[order.id]['xx_insurance_percentage']/100)
                #het totaal bedrag van factuur laten aanpassen + verzekeringskost
                res[order.id]['amount_total'] =res[order.id]['amount_tax']+res[order.id]['amount_untaxed'] * (1+ res[order.id]['xx_insurance_percentage']/100)
                return res
            def _prepare_invoice(self, cr, uid, order, lines, context=None):
                """Prepare the dict of values to create the new invoice for a
    sales order. This method may be overridden to implement custom
    invoice generation (making sure to call super() to establish
    a clean extension chain).
    :param browse_record order: sale.order record to invoice
    :param list(int) line: list of invoice line IDs that must be
    attached to the invoice
    :return: dict of value to create() the invoice
    """
    if context is None:
        context = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid,
                                                              [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
                                                              limit=1)
        if not journal_ids:
            raise osv.except_osv(_('Error!'),
                                 _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
            invoice_vals = {
                            'name': order.client_order_ref or '',
                            'origin': order.name,
                            'amount_untaxed' : order.amount_untaxed,
                            'amount_total' : order.amount_total,
                            'amount_tax' : order.amount_tax,
                            'type': 'out_invoice',
                            'reference': order.client_order_ref or order.name,
                            'account_id': order.partner_id.property_account_receivable.id,
                            'partner_id': order.partner_invoice_id.id,
                            'journal_id': journal_ids[0],
                            'invoice_line': [(6, 0, lines)],
                            'currency_id': order.pricelist_id.currency_id.id,
                            'comment': order.note,
                            'payment_term': order.payment_term and order.payment_term.id or False,
                            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
                            'date_invoice': context.get('date_invoice', False),
                            'company_id': order.company_id.id,
                            'user_id': order.user_id and order.user_id.id or False,
                            'section_id' : order.section_id.id,
                            #tonen van welke verzekerings methode op factuur
                            'xx_insurance_method' : order.xx_insurance_method.id,
                            #tonen percentage verzekering op factuur
                            'xx_insurance_percentage' : order.xx_insurance_method.xx_insurance_percentage,
                            #tonen verzekering kost op factuur
                            'xx_insurance_cost' : (order.amount_untaxed ) * ( order.xx_insurance_method.xx_insurance_percentage/100)
                            }
            # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
            invoice_vals.update(self._inv_get(cr, uid, order, context=context))
            return invoice_vals
        def _make_invoice(self, cr, uid, order, lines, context=None):
            inv_obj = self.pool.get('account.invoice')
            obj_invoice_line = self.pool.get('account.invoice.line')
            if context is None:
                context = {}
                invoiced_sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', order.id), ('invoiced', '=', True)], context=context)
                from_line_invoice_ids = []
                for invoiced_sale_line_id in self.pool.get('sale.order.line').browse(cr, uid, invoiced_sale_line_ids, context=context):
                    for invoice_line_id in invoiced_sale_line_id.invoice_lines:
                        if invoice_line_id.invoice_id.id not in from_line_invoice_ids:
                            from_line_invoice_ids.append(invoice_line_id.invoice_id.id)
                            for preinv in order.invoice_ids:
                                if preinv.state not in ('cancel',) and preinv.id not in from_line_invoice_ids:
                                    for preline in preinv.invoice_line:
                                        inv_line_id = obj_invoice_line.copy(cr, uid, preline.id, {'invoice_id': False, 'price_unit': -preline.price_unit})
                                        lines.append(inv_line_id)
                                        inv = self._prepare_invoice(cr, uid, order, lines, context=context)
                                        inv_id = inv_obj.create(cr, uid, inv, context=context)
                                        data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv['payment_term'], time.strftime(DEFAULT_SERVER_DATE_FORMAT))
                                        if data.get('value', False):
                                            inv_obj.write(cr, uid, [inv_id], data['value'], context=context)
                                            inv_obj.button_compute(cr, uid, [inv_id])
                                            return inv_id
                                        _columns = {
                                                    'xx_delivery_date': fields.date(string='Delivery date'),
                                                    'xx_payment_method': fields.many2one('xx.payment.method',
                                                                                         string='Payment method'),
                                                    
                                                    # 'xx_insurance_price': fields.many2one('xx.insurance.price',
                                                    # string='Insurance Price')
                                                    #verzekeringsmethode
                                                    'xx_insurance_method': fields.many2one('xx.insurance.method',
                                                                                           string='Insurance method'),
                                                    #verzekeringspercentage
                                                    'xx_insurance_percentages': fields.float(string='Percentage'),
                                                    #verzekeringskost
                                                    'xx_insurance_costs' : fields.float(string='Insurance Cost'),
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
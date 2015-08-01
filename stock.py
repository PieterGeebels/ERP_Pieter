# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp import SUPERUSER_ID, api

class StockMove(osv.Model):
    _inherit = "stock.move"
    
    @api.cr_uid_ids_context
    def _picking_assign(self, cr, uid, move_ids, procurement_group, location_from, location_to, context=None):
        """Assign a picking on the given move_ids, which is a list of move supposed to share the same procurement_group, location_from and location_to
        (and company). Those attributes are also given as parameters.
        """
        pick_obj = self.pool.get("stock.picking")
        picks = pick_obj.search(cr, uid, [
                ('group_id', '=', procurement_group),
                ('location_id', '=', location_from),
                ('location_dest_id', '=', location_to),
                ('state', 'in', ['draft', 'confirmed', 'waiting'])], context=context)
        if picks:
            pick = picks[0]
        else:
            move = self.browse(cr, uid, move_ids, context=context)[0]
            values = {
                      #insurance methode toegevoegd, normaalgezien ook warrant, maar het bleek dat de error ergens uit deze richting kwam.
                      #deze code is echter standaard, dus ik heb mijn custom warrant maar weggedaan
                'xx_insurance_method': move.procurement_id.sale_line_id.order_id.xx_insurance_method.id,
                'xx_delivery_date': move.procurement_id.sale_line_id.order_id.xx_delivery_date,
                'xx_payment_method': move.procurement_id.sale_line_id.order_id.xx_payment_method.id,                
                'origin': move.origin,
                'company_id': move.company_id and move.company_id.id or False,
                'move_type': move.group_id and move.group_id.move_type or 'direct',
                'partner_id': move.partner_id.id or False,
                'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
            }
            pick = pick_obj.create(cr, uid, values, context=context)
        return self.write(cr, uid, move_ids, {'picking_id': pick}, context=context)

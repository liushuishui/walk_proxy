# -*- coding:utf-8 -*-
# -------------------------------------
# 请输入该文件的说明
# -------------------------------------
from odoo import fields, models, api
from datetime import datetime
import random


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, value):
        dt = datetime.now().strftime('%Y%m%d%H%M%S')
        salt = ''
        for each in range(3):
            salt += str(random.randint(0, 9))
        name = '%s%s%s' % ('S', dt, salt)
        value.update({'name': name})
        return super(SaleOrderInherit, self).create(value)
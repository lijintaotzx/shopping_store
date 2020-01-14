# coding=utf-8
import sys
sys.path.append('/Users/tzx/workspace/tarena')

from shopping_store.cashier.views import CashierHandler

cashier = CashierHandler()
cashier.start()

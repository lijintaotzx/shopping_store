# coding=utf-8
import sys
sys.path.append('/Users/tzx/workspace/tarena')

from shopping_store.customer.views import CustomerHandler

customer = CustomerHandler()
customer.start()

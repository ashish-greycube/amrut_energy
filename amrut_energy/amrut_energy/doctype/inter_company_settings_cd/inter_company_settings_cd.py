# Copyright (c) 2023, GreyCube Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class InterCompanySettingsCD(Document):
	def validate(self):
		self.check_duplicate_combination()

	# def check_duplicate_combination(self):
	# 	check_duplicates=[]
	# 	for row in self.company_bank_mappings:
	# 		unique_value=[row.sender_company,row.sender_bank_account,row.receiver_company]
	# 		if unique_value in check_duplicates:
	# 			frappe.throw(_('Please remove duplicate at row : {0}'.format(frappe.bold(row.idx))))
	# 		else:
	# 			check_duplicates.append(unique_value)

	def check_duplicate_combination(self):
		check_duplicates = set()
		for row in self.company_bank_mappings:
			unique_value = (row.sending_company, row.sending_bank_account, row.receiving_company)
			if unique_value in check_duplicates:
				frappe.throw(_('Please remove duplicate at row : {0}'.format(frappe.bold(row.idx))))
			else:
				check_duplicates.add(unique_value)

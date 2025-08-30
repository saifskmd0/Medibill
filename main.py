import sys, os
import sqlite3
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QFileDialog, QVBoxLayout, QStyle, QHeaderView, 
                            QDesktopWidget, QMessageBox, QPushButton, 
                            QStyledItemDelegate, QWidget, QHBoxLayout, QComboBox, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlQuery
from PyQt5.QtCore import QSize, Qt, QDate, QModelIndex, QSize

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from main_ui import Ui_MainWindow

db = QSqlDatabase("QSQLITE")
db.setDatabaseName("pharmacy.sqlite")
db.open()

class MplCanvas(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)
		super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		super().__init__()
		self.setupUi(self)
		self.setWindowTitle("MediBill")
		#self.showMaximized()
		self.stackedWidget.setCurrentIndex(0)

		#init Setup
		self.editFlag = False
		self.company_id_Flag = 0
		self.loadPharmacy()

		self.prodFlag = False
		self.prodId = 0

		self.invoice_id_Flag = 0

		self.update_invoice_Flag = False

		#Insert Invoice Date
		self.InvoiceDate.setDate(QDate.currentDate())


		self.canvas = MplCanvas(self, width=7, height=2.5, dpi=100)
		self.Canvaslayout = QVBoxLayout()
		self.Canvaslayout.addWidget(self.canvas)
		self.plot_sales.setLayout(self.Canvaslayout)
		

		#LogIn Page Signals
		self.createBtn.pressed.connect(self.createCompany)
		self.LogInBtn.pressed.connect(self.logIn)

		#Sidebar Signals
		self.logOutBtn.pressed.connect(self.logOut)
		self.dashboardBtn.pressed.connect(self.toDashboard)
		self.invoiceBtn.pressed.connect(self.toInvoice)
		self.invoiceBtn.pressed.connect(self.invoiceEntries)
		self.invoiceBtn.pressed.connect(self.invNo)
		self.inventoryBtn.pressed.connect(self.toInventory)
		self.inventoryBtn.pressed.connect(self.showInventoryProducts)
		self.accountSetupBtn.pressed.connect(self.toAccount)

		#Create Company Page Signals
		self.createCancelBtn.pressed.connect(self.createCompanyCancel)
		self.createSaveBtn.pressed.connect(self.createCompanySave)

		#Inventory Signals
		self.addInvBtn.setAutoDefault(True)
		self.addInvBtn.pressed.connect(self.addProduct)
		self.clearEBtn.pressed.connect(self.clrProduct)

		self.addInvBtn.pressed.connect(self.inventory_summary)

		self.StockItems.doubleClicked.connect(self.editProduct)

		self.searchBtn.pressed.connect(self.searchProduct)

		self.nameE.editingFinished.connect(self.is_prod_exists)

		
		# Item Searchbox
		self.productInput.setEditable(True)
		self.productInput.setInsertPolicy(QComboBox.NoInsert)

		# Combobox Search
		self.load_initial_items()

		self.productInput.lineEdit().editingFinished.connect(self.filter_items)

		self.addPBtn.pressed.connect(self.addtoInv)
		#self.addPBtn.pressed.connect(self.addInvDetails)

		self.deleteItem.pressed.connect(self.delItem)

		self.discountV.editingFinished.connect(self.discounted)

		## Save Invoice Button
		self.SaveInvoice.pressed.connect(self.save_invoice)

		# InvoiceNumber Change
		self.InvoiceNumber.editingFinished.connect(self.update_invoice)

		# Cancel Invoice Button 
		self.cancelInvoice.pressed.connect(self.cance_invoice)



	###
	## Create Company Page Slots
	###
	#Create Company
	def createCompany(self):
		self.stackedWidget.setCurrentIndex(2)


	#Create Company Cancel Button Pressed
	def createCompanyCancel(self):
		self.cNameInp.clear()
		self.cAdd1Inp.clear()
		self.cAdd2Inp.clear()
		self.cCityInp.clear()
		self.cStateInp.clear()
		self.cPinInp.clear()
		self.cPhoneInp.clear()
		self.cMailInp.clear()
		self.cDLInp.clear()
		self.cGSTInp.clear()
		self.cPanInp.clear()
		self.cRegNameInp.clear()
		self.cBankNameInp.clear()
		self.cAccNoInp.clear()
		self.cIFSCInp.clear()
		self.cBranchInp.clear()
		self.cPassInp.clear()
		self.cPassCInp.clear()
		self.stackedWidget.setCurrentIndex(0)

	#Create Company Save Button Pressed
	def createCompanySave(self):
		if self.editFlag:
			query = QSqlQuery(db=db)
			query.prepare(f"""UPDATE CompanyDetails SET company_name=?, 
				address_line1=?, 
				address_line2=?, 
				city=?, 
				state=?, 
				pin_code=?, 
				phone=?, 
				email=?, 
				dl_number=?, 
				gst_number=?, 
				pan_number=?, 
				registered_name=?, 
				bank_name=?, 
				account_number=?, 
				ifsc_code=?, 
				branch=?, 
				password=? 
				WHERE company_id = '{self.company_id_Flag}'
				""")

			query.bindValue(0, str(self.cNameInp.text()));
			query.bindValue(1, str(self.cAdd1Inp.text()));
			query.bindValue(2, str(self.cAdd2Inp.text()));
			query.bindValue(3, str(self.cCityInp.text()));
			query.bindValue(4, str(self.cStateInp.text()));
			query.bindValue(5, str(self.cPinInp.text()));
			query.bindValue(6, str(self.cPhoneInp.text()));
			query.bindValue(7, str(self.cMailInp.text()));
			query.bindValue(8, str(self.cDLInp.text()));
			query.bindValue(9, str(self.cGSTInp.text()));
			query.bindValue(10, str(self.cPanInp.text()));
			query.bindValue(11, str(self.cRegNameInp.text()));
			query.bindValue(12, str(self.cBankNameInp.text()));
			query.bindValue(13, str(self.cAccNoInp.text()));
			query.bindValue(14, str(self.cIFSCInp.text()));
			query.bindValue(15, str(self.cBranchInp.text()));
			query.bindValue(16, str(self.cPassInp.text()));

		else:
			query = QSqlQuery(db=db)
			query.prepare("""INSERT INTO CompanyDetails(company_name, 
				address_line1, 
				address_line2, 
				city, 
				state, 
				pin_code, 
				phone, 
				email, 
				dl_number, 
				gst_number, 
				pan_number, 
				registered_name, 
				bank_name, 
				account_number, 
				ifsc_code, 
				branch, 
				password) 
				VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
				""")

			query.bindValue(0, str(self.cNameInp.text()));
			query.bindValue(1, str(self.cAdd1Inp.text()));
			query.bindValue(2, str(self.cAdd2Inp.text()));
			query.bindValue(3, str(self.cCityInp.text()));
			query.bindValue(4, str(self.cStateInp.text()));
			query.bindValue(5, str(self.cPinInp.text()));
			query.bindValue(6, str(self.cPhoneInp.text()));
			query.bindValue(7, str(self.cMailInp.text()));
			query.bindValue(8, str(self.cDLInp.text()));
			query.bindValue(9, str(self.cGSTInp.text()));
			query.bindValue(10, str(self.cPanInp.text()));
			query.bindValue(11, str(self.cRegNameInp.text()));
			query.bindValue(12, str(self.cBankNameInp.text()));
			query.bindValue(13, str(self.cAccNoInp.text()));
			query.bindValue(14, str(self.cIFSCInp.text()));
			query.bindValue(15, str(self.cBranchInp.text()));
			query.bindValue(16, str(self.cPassInp.text()));

		query.exec_();
		db.commit()

		#Clear Entries
		self.cNameInp.clear()
		self.cAdd1Inp.clear()
		self.cAdd2Inp.clear()
		self.cCityInp.clear()
		self.cStateInp.clear()
		self.cPinInp.clear()
		self.cPhoneInp.clear()
		self.cMailInp.clear()
		self.cDLInp.clear()
		self.cGSTInp.clear()
		self.cPanInp.clear()
		self.cRegNameInp.clear()
		self.cBankNameInp.clear()
		self.cAccNoInp.clear()
		self.cIFSCInp.clear()
		self.cBranchInp.clear()
		self.cPassInp.clear()
		self.cPassCInp.clear()

		self.loadPharmacy()
		query = QSqlQuery(db=db)
		query.exec_(f"SELECT company_id FROM CompanyDetails ORDER BY company_id")

		while query.next():
			self.CompanyId = int(query.value(0))
		self.stackedWidget.setCurrentIndex(0)


	###
	## Log In || Log Out Button Slot
	###

	def logIn(self):
		CompanySelected = self.companyList.currentText()

		query = QSqlQuery(db=db)
		query.exec_(f"SELECT company_id, company_name, password FROM CompanyDetails WHERE company_name = '{CompanySelected}'")

		while query.next():
			tempPassWord = query.value(2)
			self.company_id = query.value(0)			

		if self.LogInPass.text() == tempPassWord:
			self.LogInPass.clear()
			self.stackedWidget.setCurrentIndex(1)
			self.toDashboard()
			self.company_id_Flag = self.company_id
			self.cNameData.setText(str(self.companyList.currentText()))
			self.recent_invoices()
			self.inventory_summary()
			self.expiring_prod()
			self.showMaximized()
			self.plot_Sale()

		else:
			alert = QMessageBox()
			alert.setIcon(QMessageBox.Critical)
			alert.setText("Wrong Password!")
			alert.setWindowTitle("Alert")
			alert.exec_()
		


	def logOut(self):
		self.adjustSize()
		self.qr = self.frameGeometry()
		self.cp = QDesktopWidget().availableGeometry().center()
		self.qr.moveCenter(self.cp)
		self.move(self.qr.topLeft())
		self.stackedWidget.setCurrentIndex(0)

	def loadPharmacy(self):
		self.CompaniesModel = QSqlQueryModel()
		self.CompaniesModel.setQuery("SELECT company_id, company_name, password FROM CompanyDetails", db)

		self.companyList.setModel(self.CompaniesModel)
		self.companyList.setModelColumn(1)

	###
	## Sidebar Slots
	###

	def toDashboard(self):
		self.invoiceBtn.setChecked(False)
		self.inventoryBtn.setChecked(False)
		self.stackedWidget_2.setCurrentIndex(0)
		self.top_prod()
		self.recent_invoices()
		self.inventory_summary()
		self.expiring_prod()
		self.plot_Sale()

	def toInvoice(self):
		self.dashboardBtn.setChecked(False)
		self.inventoryBtn.setChecked(False)
		self.stackedWidget_2.setCurrentIndex(1)
		self.invoiceEntries()
		self.gst_amt()
		self.gross_amt()

	def toInventory(self):
		self.dashboardBtn.setChecked(False)
		self.invoiceBtn.setChecked(False)
		self.stackedWidget_2.setCurrentIndex(2)
		self.inventory_summary()

	def toAccount(self):
		self.editFlag = True
		self.adjustSize()
		self.qr = self.frameGeometry()
		self.cp = QDesktopWidget().availableGeometry().center()
		self.qr.moveCenter(self.cp)
		self.move(self.qr.topLeft())
		self.stackedWidget.setCurrentIndex(2)

		query = QSqlQuery(db=db)
		query.exec_(f"""SELECT company_name, 
			address_line1, 
			address_line2, 
			city, 
			state, 
			pin_code, 
			phone, 
			email, 
			dl_number, 
			gst_number, 
			pan_number, 
			registered_name, 
			bank_name, 
			account_number, 
			ifsc_code, 
			branch 
			FROM CompanyDetails 
			WHERE company_id = '{self.company_id_Flag}'
			""")

		while query.next():
			self.cNameInp.setText(str(query.value(0)))
			self.cAdd1Inp.setText(str(query.value(1)))
			self.cAdd2Inp.setText(str(query.value(2)))
			self.cCityInp.setText(str(query.value(3)))
			self.cStateInp.setText(str(query.value(4)))
			self.cPinInp.setText(str(query.value(5)))
			self.cPhoneInp.setText(str(query.value(6)))
			self.cMailInp.setText(str(query.value(7)))
			self.cDLInp.setText(str(query.value(8)))
			self.cGSTInp.setText(str(query.value(9)))
			self.cPanInp.setText(str(query.value(10)))
			self.cRegNameInp.setText(str(query.value(11)))
			self.cBankNameInp.setText(str(query.value(12)))
			self.cAccNoInp.setText(str(query.value(13)))
			self.cIFSCInp.setText(str(query.value(14)))
			self.cBranchInp.setText(str(query.value(15)))
		

	###
	## Inventory Page Slots
	###
	def addProduct(self):
		productDict={
		"product_name": str(self.nameE.text()), 
		"quantity": str(self.qtyE.text()), 
		"pack": str(self.packE.text()), 
		"hsn": str(self.hsnE.text()), 
		"mfg_by": str(self.mfgE.text()), 
		"batch": str(self.batchE.text()), 
		"expiry": str(self.expiryE.text()), 
		"mrp": str(self.mrpE.text()), 
		"rate": str(self.rateE.text()), 
		"sch": str(self.schE.text()), 
		"gst": str(self.gstE.text())
		}

		for key in productDict:
			if productDict[key] == '':
				alert = QMessageBox()
				alert.setIcon(QMessageBox.Critical)
				alert.setText(f"Check Form Entry! There are empty values in !\n\n\n'{key}'' field.")
				alert.setWindowTitle("Alert")
				alert.exec_()
				break

		try:
			productDict["quantity"] = int(self.qtyE.text())
			productDict["mrp"] = int(self.mrpE.text())
			productDict["rate"] = int(self.rateE.text())
			productDict["gst"] = int(self.gstE.text())
			
			if self.prodFlag:
				query = QSqlQuery(db=db)
				query.prepare(f"""UPDATE Products SET product_name=?, 
					quantity=?, 
					pack=?, 
					hsn=?, 
					mfg_by=?, 
					batch=?, 
					expiry=?, 
					mrp=?, 
					rate=?, 
					sch=?, 
					gst=? 
					WHERE product_id = {self.prodId}
					""")
				query.bindValue(0, productDict["product_name"]);
				query.bindValue(1, productDict["quantity"]);
				query.bindValue(2, productDict["pack"]);
				query.bindValue(3, productDict["hsn"]);
				query.bindValue(4, productDict["mfg_by"]);
				query.bindValue(5, productDict["batch"]);
				query.bindValue(6, productDict["expiry"]);
				query.bindValue(7, productDict["mrp"]);
				query.bindValue(8, productDict["rate"]);
				query.bindValue(9, productDict["sch"]);
				query.bindValue(10, productDict["gst"]);

				query.exec_();
				db.commit()

			else:
				query = QSqlQuery(db=db)
				query.prepare("""INSERT INTO Products(product_name, 
					quantity, 
					pack, 
					hsn, 
					mfg_by, 
					batch, 
					expiry, 
					mrp, 
					rate, 
					sch, 
					gst, 
					company_id) 
				VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
				""")

				query.bindValue(0, productDict["product_name"]);
				query.bindValue(1, productDict["quantity"]);
				query.bindValue(2, productDict["pack"]);
				query.bindValue(3, productDict["hsn"]);
				query.bindValue(4, productDict["mfg_by"]);
				query.bindValue(5, productDict["batch"]);
				query.bindValue(6, productDict["expiry"]);
				query.bindValue(7, productDict["mrp"]);
				query.bindValue(8, productDict["rate"]);
				query.bindValue(9, productDict["sch"]);
				query.bindValue(10, productDict["gst"]);
				query.bindValue(11, str(self.company_id_Flag));

				query.exec_();
				db.commit()


			self.clrProduct()
			self.showInventoryProducts()

		except:
			alert = QMessageBox()
			alert.setIcon(QMessageBox.Warning)
			alert.setText(f"Check Form Entry! \n\n\n 'Quantity', 'MRP', 'Rate', 'GST' field must be a number.")
			alert.setWindowTitle("Alert")
			alert.exec_()


	def showInventoryProducts(self):
		self.InventoryTableView = QSqlTableModel(db=db)
		self.InventoryTableView.setTable("Products")
		self.StockItems.setModel(self.InventoryTableView)
		self.InventoryTableView.setFilter(f"company_id = {self.company_id_Flag} ORDER BY product_id DESC")
		self.InventoryTableView.setHeaderData(1,Qt.Horizontal, "Name")
		self.InventoryTableView.setHeaderData(2,Qt.Horizontal, "Quantity")
		self.InventoryTableView.setHeaderData(5,Qt.Horizontal, "MFG By")
		self.InventoryTableView.setHeaderData(7,Qt.Horizontal, "Expiry")
		self.InventoryTableView.setHeaderData(8,Qt.Horizontal, "MRP")
		self.InventoryTableView.setHeaderData(11,Qt.Horizontal, "GST@")
		self.StockItems.hideColumn(0)
		self.StockItems.hideColumn(3)
		self.StockItems.hideColumn(4)
		self.StockItems.hideColumn(6)
		self.StockItems.hideColumn(9)
		self.StockItems.hideColumn(10)
		self.StockItems.hideColumn(12)
		self.StockItems.hideColumn(13)

		self.StockItems.setColumnWidth(1, 180)
		self.StockItems.horizontalHeader().setStretchLastSection(True)
		self.InventoryTableView.select()

		self.StockItems.setEditTriggers(self.StockItems.NoEditTriggers)

	def editProduct(self, index: QModelIndex):
		row = index.row()
		model = index.model()
		rowValues = [model.index(row,col).data() for col in range(model.columnCount())]

		#print(rowValues)

		self.nameE.setText(rowValues[1])
		self.qtyE.setText(str(rowValues[2]))
		self.packE.setText(rowValues[3])
		self.hsnE.setText(rowValues[4])
		self.mfgE.setText(rowValues[5])
		self.batchE.setText(rowValues[6])
		self.expiryE.setDate(QDate.fromString(rowValues[7],"dd/MM/yyyy"))
		self.mrpE.setText(str(rowValues[8]))
		self.rateE.setText(str(rowValues[9]))
		self.schE.setText(rowValues[10])
		self.gstE.setText(str(rowValues[11]))

		self.addInvBtn.setText("Update")
		self.prodFlag = True
		self.prodId = rowValues[0]

	def clrProduct(self):
		self.nameE.clear()
		self.qtyE.clear()
		self.packE.clear()
		self.hsnE.clear()
		self.mfgE.clear()
		self.batchE.clear()
		self.expiryE.setDate(QDate(1,1,2025))
		self.mrpE.clear()
		self.rateE.clear()
		self.schE.clear()
		self.gstE.clear()

		self.addInvBtn.setText("Add To Inventory >>")
		self.prodFlag = False

	def searchProduct(self):
		self.InventoryTableView.setFilter(f"company_id = {self.company_id_Flag} AND product_name LIKE '%{self.searchE.text()}%' ORDER BY product_id DESC")
	
	def invoiceEntries(self):
		##
		## Invoice Table Model
		##
		self.invoiceItemModel = QSqlTableModel(db=db)
		self.invoiceItemModel.setTable("Invoice_Items")
		self.InvoiceItemTable.setModel(self.invoiceItemModel)
		self.invoiceItemModel.setFilter(f"invoice_no = {self.InvoiceNumber.text()} AND company_id = {self.company_id_Flag}")
		self.invoiceItemModel.setEditStrategy(QSqlTableModel.OnManualSubmit)
		self.invoiceItemModel.setHeaderData(4,Qt.Horizontal, "Name")
		self.invoiceItemModel.setHeaderData(5,Qt.Horizontal, "Quantity")
		self.invoiceItemModel.setHeaderData(6,Qt.Horizontal, "Pack")
		self.invoiceItemModel.setHeaderData(7,Qt.Horizontal, "HSN")
		self.invoiceItemModel.setHeaderData(8,Qt.Horizontal, "MFG By")
		self.invoiceItemModel.setHeaderData(9,Qt.Horizontal, "Batch")
		self.invoiceItemModel.setHeaderData(10,Qt.Horizontal, "Expiry")
		self.invoiceItemModel.setHeaderData(11,Qt.Horizontal, "MRP")
		self.invoiceItemModel.setHeaderData(12,Qt.Horizontal, "Rate")
		self.invoiceItemModel.setHeaderData(13,Qt.Horizontal, "SCH")
		self.invoiceItemModel.setHeaderData(14,Qt.Horizontal, "GST%")
		#self.invoiceItemModel.setHeaderData(15,Qt.Horizontal, "Amount")
		self.InvoiceItemTable.hideColumn(0)
		self.InvoiceItemTable.hideColumn(1)
		self.InvoiceItemTable.hideColumn(2)
		self.InvoiceItemTable.hideColumn(3)
		self.InvoiceItemTable.hideColumn(15)
		self.invoiceItemModel.select()

		self.InvoiceItemTable.setColumnWidth(4, 150)

		self.InvoiceItemTable.horizontalHeader().setStretchLastSection(True)

		self.invoiceItemModel.layoutChanged.emit()

		self.InvoiceItemTable.update()

		self.invoiceItemModel.dataChanged.connect(self.calculate)

	"""def loadItems(self):
		self.ItemModel = QSqlQueryModel()
		self.ItemModel.setQuery("SELECT product_id, product_name FROM Products", db)

		self.productInput.setModel(self.ItemModel)
		self.productInput.setModelColumn(1)"""

	def load_initial_items(self):
		"""Load all distinct items from the database column"""
		try:
			conn = sqlite3.connect("pharmacy.sqlite")
			cursor = conn.cursor()
			query = f"SELECT DISTINCT product_name FROM Products ORDER BY product_name LIMIT 10"
			cursor.execute(query)
			items = [str(item[0]) for item in cursor.fetchall()]
			self.productInput.addItems(items)
			conn.close()
		except sqlite3.Error as e:
			print(f"Database error: {e}")
    
	def filter_items(self):
		"""Filter items based on user input"""
		current_text = self.productInput.lineEdit().text()
    		    
		try:
			conn = sqlite3.connect("pharmacy.sqlite")
			cursor = conn.cursor()
			query = f"""
				SELECT DISTINCT product_name 
				FROM Products 
				WHERE product_name LIKE ? 
				ORDER BY product_name LIMIT 10
			"""
			cursor.execute(query, (f'%{current_text}%',))
			
			# Clear and repopulate the combobox
			self.productInput.clear()
			items = [str(item[0]) for item in cursor.fetchall()]
			self.productInput.addItems(items)
			
			# Restore the typed text and show the dropdown
			self.productInput.lineEdit().setText(current_text)
			self.productInput.showPopup()
			
			conn.close()
		except sqlite3.Error as e:
			print(f"Database error: {e}")

	def addtoInv(self):
		itemsDict = {
		"product_id": "",
		"company_id": "",
		"product_name": "", 
		"quantity": "", 
		"pack": "", 
		"hsn": "", 
		"mfg_by": "", 
		"batch": "", 
		"expiry": "", 
		"mrp": "", 
		"rate": "", 
		"sch": "", 
		"gst": ""
		}

		query = QSqlQuery(db=db)
		query.exec_(f"""SELECT 
			product_id,
			company_id,
			product_name,
			quantity, 
			pack, 
			hsn, 
			mfg_by, 
			batch, 
			expiry, 
			mrp, 
			rate, 
			sch, 
			gst 
			FROM Products 
			WHERE company_id = '{self.company_id_Flag}' AND product_name = '{self.productInput.lineEdit().text()}'
			""")

		while query.next():
			counter = 0
			for itm in itemsDict:
				itemsDict[itm] = str(query.value(counter))
				counter+=1
		"""
		for x in itemsDict:
			print(x, " ", itemsDict[x])"""

		row = self.invoiceItemModel.rowCount()
		self.invoiceItemModel.insertRows(self.invoiceItemModel.rowCount(), 1)

		self.invoiceItemModel.setData(self.invoiceItemModel.index(row, 1), self.InvoiceNumber.text())

		itmsCounter = 2
		for itms in itemsDict:
			self.invoiceItemModel.setData(self.invoiceItemModel.index(row, itmsCounter), itemsDict[itms])
			itmsCounter+=1

		self.invoiceItemModel.submitAll()

		self.calculate()

	def delItem(self):
		self.invoiceItemModel.removeRow(self.InvoiceItemTable.currentIndex().row())
		self.invoiceItemModel.submitAll()
		self.calculate()

	def addInvDetails(self):
		if self.update_invoice_Flag:
			query = QSqlQuery(db=db)
			query.exec_(f"""UPDATE Invoices SET 
				company_id=?,
				invoice_date=?,
				invoice_no=?,
				sgst=?,
				cgst=?,
				gross=?,
				discount=?,
				total_amount=?,
				notes=?
				WHERE invoice_no = {self.InvoiceNumber.text()}
				""")
			query.bindValue(0, str(self.company_id_Flag));
			query.bindValue(1, str(self.InvoiceDate.text()));
			query.bindValue(2, str(self.InvoiceNumber.text()));
			query.bindValue(3, str(self.sgstV.text()));
			query.bindValue(4, str(self.cgstV.text()));
			query.bindValue(5, str(self.grossV.text()));
			query.bindValue(6, str(self.discountV.text()));
			query.bindValue(7, str(self.grandtotalV.text()));
			query.bindValue(8, str(self.noteE.text()));

			query.exec_();
			db.commit()
			self.update_invoice_Flag = False
		else:
			query = QSqlQuery(db=db)
			query.exec_("""INSERT INTO Invoices (
				company_id,
				invoice_date,
				invoice_no,
				sgst,
				cgst,
				gross,
				discount,
				total_amount,
				notes
				) 
				VALUES (?,?,?,?,?,?,?,?,?)
				""")
			query.bindValue(0, str(self.company_id_Flag));
			query.bindValue(1, str(self.InvoiceDate.text()));
			query.bindValue(2, str(self.InvoiceNumber.text()));
			query.bindValue(3, str(self.sgstV.text()));
			query.bindValue(4, str(self.cgstV.text()));
			query.bindValue(5, str(self.grossV.text()));
			query.bindValue(6, str(self.discountV.text()));
			query.bindValue(7, str(self.grandtotalV.text()));
			query.bindValue(8, str(self.noteE.text()));

			query.exec_();
			db.commit()

	def cance_invoice(self):
		if (self.update_invoice_Flag == False):
			for i in range(self.invoiceItemModel.rowCount()):
				self.invoiceItemModel.removeRow(self.invoiceItemModel.rowCount()-1)
				self.invoiceItemModel.submitAll()

			self.update_invoice_Flag = False
		self.invoiceEntries()
		self.invNo()	
		self.calculate()


	def save_invoice(self):
		self.addInvDetails()
		self.invoiceItemModel.submitAll()
		self.invNo()
		self.InvoiceDate.setDate(QDate.currentDate())
		self.invoiceEntries()
		self.discountV.setText("0.00")
		self.schmD.setText("0.00")
		self.calculate()
	
	def update_invoice(self):
		try:
			self.update_invoice_Flag = True
			conn = sqlite3.connect("pharmacy.sqlite")
			cursor = conn.cursor()
			query = f"SELECT invoice_date, discount FROM Invoices WHERE invoice_no = {self.InvoiceNumber.text()}"
			cursor.execute(query)
			res = cursor.fetchone()
			conn.close()

			#print(res[0])

			self.InvoiceDate.setDate(QDate.fromString(res[0],"dd/M/yyyy"))
			self.discountV.setText(str(res[1]))

			self.invoiceEntries()
			self.calculate()

		except Exception as e:
			print(e)
			print("Database Error")
	

	def invNo(self):
		try:
			conn = sqlite3.connect("pharmacy.sqlite")
			cursor = conn.cursor()
			query = f"SELECT invoice_no FROM Invoices ORDER BY invoice_no DESC LIMIT 1"
			cursor.execute(query)
			invoiceNo = cursor.fetchone()[0]
			conn.close()

			self.InvoiceNumber.setText(str(invoiceNo+1))
			self.invoiceEntries()
		
		except:
			self.InvoiceNumber.setText(str("25001"))
			self.invoiceEntries()
		
	def gst_amt(self):
		amt = 0
		for i in range(self.invoiceItemModel.rowCount()):
			try:
				amt+=(float(self.invoiceItemModel.record(i).value(14))/100)*float(self.invoiceItemModel.record(i).value(12))*float(self.invoiceItemModel.record(i).value(5))
			except:
				pass
				#amt+=(self.invoiceItemModel.record(i).value(14))/100*self.invoiceItemModel.record(i).value(12)*self.invoiceItemModel.record(i).value(5)		

		self.sgstV.setText(str(round(amt,2)/2))
		self.cgstV.setText(str(round(amt,2)/2))

	def gross_amt(self):
		amt = 0
		for i in range(self.invoiceItemModel.rowCount()):
			try:
				amt+=((float(self.invoiceItemModel.record(i).value(14)/100))*float(self.invoiceItemModel.record(i).value(12))*float(self.invoiceItemModel.record(i).value(5)))+float(self.invoiceItemModel.record(i).value(12))*float(self.invoiceItemModel.record(i).value(5))
			except:
				pass
				#amt+=((self.invoiceItemModel.record(i).value(14)/100)*self.invoiceItemModel.record(i).value(12)*self.invoiceItemModel.record(i).value(5))+self.invoiceItemModel.record(i).value(12)*self.invoiceItemModel.record(i).value(5)
			
		self.grossV.setText(str(round(amt,2)))	

	def schm_discount(self):
		scamt = 0
		for i in range(self.invoiceItemModel.rowCount()):
			try:
				scamt+=float(self.invoiceItemModel.record(i).value(13))
			except:
				pass
				#amt+=((self.invoiceItemModel.record(i).value(14)/100)*self.invoiceItemModel.record(i).value(12)*self.invoiceItemModel.record(i).value(5))+self.invoiceItemModel.record(i).value(12)*self.invoiceItemModel.record(i).value(5)
			
		self.schmD.setText(str(round(scamt,2)))

	def discounted(self):
		self.total_discount = float(self.discountV.text())+float(self.schmD.text())
		#print(self.total_discount)
		self.grandtotalV.setText(str(float(self.grossV.text())-self.total_discount))

	def calculate(self):
		self.gst_amt()
		self.schm_discount()
		self.gross_amt()
		self.discounted()

	def top_prod(self):
		self.topProdModel = QSqlQueryModel()
		self.topProdModel.setQuery(f"SELECT product_name || ' - ' || expiry || ' - INR ' || mrp as lst FROM Products", db)
		self.topProd.setModel(self.topProdModel)	
		self.topProd.setModelColumn(0)

	def expiring_prod(self):
		self.expProdModel = QSqlQueryModel()
		self.expProdModel.setQuery(f"SELECT product_name || ' - ' || expiry as exp FROM Products ORDER BY expiry DESC", db)
		self.expiringLst.setModel(self.expProdModel)	
		self.expiringLst.setModelColumn(0)

	def recent_invoices(self):
		self.recent_inv_Model = QSqlTableModel(db=db)
		self.recent_inv_Model.setTable("Invoices")
		self.recentInv.setModel(self.recent_inv_Model)	
		self.recent_inv_Model.setFilter(f"company_id = {self.company_id_Flag} ORDER BY invoice_id DESC")
		self.recent_inv_Model.setHeaderData(2,Qt.Horizontal, "Date")
		self.recent_inv_Model.setHeaderData(3,Qt.Horizontal, "Invoice Number")
		self.recent_inv_Model.setHeaderData(4,Qt.Horizontal, "CGST")
		self.recent_inv_Model.setHeaderData(5,Qt.Horizontal, "SGST")
		self.recent_inv_Model.setHeaderData(6,Qt.Horizontal, "Gross Amount")
		self.recent_inv_Model.setHeaderData(7,Qt.Horizontal, "Discount")
		self.recent_inv_Model.setHeaderData(8,Qt.Horizontal, "Total")
		self.recent_inv_Model.setHeaderData(10,Qt.Horizontal, "Notes")
		self.recentInv.hideColumn(0)
		self.recentInv.hideColumn(1)
		self.recentInv.hideColumn(9)
		#self.recentInv.hideColumn(10)

		self.recentInv.horizontalHeader().setStretchLastSection(True)
		#self.recentInv.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		#self.recentInv.resizeColumnsToContents()

		self.recent_inv_Model.select()

		self.recentInv.setEditTriggers(self.recentInv.NoEditTriggers)	

	def is_prod_exists(self):
		conn = sqlite3.connect("pharmacy.sqlite")
		cursor = conn.cursor()
		query = f"SELECT product_name FROM Products WHERE product_name = '{self.nameE.text()}' COLLATE NOCASE"
		cursor.execute(query)
		prod_in = cursor.fetchall()
		conn.close()

		if(len(prod_in)>0):
			alert = QMessageBox()
			alert.setIcon(QMessageBox.Warning)
			alert.setText(f"Product Already Exists. \nPlease Update Inventory Details🙏.")
			alert.setWindowTitle("Alert")
			alert.exec_()

			self.searchE.setText(self.nameE.text())

			self.searchProduct()

	def inventory_summary(self):
		conn = sqlite3.connect("pharmacy.sqlite")
		cursor = conn.cursor()
		query = f"SELECT COUNT(product_name), SUM(quantity), SUM(mrp) FROM Products WHERE company_id = {self.company_id_Flag}"
		cursor.execute(query)
		res = cursor.fetchone()
		conn.close()

		self.totalData.setText(str(res[0]))
		self.totalProdD.setText(str(res[0]))
		self.totalQtyInv.setText(str(res[1]))
		self.totalQtyD.setText(str(res[1]))
		self.totalValueInv.setText(str(res[2]))

		conn = sqlite3.connect("pharmacy.sqlite")
		cursor = conn.cursor()
		query = f"SELECT COUNT(product_name) FROM Products WHERE quantity <= 0 AND company_id = {self.company_id_Flag}"
		cursor.execute(query)
		res = cursor.fetchone()
		conn.close()

		self.totalOutInv.setText(str(res[0]))
		self.outD.setText(str(res[0]))

	def plot_Sale(self):
		
		conn = sqlite3.connect("pharmacy.sqlite")
		cursor = conn.cursor()
		query = f"SELECT invoice_date, SUM(total_amount) FROM Invoices WHERE company_id = {self.company_id_Flag} GROUP BY invoice_date LIMIT 7"
		cursor.execute(query)
		res = cursor.fetchall()
		conn.close()
	
		self.canvas.axes.cla()
		self.canvas.axes.bar(list(map(lambda x : x[0],res)), list(map(lambda x : x[1],res)), color = '#5a5d8a')
		self.canvas.axes.spines['top'].set_color('white')
		self.canvas.axes.spines['right'].set_color('white')
		self.canvas.draw()

	
#Event Loop
app = QtWidgets.QApplication([])
window = MainWindow()
app.setFont(QFont("Calibri", 10))

window.show()
app.exec_()
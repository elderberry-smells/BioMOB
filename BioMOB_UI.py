# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 12:06:13 2018

@author: jamesbc
"""

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QLineEdit, QMessageBox
from PyQt5.QtCore import pyqtSlot
import PySimpleGUI as sg 
import box_details
import metrics
import pandas as pd
from PandasModel import PandasModel
import datetime
import sqlite3
import quant_program
import os
import glob
import pgrc_shipment
import gh_sampling
import quant_upload
import samplesheet


class PopupQuit(QWidget):
    
    def __init__(self, parent=None):
        super(PopupQuit, self).__init__()
        self.setGeometry(200, 200, 384, 100)
        self.setWindowTitle("Are you sure?")
        self.popup_ui()
        
    def popup_ui(self):
        '''make a popup question, yes, no, cancel type thing'''
        self.areyousureLabel = QtWidgets.QLabel("Are you sure you want to quit??", self)
        self.areyousureLabel.setGeometry(QtCore.QRect(100, 10, 360, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.areyousureLabel.setFont(font)
        self.areyousureLabel.setObjectName("areyousureLabel")
                
        self.okButton = QtWidgets.QPushButton("OK", self)
        self.okButton.setGeometry(QtCore.QRect(100, 50, 131, 31))
        self.okButton.setObjectName("okButton")
        self.okButton.clicked.connect(self.buttonChoice)
        
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.cancelButton.setGeometry(QtCore.QRect(240, 50, 131, 31))
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.clicked.connect(self.closedialog)
        
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 81))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/code/BioMOB/images/questionmark.PNG"))
        self.label.setObjectName("questionimg")
        
    def buttonChoice(self):
        '''close the whole app'''
        app.deleteLater()
        app.quit()
    
    def closedialog(self):
        '''just close the option dialog'''
        self.close()

        
class Metrics(QWidget):
    
    def __init__(self, parent=None):
        super(Metrics, self).__init__()
        self.setGeometry(200, 50, 1320, 950)
        self.setWindowTitle('BioMOB DB Viewer')
        self.metrics_ui()
    
    def metrics_ui(self):
        
        # adda  title to the metrics widget
        self.labelTitle = QtWidgets.QLabel("BioMOB Database Viewer and Metrics", self)
        self.labelTitle.setGeometry(QtCore.QRect(170, 0, 849, 40))
        font = QtGui.QFont()
        font.setPointSize(25)
        self.labelTitle.setFont(font)
        self.labelTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.labelTitle.setObjectName("labelTitle")
        
        # add a table view area to the widget, this is where tables will generate to
        self.dbTableView = QtWidgets.QTableView(self)
        self.dbTableView.setGeometry(QtCore.QRect(10, 40, 1181, 861))
        self.dbTableView.setObjectName("dbTableView")
        
        # add a combobox to the widget, the drop down in this will determine what to show in tableview area
        self.dbTableSelector = QtWidgets.QComboBox(self)
        self.dbTableSelector.setEnabled(True)
        self.dbTableSelector.setGeometry(QtCore.QRect(10, 910, 211, 20))
        self.dbTableSelector.setCurrentText("")
        self.dbTableSelector.setObjectName("dbTableSelector")
        self.dbTableSelector.addItems(['', 'shipment_details', 'box_details', 'sample_information', 'adapter_sets',
                                'no_tissue_sampling', 'failed_extraction', 'DNA_storage_details', 'metrics_table'])

        
        # adda a button that when clicked will generate the current table selected in combobox 
        self.generateButton = QtWidgets.QPushButton("Generate Table", self)
        self.generateButton.setGeometry(QtCore.QRect(230, 910, 211, 23))
        self.generateButton.setObjectName("generateButton")
        self.generateButton.clicked.connect(self.generate_table)
        
        # button that saves the current table selected in the combobox
        self.saveButton = QtWidgets.QPushButton("Save Current Table", self)
        self.saveButton.setGeometry(QtCore.QRect(450, 910, 211, 23))
        self.saveButton.setObjectName("saveButton")
        self.saveButton.clicked.connect(self.saveTable)
        
        # button to close down the metric and DB viewer widget and return to main app
        self.quitButton = QtWidgets.QPushButton("Close DB Viewer", self)
        self.quitButton.setGeometry(QtCore.QRect(990, 910, 201, 23))
        self.quitButton.setObjectName("quitButton")
        self.quitButton.clicked.connect(self.exitMetrics)
        
        # add a "sort by plant" label and combobox to the side of the tableview
        self.sortplantLabel = QtWidgets.QLabel("Sort by plant type", self)
        self.sortplantLabel.setGeometry(QtCore.QRect(1200, 70, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.sortplantLabel.setFont(font)
        self.sortplantLabel.setObjectName("sortplantLabel")
        
        self.plantCombo = QtWidgets.QComboBox(self)
        self.plantCombo.setGeometry(QtCore.QRect(1200, 90, 111, 22))
        self.plantCombo.setObjectName("plantCombo")
        plants = self.generatePlants()
        plants = sorted(plants)
        self.plantCombo.addItems(plants)
        
        # add a field to generate a "Box View" that pulls box, well, and plant type into a table
        self.sortBoxLabel = QtWidgets.QLabel("View Box Number", self)
        self.sortBoxLabel.setGeometry(QtCore.QRect(1200, 480, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.sortBoxLabel.setFont(font)
        self.sortBoxLabel.setObjectName("sortBoxLabel")
        
        # add a fillable box field and a generate button
        self.boxValue = QLineEdit(self)
        self.boxValue.setGeometry(QtCore.QRect(1200, 500, 111, 22))
        self.boxValue.setObjectName("boxValue")
        
        # add a button to generate the table
        self.boxButton = QtWidgets.QPushButton("Generate Box view", self)
        self.boxButton.setGeometry(QtCore.QRect(1200, 530, 111, 22))
        self.boxButton.clicked.connect(self.generateBoxView)
        
        # add a total count label and box to the side of the label view
        self.countLabel = QtWidgets.QLabel("Total Plant Count", self)
        self.countLabel.setGeometry(QtCore.QRect(1200, 140, 111, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.countLabel.setFont(font)
        self.countLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.countLabel.setObjectName("countLabel")
        self.totalCount = QtWidgets.QLabel(self)
        self.totalCount.setGeometry(QtCore.QRect(1200, 160, 111, 22))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.totalCount.setFont(font)
        self.totalCount.setFrameShape(QtWidgets.QFrame.Box)
        self.totalCount.setText("")
        self.totalCount.setAlignment(QtCore.Qt.AlignCenter)
        self.totalCount.setObjectName("totalCount")
        
    
    @pyqtSlot()
    def generateBoxView(self):
        '''Connect to the database, and depending on the selection currently shown in boxValue field, query the DB 
        for that data.  Generate a pandas dataframe out of that query, and add the table to the tableview using 
        PandasModel library'''

        
        conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
        conn.text_factory = str 
        cur = conn.cursor() 
        box_text = str(self.boxValue.text())
        
        # test to make sure that it an integer, and if not, popup that states only whole numbers can be put in field
        try:
            # make sure the field filled in is an integer, if not make a popup in exception
            int(box_text)
                        
        except ValueError:
            # popup stating that number is not an integer and to re-fill the field properly
            QMessageBox.about(self, 'Value Error', 'Field must be an integer/whole number\nPut in new number to try again')


        query = '''SELECT box_number from sample_information where box_number={}'''.format(box_text)
        box_query = cur.execute(query).fetchall()
        if len(box_query) > 0:
            pass
        else:
            QMessageBox.about(self, 'Value error', 'That box number is not in the database')

         
        cols = ['box_number', 'well', 'accession', 'plant', ] # get the column headers for the output
        query = '''SELECT
                sample_information.box_number,
                sample_information.well,
                sample_information.accession,
                shipment_details.plant
                FROM sample_information
                INNER JOIN shipment_details
                ON shipment_details.accession = sample_information.accession
                WHERE box_number={boxnum}'''.format(boxnum=box_text)
        
        tabledata = cur.execute(query).fetchall()
        df = pd.DataFrame(tabledata, columns=cols)    
        model = PandasModel(df)
    
        conn.close()
        self.dbTableView.setModel(model)
        self.totalCount.setText(str(len(df)))

    
    @pyqtSlot()
    def generatePlants(self):
        conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
        conn.text_factory = str 
        cur = conn.cursor() 
        
        plants = list(set(cur.execute("SELECT plant FROM shipment_details").fetchall()))
        conn.close() # close the connection
        unique_list = [' '.join(item) for item in plants]
        string_list = ['']
        for i in unique_list:
            string_list.append(i.lower())
        return set(string_list)
           
    
    @pyqtSlot()    
    def generate_table(self):
        '''Connect to the database, and depending on the selection currently shown in combobox, query the DB 
        for that data.  Generate a pandas dataframe out of that query, and add the table to the tableview using 
        PandasModel library'''

        
        conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
        conn.text_factory = str 
        cur = conn.cursor() 
        text = str(self.dbTableSelector.currentText())
        sort_plant = str(self.plantCombo.currentText())  # based on what is currently selected in combo box, grab that text
        
        box_details.updateBoxDetails()  #update the box_details before making the tables
        
        # if it is the metrics table, run the metrics function which will query whats needed from db
        if text == 'metrics_table':
            metrics_df = metrics.generateMetrics()
            model = PandasModel(metrics_df)
        
        else:  # set up columns for the database headers for shipment_details
            if text == 'shipment_details':
                cols = ['shipment_id', 'accession', 'taxon', 'plant', 'name',
                        'habit', 'country', 'donor type', 'barcode', 'alt',
                        'donor institute', 'donor country', 'origin', 'received']
            
            elif text == 'box_details':
                cols = ['box_number', 'plant_type', 'sampled', 'submitted', 'extracted',
                        'quantified', 'adapter_set', 'sequenced', 'library_id', 'sequence_path', 'avg_fragment', 'lib_conc']
                            
            elif text == 'sample_information':
                cols = ['sample_id', 'seq_id', 'accession', 'box_number', 'well',
                        'box_id', 'number_plants', 'quant', 'adapter_set', 'index_name']           
                
            elif text == 'adapter_sets':
                cols = ['adapter_id', 'adapter_set', 'plate', 'well', 'index_name', 'barcode', 'date']
                           
            elif text == 'no_tissue_sampling':
                cols = ['tissue_id', 'accession', 'taxon', 'plant', 'name', 'comments']
    
            elif text == 'failed_extraction':
                cols = ['accession', 'box_number', 'well']
    
            elif text == 'DNA_storage_details':
                cols = ['box_number', 'room_number', 'storage_unit', 'compartment', 'shelf_number']
            
            elif text == '':
                cols = None
        
        # -----------------------------------  Sorting queries -----------------------------------------------------
        
            if sort_plant == "":  # there is no sort being requested in the app, so just grab the table like normal
                query = '''SELECT * FROM {table}'''.format(table=text)
                tabledata = cur.execute(query).fetchall()
                df = pd.DataFrame(tabledata, columns=cols)
                model = PandasModel(df)
    
            
            else: # there is a sort being requested, so query based on the sort selected (sort_plant)
                  
                                    
                if text in ['adapter_sets', 'DNA_storage_details']:  # sorting has no bearing on these table
                    query = '''SELECT * FROM {table}'''.format(table=text)
                    tabledata = cur.execute(query).fetchall()
                    df = pd.DataFrame(tabledata, columns=cols)
                    
                    
                elif text == 'shipment_details':  # shipment details has plant column, so just sort tables by plant(psort)
                    query = '''SELECT * FROM {table} WHERE plant LIKE "%{psort}%"'''.format(table=text, psort=sort_plant)
                    tabledata = cur.execute(query).fetchall()
                    df = pd.DataFrame(tabledata, columns=cols)
                    
                elif text == 'no_tissue_sampling':  # not tissue sampling has plant column, so just sort by plant(psort)
                    query = """SELECT * FROM {table} WHERE plant LIKE '%{psort}%'""".format(table=text, psort=sort_plant)
                    tabledata = cur.execute(query).fetchall()
                    df = pd.DataFrame(tabledata, columns=cols)
            
                elif text == 'sample_information':  # need to grab plant type from shipment details and join with this table
                    query = '''SELECT
                            sample_information.sample_id,
                            sample_information.seq_id,
                            sample_information.accession,
                            sample_information.box_number,
                            sample_information.well,
                            sample_information.box_id,
                            sample_information.number_plants,
                            sample_information.quant,
                            sample_information.adapter_set,
                            sample_information.index_name,
                            shipment_details.plant
                            FROM sample_information
                            INNER JOIN shipment_details
                            ON shipment_details.accession = sample_information.accession
                            WHERE plant LIKE "%{psort}%"'''.format(psort=sort_plant)
                    
                    tabledata = cur.execute(query).fetchall()
                    sort_cols = cols
                    sort_cols.append('plant')
                    df = pd.DataFrame(tabledata, columns=sort_cols)
                    df.drop('plant', axis=1, inplace=True)

              
                elif text == 'failed_extraction':  # need to grab plant type from shipment details and join with this table
                    query = '''SELECT
                            failed_extraction.accession,
                            failed_extraction.box_number,
                            failed_extraction.well,
                            shipment_details.plant
                            FROM failed_extraction
                            INNER JOIN shipment_details
                            ON shipment_details.accession = failed_extraction.accession
                            WHERE plant LIKE "%{psort}%"'''.format(psort=sort_plant)

                    tabledata = cur.execute(query).fetchall()
                    sort_cols = cols
                    sort_cols.append('plant')
                    df = pd.DataFrame(tabledata, columns=sort_cols)    
                    df.drop('plant', axis=1, inplace=True)


                elif text == 'box_details':
                   query = '''SELECT * FROM {table}'''.format(table=text)
                   tabledata = cur.execute(query).fetchall()
                   df = pd.DataFrame(tabledata, columns=cols)
                   
                
                model = PandasModel(df)
            
        conn.close()
        self.dbTableView.setModel(model)
        self.totalCount.setText(str(len(df)))
        
    @pyqtSlot() 
    def saveTable(self):
        '''function to save the current table that is selected in combobox.  This will query the database
        to generate the table, and use pandas to save the table as an XLSX file'''
        
        reply = sg.PopupOKCancel('Are you sure you want to save the file?') # popup to save file
        text = str(self.dbTableSelector.currentText())
        sort_plant = str(self.plantCombo.currentText())     # based on what is currently selected in combo box, grab that text
                
        if reply == 'OK':
            # connect to the database 
            conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
            conn.text_factory = str 
            cur = conn.cursor()

            
            # if it is the metrics table, generate a table and a graph, save those together in one xlsx file            
            if text == 'metrics_table':
                metrics_df = metrics.generateMetrics()
                metrics.graph_metrics(metrics_df)
            
            else:
                # get the correct column headers for the specific table selected
                if text == 'shipment_details':
                    cols = ['shipment_id', 'accession', 'taxon', 'plant', 'name',
                            'habit', 'country', 'donor type', 'barcode', 'alt',
                            'donor institute', 'donor country', 'origin', 'received']
                
                elif text == 'box_details':
                    cols = ['box_number', 'plant_type', 'sampled', 'submitted', 'extracted',
                            'quantified', 'adapter_set', 'sequenced', 'library_id', 'sequence_path', 'avg_fragment', 'lib_conc']
                                
                elif text == 'sample_information':
                    cols = ['sample_id', 'seq_id', 'accession', 'box_number', 'well',
                            'box_id', 'number_plants', 'quant', 'adapter_set', 'index_name']           
                    
                elif text == 'adapter_sets':
                    cols = ['adapter_id', 'adapter_set', 'plate', 'well', 'index_name', 'barcode', 'date']
                               
                elif text == 'no_tissue_sampling':
                    cols = ['tissue_id', 'accession', 'taxon', 'plant', 'name', 'comments']
        
                elif text == 'failed_extraction':
                    cols = ['accession', 'box_number', 'well']
        
                elif text == 'DNA_storage_details':
                    cols = ['box_number', 'room_number', 'storage_unit', 'compartment', 'shelf_number']
                
                # -----------------------------------  Sorting queries -----------------------------------------------------
                
                if sort_plant == "":  # there is no sort being requested in the app, so just grab the table like normal
                    query = '''SELECT * FROM {table}'''.format(table=text)
                    tabledata = cur.execute(query).fetchall()
                    df = pd.DataFrame(tabledata, columns=cols)
                
                else: # there is a sort being requested, so query based on the sort selected (sort_plant)
                    
                                    
                    if text in ['adapter_sets', 'DNA_storage_details']:  # sorting has no bearing on these table
                        query = '''SELECT * FROM {table}'''.format(table=text)
                        tabledata = cur.execute(query).fetchall()
                        df = pd.DataFrame(tabledata, columns=cols)
                        
                        
                    elif text == 'shipment_details':  # shipment details has plant column, so just sort tables by plant(psort)
                        query = '''SELECT * FROM {table} WHERE plant LIKE "%{psort}%"'''.format(table=text, psort=sort_plant)
                        tabledata = cur.execute(query).fetchall()
                        df = pd.DataFrame(tabledata, columns=cols)
                        
                    elif text == 'no_tissue_sampling':  # not tissue sampling has plant column, so just sort by plant(psort)
                        query = '''SELECT * FROM {table} WHERE plant LIKE "%{psort}%"'''.format(table=text, psort=sort_plant)
                        tabledata = cur.execute(query).fetchall()
                        df = pd.DataFrame(tabledata, columns=cols)
                
                    elif text == 'sample_information':  # need to grab plant type from shipment details and join with this table
                        query = '''SELECT
                                sample_information.sample_id,
                                sample_information.seq_id,
                                sample_information.accession,
                                sample_information.box_number,
                                sample_information.well,
                                sample_information.box_id,
                                sample_information.number_plants,
                                sample_information.quant,
                                sample_information.adapter_set,
                                sample_information.index_name,
                                shipment_details.plant
                                FROM sample_information
                                INNER JOIN shipment_details
                                ON shipment_details.accession = sample_information.accession
                                WHERE plant LIKE "%{psort}%"'''.format(psort=sort_plant)
                        
                        tabledata = cur.execute(query).fetchall()
                        sort_cols = cols
                        sort_cols.append('plant')
                        df = pd.DataFrame(tabledata, columns=sort_cols)
                        df.drop('plant', axis=1, inplace=True)
    
                  
                    elif text == 'failed_extraction':  # need to grab plant type from shipment details and join with this table
                        query = '''SELECT
                                failed_extraction.accession,
                                failed_extraction.box_number,
                                failed_extraction.well,
                                shipment_details.plant
                                FROM failed_extraction
                                INNER JOIN shipment_details
                                ON shipment_details.accession = failed_extraction.accession
                                WHERE plant LIKE "%{psort}%"'''.format(psort=sort_plant)
    
                        tabledata = cur.execute(query).fetchall()
                        sort_cols = cols
                        sort_cols.append('plant')
                        df = pd.DataFrame(tabledata, columns=sort_cols)    
                        df.drop('plant', axis=1, inplace=True)
    
    
                    elif text == 'box_details':
                       query = '''SELECT * FROM {table}'''.format(table=text)
                       tabledata = cur.execute(query).fetchall()
                       df = pd.DataFrame(tabledata, columns=cols)
                        
                    
                # get formatting for save name(including pathway) and save the xlsx file using xlsxwriter
                if sort_plant == '':
                    fhand = '{0}_{1}'.format(str(self.dbTableSelector.currentText()), datetime.datetime.today().strftime("%m-%d-%Y"))
                else:
                    fhand = '(sorted){0}_{1}'.format(str(self.dbTableSelector.currentText()), datetime.datetime.today().strftime("%m-%d-%Y"))
                path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/7.  Lab Book and miscellaneous/metrics/{0}{1}'.format(fhand, '.xlsx')
                writer = pd.ExcelWriter(path, engine='xlsxwriter')
                df.to_excel(writer, index=False)
                writer.close()
                       
            conn.close()  # close the connection to the database
            
    @pyqtSlot()    
    def exitMetrics(self):
        """exit the application gently so Spyder IDE will not hang"""     
        self.close()


class Window(QDialog):
    
    def __init__(self):
        super(Window, self).__init__()
        self.setGeometry(50, 50, 690, 651)
        self.setWindowTitle('BioMOB')
        self.home()
    
    
    def home(self):
        
        # title font
        title_font = QtGui.QFont()
        title_font.setFamily("Calibri")
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_font.setWeight(75)
        
        # button font (except sequence button)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        
        # sequence sheet button font
        font2 = QtGui.QFont()
        font2.setPointSize(7)
        font2.setBold(True)
        font2.setWeight(75)  
        
        # label font - desciptions of buttons
        label_font = QtGui.QFont()
        label_font.setPointSize(10)
        
        # font for the log sheet
        logsheet_font = QtGui.QFont()
        logsheet_font.setFamily("Calibri")
        logsheet_font.setPointSize(12)
        
        
        # write title on top of app
        titleLabel = QtWidgets.QLabel("BIOMOB USER INTERFACE -- DATABASE CONNECTION AND TOOLS", self)
        titleLabel.setFont(title_font)
        titleLabel.setGeometry(QtCore.QRect(10, 10, 671, 51))
        titleLabel.setFrameShape(QtWidgets.QFrame.Box)
        titleLabel.setFrameShadow(QtWidgets.QFrame.Raised)
        titleLabel.setLineWidth(2)
        
        # add logo image label to the bottom of the app
        logoLabel = QtWidgets.QLabel(self)
        logoLabel.setGeometry(QtCore.QRect(10, 600, 151, 51))
        logoLabel.setText("")
        logoLabel.setPixmap(QtGui.QPixmap("images/aafc_logo.png"))
        logoLabel.setObjectName("logoLabel")
        
        # add a line.  It doesn't do anything, but I think it looks pretty sharp.
        line = QtWidgets.QFrame(self)
        line.setGeometry(QtCore.QRect(10, 70, 671, 16))
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setObjectName("line")
        
        
        # ---------------------------------- BUTTONS -------------------------------------------
        
        # shipment button that loads PGRC shipments info into database
        shipmentButton = QtWidgets.QPushButton('Load Shipment Details', self)
        shipmentButton.setGeometry(QtCore.QRect(10, 90, 181, 41))
        shipmentButton.setFont(font)
        shipmentButton.setObjectName("shipmentButton")
        shipmentButton.clicked.connect(self.update_shipmentDetails)
        
        # GH Sampling button that loads GH sampling sheet into database
        ghButton = QtWidgets.QPushButton("Load GH Samples", self)
        ghButton.setGeometry(QtCore.QRect(10, 150, 181, 41))
        ghButton.setFont(font)
        ghButton.setObjectName("ghButton")
        ghButton.clicked.connect(self.greenhouse_samplesheet)

        # Quantification button that loads quants into database
        quantButton = QtWidgets.QPushButton("Load Quantification Data", self)
        quantButton.setGeometry(QtCore.QRect(10, 210, 181, 41))
        quantButton.setFont(font)
        quantButton.setObjectName("quantButton")
        quantButton.clicked.connect(self.uploadQuant)
        
        # sampling button to update sampling sheet in database
        samplingButton = QtWidgets.QPushButton("Update Sampling Sheet", self)
        samplingButton.setGeometry(QtCore.QRect(10, 270, 181, 41))
        samplingButton.setFont(font)
        samplingButton.setObjectName("samplingButton")
        samplingButton.clicked.connect(self.update_boxdetails)
        
        # sequence button that generates sequencing sampling sheets for GBS pipeline
        sequenceButton = QtWidgets.QPushButton("Create Sequencing Samplesheet", self)
        sequenceButton.setGeometry(QtCore.QRect(10, 330, 181, 41))
        sequenceButton.setFont(font2)
        sequenceButton.setObjectName("sequenceButton")
        sequenceButton.clicked.connect(self.samplesheetGenerator)

        # metrics button to generate the metrics app and database viewer
        metricsButton = QtWidgets.QPushButton("Table View", self)
        metricsButton.setGeometry(QtCore.QRect(10, 390, 181, 41))
        metricsButton.setFont(font)
        metricsButton.setObjectName("metricsButton")
        metricsButton.clicked.connect(self.viewDB)
        
        # flourimetrics button to analyze quantification data 
        flourButton = QtWidgets.QPushButton("Analyze Flourimeter Data", self)
        flourButton.setGeometry(QtCore.QRect(10, 450, 181, 41))
        flourButton.setFont(font)
        flourButton.setObjectName("flourButton")
        flourButton.clicked.connect(self.quant_plates)

        # exit button to close down the application
        quitButton = QtWidgets.QPushButton("Quit Application", self)
        quitButton.setGeometry(QtCore.QRect(530, 610, 151, 31))
        quitButton.setFont(font)
        quitButton.setObjectName("quitButton")
        quitButton.clicked.connect(self.safeExit)
        
        
        # ---------------------------------- Labels -------------------------------------------        
        
        # add a label to describe shipment button use
        shipmentLabel = QtWidgets.QLabel("Take shipment information from PGRC and load it into database.\n"
                                         "This creates a sampling sheet for the greenhouse as well\n""", self)
        shipmentLabel.setGeometry(QtCore.QRect(210, 90, 471, 41))
        shipmentLabel.setFont(label_font)
        shipmentLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        shipmentLabel.setIndent(-1)
        shipmentLabel.setObjectName("shipmentLabel")
        
        # add a label to describe GH sampling sheet button use
        ghLabel = QtWidgets.QLabel("Upload GH sampling sheet into the database.  Move any plants\n"
                                   "Not sampled into the no_tissue_sampling table  \n""", self)
        ghLabel.setGeometry(QtCore.QRect(210, 150, 471, 41))
        ghLabel.setFont(label_font)
        ghLabel.setObjectName("ghLabel")
        
        # add a label to describe "load quantification" button use
        quantLabel = QtWidgets.QLabel("Upload the quantification data from sampled plates into the\n"
                                      "Database, move any failed extractions into failed_extraction table\n""", self)
        quantLabel.setGeometry(QtCore.QRect(210, 210, 471, 41))
        quantLabel.setFont(label_font)
        quantLabel.setObjectName("quantLabel")
        
        # add a label to describe the "update sampling sheet" button
        samplesheetLabel = QtWidgets.QLabel("Update the database information by uploading any updates from \n"
                                            "Sampling sheet, including sample dates, box names, etc.\n""", self)
        samplesheetLabel.setGeometry(QtCore.QRect(210, 270, 471, 41))
        samplesheetLabel.setFont(label_font)
        samplesheetLabel.setObjectName("samplesheetLabel")
        
        # add a label to describe the "generate sequencing sample sheet" button
        sequencingLabel = QtWidgets.QLabel("Query the database to create sample sheets used in the GBS \n"
                                           "Pipeline.  Group samples if there are more than 1 plate combined\n""", self)
        sequencingLabel.setGeometry(QtCore.QRect(210, 330, 471, 41))
        sequencingLabel.setFont(label_font)
        sequencingLabel.setObjectName("sequencingLabel")
        
        # add a label to describe what the "generate metrics" button does 
        metricsLabel = QtWidgets.QLabel("Query the database to create an excel metrics sheet and graphic\n"
                                        "that outlines all sample information done to date.\n""", self)
        metricsLabel.setGeometry(QtCore.QRect(210, 390, 471, 41))
        metricsLabel.setFont(label_font)
        metricsLabel.setObjectName("metricsLabel")
        
        # add a label to describe the "analyze flourimeter" button
        flourLabel = QtWidgets.QLabel("Take raw file from flourimeter and generate the quantification data.", self)
        flourLabel.setGeometry(QtCore.QRect(210, 450, 471, 41))
        flourLabel.setFont(label_font)
        flourLabel.setObjectName("flourLabel")
        
        # add a log label to the app, shows what was run throughout the program being open
        self.logLabel = QtWidgets.QLabel(self)
        self.logLabel.setGeometry(QtCore.QRect(10, 520, 671, 400))
        self.logLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.logLabel.setText("")
        self.logLabel.setWordWrap(True)
        scrollLabel = QtWidgets.QScrollArea(self)  # create a scrollable area
        scrollLabel.setGeometry(QtCore.QRect(10, 520, 671, 81))
        scrollLabel.setObjectName("scrolllabel")
        scrollLabel.setWidget(self.logLabel)  # pack the scrollable area into the log label
        
        # add some formatting to the log label
        self.logLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.logLabel.setObjectName("logLabel")
        self.loglabeltext = ""  # empty text to append log label strings to, then display in logLabel scroll area
        
        # add some detail to the log label, just states what the label is
        logsheetLabel = QtWidgets.QLabel("Tool Logsheet - current session", self)
        logsheetLabel.setGeometry(QtCore.QRect(230, 500, 211, 20))
        logsheetLabel.setFont(logsheet_font)
        logsheetLabel.setAlignment(QtCore.Qt.AlignCenter)
        logsheetLabel.setObjectName("logsheetLabel")
        
        # -------------------------------------  METRICS APP ----------------------------------------------------
        
        self.metrics = Metrics(self)  # init the Metrics/DB viewer widget
        self.popup = PopupQuit(self)
        
        self.show()

        # --------------------------------------  FUNCTIONS -----------------------------------------------------
    
    @pyqtSlot()
    def update_shipmentDetails(self):
        import tkinter as tk
        from tkinter import filedialog
        #  pop up dialog using tkinter - file selector.  Open file dialog prompts from shipment folder
        root = tk.Tk()
        root.withdraw()
        shipment_path = filedialog.askopenfilename(initialdir = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/1.  Sample Shipments')
        shipment_name = shipment_path.rsplit("/", 1)[-1]  # get the file name seperate from the pathway
        
        add_text = pgrc_shipment.update_shipment(shipment_name, shipment_path)
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text


    @pyqtSlot()
    def greenhouse_samplesheet(self):
        '''upload the greenhouse sample sheets to the database'''
        add_text = gh_sampling.gh_samplingsheet()
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text


    @pyqtSlot()
    def uploadQuant(self):
        '''upload the quantifications to the database by passing all xlsx files in quant folder through quant_upload.py'''
        add_text = quant_upload.upload_quantsDB()
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text


    @pyqtSlot()
    def update_boxdetails(self):
        add_text = box_details.updateBoxDetails()
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text
           

    @pyqtSlot()
    def samplesheetGenerator(self):
        '''create the sample sheets for the GBS pipeline'''
        add_text = samplesheet.get_samplesheets("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/5.  Adapter Sets/2.  Pipeline sample sheets/")
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text


    @pyqtSlot()
    def viewDB(self):
        '''show the metrics and DB viewer widget when button clicked'''
        box_details.updateBoxDetails()  # update the details before opening metrics/DB viewer
        self.metrics.show()


    @pyqtSlot()
    def quant_plates(self):
        # look in the quantification folder for any csv files that are to be run
        file_path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/3.  Quantification data/flourimeter data/'
        extension = 'csv'
        os.chdir(file_path)
        csv_results = [c for c in glob.glob('{0}*.{1}'.format(file_path, extension))]
        add_text = quant_program.quantify(csv_results, file_path)  # run file, return what was run
        
        # add the run to the log
        if self.loglabeltext == "":
           self.logLabel.setText(add_text)
           self.loglabeltext = add_text

        else:
           more_text = '{} \n{}'.format(self.loglabeltext, add_text)
           self.logLabel.setText(more_text)
           self.loglabeltext = more_text
   
    
    @pyqtSlot()
    def safeExit(self):
        global quitter
        """exit the application gently so Spyder IDE will not hang"""     
        
        self.popup.show()


if __name__ == '__main__':
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    else:
        print('QApplication instance already exists: {}'.format(str(app)))

    ex = Window()
    app.exec_()

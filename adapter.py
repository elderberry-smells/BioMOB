# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 11:55:18 2018

@author: JamesBC

Move the adapter set information into the database.  This will be called upon for 
identifying barcode sequences (making sample list) for GBS pipeline.  

ONLY NEEDS TO BE RUN IF NEW ADAPTER SETS HAVE BEEN MADE!!
"""

import pandas as pd
import sqlite3
import csv
import os
import datetime


# grab the adapter set file you want to move into the database.  set to one file currently.
fname = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/5.  Adapter Sets/1.  uploaded adapters/Feb2018 adapter set_ID sheet.xlsx'

# open the file as a dataframe, and ensure the columns are correct 
adap_df = pd.read_excel(fname) 
adap_col = ['adapter_set', 'plate', 'well', 'index_name', 'barcode', 'date']
adap_df = adap_df[adap_col]
adap_df['date'] = adap_df['date'].astype('str')
to_db = list(adap_df.itertuples(index=False, name=None))
# write a temporary csv for writing to the database
'''
adap_df.to_csv('temp.csv')


with open('temp.csv', 'rt') as csv_file: 
    dr = csv.DictReader(csv_file) 
    
    # get all the information into memory from the csv file in one list of tuples
    to_db = [(i['adapter_set'], i['plate'], i['well'], i['index_name'],
              i['barcode'], i['date']) for i in dr] 
'''

# connect to the database
conn = sqlite3.connect("C:/Users/JamesBC/Python_Projects/biomobUI/biomob_ui/testDB_gui.db")
conn.text_factory = str 
cur = conn.cursor() 

#  add the information into the database from the to_db tuple, commit the additions, and close the connection
cur.executemany('''INSERT OR IGNORE INTO adapter_sets (
        adapter_set, plate, well,
        index_name, barcode, date) VALUES (?, ?, ?, ?, ?, ?);''', to_db)

#with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
#    log.write('\n{0} -- Inserted February 2018 adapter set'.format(datetime.datetime.now()))

conn.commit()

conn.close()



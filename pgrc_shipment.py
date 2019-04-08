# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 16:21:08 2018

@author: JamesBC

Take a shipment excel sheet and insert the information into the database.  Convert 
the shipment details into a sampling sheet, save it into a different sampling directory
"""

import pandas as pd
import sqlite3
import os
import datetime
import tkinter
from tkinter import messagebox
import sys


def scan_sheet(df):
    '''read through the dataframe and make a scan sheet sampling sheet with the wells pre-populated'''
    
    # make a list of wells for sampling data, column-by-column 
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

    sample_wells = []  # empty list to append to
    for letter in letters:
        # make a row-by-row list of lists for the wells in the box
        row = ['{0}{1}'.format(letter, str(x).zfill(2)) for x in range(1, 12)]
        sample_wells.append(row)

    col_by_col = []  # empty list to append to, final  
    for nth in range(0, 11):
        # convert the row-by-row to column-by-column by grabbing the nth item of each list in order
        for row in sample_wells:
            transposed = row[nth]
            col_by_col.append(transposed)
    
    number = len(df)
    num_list = number//88 # how many times you need to loop the list (in this case 1, if value has remainder, get rid of it)

    num_partial_list = number%88  # get the remainder of the division ie) how many values into a partial list you need to grab

    final_sample_list = col_by_col * num_list
    for i in range(0, num_partial_list):
        final_sample_list.append(col_by_col[i])
    
    df = pd.DataFrame(final_sample_list, columns=['well'])
    df['box_number'] = ''
    df['accession'] = ''
    
    return df


def update_shipment(file_name, file_path):    
    
    # connect to the database
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor() 
    
    
    # read the file using pandas
    df = pd.read_excel(file_path)
    df.columns = [x.lower() for x in df.columns]  # make all lower case if they aren't already
    

    if 'plant' not in df.columns:
        '''put a message to the user that says opne of the critical column names is missing, so stop the program so they can go fix it'''
        cols = df.columns
        error_message = 'Your file is missing the plant column, please go add that to the sheet'
        root = tkinter.Tk()
        root.withdraw()
        
        messagebox.showerror("Error", error_message)
        sys.exit()
        
    
    
    # grab only the columns that exist in the database for shipment details,
    cols = ['accession', 'taxon', 'plant', 'name', 'habit', 'country', 'donor type',
           'barcode', 'alt', 'donor institute', 'donor country', 'origin', 'received']
    
    df = df[[x for x in df.columns if x in cols]]
    
    # if missing columns in file that exist in database, add them as blank cells
    for col in cols:
        if col not in df.columns:
            df[col] = None
        else: 
            pass
    
    to_db = list(df.itertuples(index=False, name=None))  # make a list of tuples of the dataframe, to be inserted into database
    log_number = len(to_db)
      
    #  add the information into the database, commit the changes, then close the connection
    cur.executemany('''INSERT OR REPLACE INTO shipment_details (
            accession, taxon, plant, name, 
            habit, country, 'donor type', barcode, 
            alt, 'donor institute', 'donor country', origin, 
            received) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', to_db) 
    
    # write into the log file what was inserted into database
    with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
            log.write('\n{0} -- Inserted {1} entries into sample_shipment table from sheet : {2}'.format(datetime.datetime.now(), log_number, file_name))
    
    
    conn.commit() 
    
    conn.close()    
    
    # make a tissue sampling sheet for the shipment details from the dataframe with empty box, well, and comments columns
    
    df['box_number'] = ''  
    df['well'] = ''
    df['comments'] = ''  
    
    #change the dataframe to only have the columns necessary for sampling
    sampling_col = ['accession', 'taxon', 'plant', 'name', 'box_number', 'well', 'comments']
    sampling_df = df[sampling_col]
    scan_df = scan_sheet(sampling_df)
    
    # write out the new sampling sheet into the sampling sheet directory
    os.chdir('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/2.  GH Sampling Sheets')
    
    writer = pd.ExcelWriter('(SAMPLING) ' + file_name, engine='xlsxwriter')
    sampling_df.to_excel(writer, 'sampling sheet', index=False)
    scan_df.to_excel(writer, 'scanning_sheet')
    
    writer.close()
    
    #  move the shipment excel sheet into the uploaded shipments folder
    uploaded_path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/1.  Sample Shipments/uploaded shipments/'
    os.rename(file_path, '{}{}'.format(uploaded_path, file_name))

    guilogupdate = '{0} -- Inserted {1} entries into sample_shipment table from sheet : {2}'.format(datetime.datetime.today().strftime("%m/%d/%Y"), log_number, file_name)
    return guilogupdate


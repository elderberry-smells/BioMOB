# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 10:50:34 2018

Add the sampling sheets to the database, this will track which sample went in which well for each box
that is sampled.  This is important to keep track of, as these samples will be pooled and need to have 
box # and well queried easily.  Move any line that did not have any tissue sampled into the 
no_tissue_sampling table so we can keep track of which lines did not move forward from the greenhouse 
for attempting at re-planting later or for PGRC records.

@author: JamesBC
"""

import pandas as pd
import sqlite3
import tkinter as tk
from tkinter import filedialog
import datetime
import os

def gh_samplingsheet():
    
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor() 
    
    
    #  pop up dialog using tkinter - file selector.  Open file dialog prompts from sampling folder
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/2.  GH Sampling Sheets')
    file_name = file_path.rsplit("/", 1)[-1]  # get the file name seperate from the pathway
    
    df = pd.read_excel(file_path)
    if 'barcode' in df.columns:
        df.drop(['barcode'], axis=1, inplace=True, errors='ignore')
    
    
    ##  if the dataframe has any rows where no tissue was sampled, remove them from the df, 
    ## and add them to the no_tissue_sampling table in the database
    
    no_tissue_df = df[df['box_number'].isnull()]  # make a df that has all lines that were not sampled
    
    if len(no_tissue_df.index) > 0:  # there were varities in this shipment that did not get sampled
        no_tissue_df = no_tissue_df[['accession', 'taxon', 'plant', 'name', 'comments']]
        to_nan = list(no_tissue_df.itertuples(index=False, name=None))
    
        cur.executemany('''INSERT OR REPLACE INTO no_tissue_sampling (
                accession, taxon, plant, name, comments) VALUES (?, ?, ?, ?, ?);''', to_nan)
        
        with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
            log.write('\n{0} -- Inserted {1} entries into no_tissue_sampling table from sheet : {2}'.format(datetime.datetime.now(), len(to_nan), file_name))
    
    
    #  determine the next set of seq_id value for the database.  This is a unique value that increments up as you add entries 
    seq = cur.execute('SELECT seq_id FROM sample_information ORDER BY sample_id DESC LIMIT 1;').fetchall()  # the last entry is highest seq_id
    
    if len(seq) == 0:
        starting_num = 0 # if its the first entry into the database, have a value of 0 to start
    else:
        starting_num = int(seq[0][0][7:])  # turn the final 6 characters in the id into an integer
    
    
    # remove the rows missing 'box' and 'well', then get a list of the next succession of unique seq_ids
    
    df = df.dropna(subset=['box_number', 'well'])
    
    new_seq = ['SK-GBD-{}'.format(str(i+starting_num+1).zfill(6)) for i in range(len(df.index))]
    
    
    #  add the seq_id column, then remove any extra columns from the dataframe
    if 'number_plants' in df.columns:
        sampling_col = ['seq_id', 'accession', 'box_number', 'well', 'number_plants']
    else:
        sampling_col = ['seq_id', 'accession', 'box_number', 'well']
    
    df['seq_id'] = new_seq
    
    sampling_col = ['seq_id', 'accession', 'box_number', 'well', 'number_plants']
    
    
    if 'number_plants' in df.columns:
        df = df[sampling_col]
        to_db = list(df.itertuples(index=False, name=None))    
        
    else:
        df['number_plants'] = 1
        df = df[sampling_col]
        to_db = to_db = list(df.itertuples(index=False, name=None))  
    
    
    cur.executemany('''INSERT OR REPLACE INTO sample_information (
            seq_id, accession, box_number, well, number_plants) VALUES (?, ?, ?, ?, ?);''', to_db)
    
    
    # update the log book with entries being inserted
    with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
        log.write('\n{0} -- Inserted/Updated {1} entries into sample_information table from sheet : {2}'.format(datetime.datetime.now(), len(to_db), file_name))
    
    
    #  check the database for any duplicated entries from sample_information and no_tissue_sampling tables (ie. where we 
    #  have re-planted and successfully harvested tissue),and update the comments section when something has been resampled, 
    #  do not delete the line from the table, that causes some concern in the whole thing getting deleted
    
    cur.execute('UPDATE no_tissue_sampling SET comments="resampled" WHERE accession in (SELECT accession FROM sample_information)')
    
    conn.commit()
    
    conn.close()
    
    
    # move sampling sheet into a new folder for files that have been successfully uploaded
    uploaded_path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/2.  GH Sampling Sheets/uploaded samples/'
    os.rename(file_path, '{}{}'.format(uploaded_path, file_name))

    guilogupdate = '{0} -- Inserted/Updated {1} entries into sample_information table from sheet : {2}'.format(datetime.datetime.today().strftime("%m/%d/%Y"), len(to_db), file_name)
    return guilogupdate

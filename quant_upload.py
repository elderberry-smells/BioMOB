# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 11:14:41 2018

Upload the quantification data from the quant folder into the database in the sampling_information 
table.  

@author: jamesbc
"""
import pandas as pd
import sqlite3
import glob
import datetime
import os

def failed_extraction(dataframe, dbcursor):
    '''look through the quantification data from the passed through df, determine which samples 
    failed, and remove them from the main df, returning a failed extraction df (with non-sampled wells
    excluded before entering into database)'''
    
    a = dataframe[dataframe['DNA Concentration'].isnull()]
    box = dataframe.box_number.unique
    
    # remove the rows where they were left empty in sampling, and not actually a failed extraction
    
    box = dataframe.at[1,'box_number']
    all_wells = dbcursor.execute("SELECT well FROM sample_information WHERE box_number='%s'" % box).fetchall()  # list of wells actually sampled in the db
    
    well_list = []  # empty list to throw all the wells that were actually sampled into
    for wells in all_wells:
        well_list.append(wells[0])
    
    # look at the 'a' dataframe and remove any wells that ARE NOT in the well list
    a = a[a['well'].isin(well_list)]
    
    return a  # return the dataframe of failed extractions only


def upload_quantsDB():
    
    # connect to the database
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor()  
        
#    select the files to upload into the database using glob
    quant_path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/3.  Quantification data'
    os.chdir(quant_path)

    # get a list of all xlsx files in the quantification folder
    extension = 'xlsx'
    xlsx_results = [c for c in glob.glob('*.{0}'.format(extension))]
    num_sheets = len(xlsx_results)  # the number of files found in the folder
    
    if num_sheets == 0:
        guilogupdate = 'There are no quantification files in the quant folder'
        return guilogupdate
    
    else:
        
        
        df = pd.DataFrame()  # empty dataframe to append to
        no_dna_df = pd.DataFrame()  # empty dataframe to append to
        
        quant_col = ['box_number', 'well', 'DNA Concentration']
        
        for xlfile in xlsx_results:
            data = pd.read_excel(xlfile, sheet_name='summarized_data')
            
            # clean up the data dataframes before you append them to the main df
            data = data[quant_col]  # remove any columns not necessary for upload to db
            no_data = failed_extraction(data, cur)  # get the failed/empty wells into a seperate df
            data = data.dropna(how='any')  # remove the empty/failed wells from main dataframe
            
            
            df = df.append(data)  # update the 
            no_dna_df = no_dna_df.append(no_data)
        
        # update the sample_information table with quants, matching the box_number and well
        df = df[['DNA Concentration', 'box_number', 'well']]  # change the column order to match the SQL query
        to_db = list(df.itertuples(index=False, name=None))
        
        cur.executemany('''UPDATE sample_information SET quant=? WHERE box_number=? AND well=?;''', to_db)
        
        # write into the failed_extraction table all the failed extraction, grab the accession number for the failed well for the table
        no_dna_df = no_dna_df[['box_number', 'well']]
        nan_db = list(no_dna_df.itertuples(index=False, name=None))
        
        cur.executemany('''INSERT OR REPLACE INTO failed_extraction
                        SELECT accession, box_number, well 
                        FROM sample_information 
                        WHERE box_number=? AND well=?;''', nan_db)
        
        #  Write quantifications and failed extractions to the log file 
        with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
            log.write('\n{0} -- Updated {1} quantifications in sample_information table from {2} quantification sheets'.format(datetime.datetime.now(), len(to_db), num_sheets))
        
            if len(nan_db) > 0:
                log.write('\n{0} -- Inserted {1} entries into failed_extraction table'.format(datetime.datetime.now(), len(nan_db)))
        
        
        conn.commit()
        conn.close()
        
        # move the files into a new folder after they have been uploaded to the database
        uploaded_path = 'L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/3.  Quantification data/uploaded quants/'
        for i in xlsx_results:
            os.rename('{0}/{1}'.format(quant_path, i), '{0}{1}'.format(uploaded_path, i))
        
        guilogupdate = '{0} -- Uploaded {1} quantifications into sample_information table from {2} quantification sheets'.format(datetime.datetime.today().strftime("%m-%d-%Y"), len(to_db), num_sheets)
        return guilogupdate


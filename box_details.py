# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 14:26:29 2018

@author: JamesBC

Take the sampling sheet that houses a lot of the dates tasks were done, and insert that 
data into the database into the box_details table.  This will also be the table that 
houses the library names, adapter sets used on the samples, and locations of the plates/libraries
"""

import pandas as pd
import sqlite3
import datetime

#  select the file that is being uploaded into the database (should be the same working file every time)
def updateBoxDetails():
    # open the file as a dataframe with pandas
    df = pd.read_excel('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/sampling schedule.xlsx')
       
    # grab only the columns that exist in the database for shipment details,
    cols = ['box_number', 'plant_type', 'sampled', 'submitted', 'extracted', 'quantified', 'adapter_set',
           'sequenced', 'library_id', 'sequence_path', 'avg_fragment', 'lib_conc']
    
    df = df[[x for x in df.columns if x in cols]]
    
    # make sure the type of data in the dat columns is formatted as string (type is TEXT in database, not date-time)
    df[['sampled', 'submitted', 'extracted', 'quantified', 'sequenced']] = df[['sampled', 'submitted', 'extracted', 'quantified', 'sequenced']].astype(str)
        
    to_db = list(df.itertuples(index=False, name=None))

    
    #  set up a connection to the database
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor() 
    
    #  add the information into the database from the to_db tuple
    cur.executemany('''INSERT OR REPLACE INTO box_details (
            box_number, plant_type, sampled, submitted,
            extracted, quantified, adapter_set,
            sequenced, library_id, sequence_path, avg_fragment, lib_conc)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', to_db) 
    
    # write an update in the database log sheet
    with open('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/database_log.txt', 'a') as log:
        log.write('\n{0} -- updated box_details table'.format(datetime.datetime.now()))
        
        
    #  look up values in the adapter set column and, if present, add corresponding index_name to the sample_information table
    cur.execute("select adapter_set, box_number from box_details where adapter_set IS NOT NULL AND adapter_set !='';")
    assigned_adapter = cur.fetchall()   
    #  this makes a list of tuples of anything that has an adapter set assigned
    #  example --  [('1A', 1), ('1B', 2), ('1C', 3), ('1D', 4)]
    
    box_nums = [i[1] for i in assigned_adapter]  # just the box numbers
    adap_nums = [i[0] for i in assigned_adapter]  # just the adapter sets
    adap_nums = list(set(adap_nums))  # remove duplicates
    
    if len(assigned_adapter) > 0:  # there have been adapters added to samples
        # update the sample_information table with adapter_set used
        cur.executemany('UPDATE sample_information SET adapter_set=? WHERE box_number=?;', assigned_adapter)
        
        # get a dataframe of all the samples that have adapters assigned.
        cur.execute('SELECT * FROM sample_information WHERE box_number in ({0})'.format(', '.join('?' for _ in box_nums)), box_nums)
        sample_info = cur.fetchall()
        sample_cols = ['sample_id', 'seq_id', 'accession', 'box_number', 'well', 'box_id', 'number_plants', 'quant', 'adapter_set', 'index_name']
        sample_df = pd.DataFrame(sample_info, columns=sample_cols)
        sample_df.drop(['index_name'],  axis=1, inplace=True, errors='ignore') # remove the blank index_name as that will be grabbed by merge
       
        # get a dataframe of just well and index_id of adapter set and merge that with the sample df
        cur.execute('SELECT adapter_set, well, index_name FROM adapter_sets WHERE adapter_set IN ({0})'.format(', '.join('?' for _ in adap_nums)), adap_nums)
        adap_info = cur.fetchall()
        adap_df = pd.DataFrame(adap_info, columns =['adapter_set', 'well', 'index_name'])
        
        # join the adapter and sample dataframes
        joined_df = pd.merge(left=sample_df, right=adap_df, how='left')
        join_cols = ['index_name', 'seq_id'] 
        joined_df = joined_df[join_cols] # just keep these 2 values
        #joined_df['submitted'] = joined_df['submitted'].astype('date')
    
        
        # make a list of tuples of the dataframe for insert into the database
        adap_todb = list(joined_df.itertuples(index=False, name=None))
    
        # update the sample_information table with the index_name
        cur.executemany('UPDATE OR IGNORE sample_information SET index_name=? WHERE seq_id=?;', adap_todb)
        
        conn.commit()
        
    else:
        conn.commit() 
        conn.close() 
    
    guilogupdate = '{0} -- updated box_details table'.format(datetime.datetime.today().strftime("%m/%d/%Y"))
    return guilogupdate


# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 14:52:55 2018

create a tab delimited sample sheet for a box in the database, linking the path to the sequence file, seq_id and index name in
the format that is required for the GBS_PIPELINE protocol

@author: jamesbc
"""
import pandas as pd
import numpy as np
import sqlite3
import glob
import os
import datetime


def get_samplesheets(save_path):
    
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor()  
    guilogupdate = '{0} -- Created Sample sheets:'.format(datetime.datetime.today().strftime("%m-%d-%Y"))
    
    # read the sample scheduler excel sheet into a dataframe
    details_df = pd.read_excel('L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/sampling schedule.xlsx')
    
    # get the rows where there is a sequence path only, remove columns that are not needed
    seq_db = details_df.loc[details_df['sequence_path'].notnull()]
    seq_db = seq_db[['box_number', 'sequence_path']]
    item = list(seq_db.itertuples(index=False, name=None))
        
    # get the unique pathway values, file names for the remaining rows
    path_file = [i for i in seq_db.sequence_path.unique()]
    samplesheet_path, filename = [os.path.split(i)[0] for i in path_file], [os.path.split(i)[1] for i in path_file]
    sequence_number = [i.rsplit('_', 1)[0] for i in filename]
    
    # make a sample list that contains only those pathways that have not already generated a sample sheet
    txt_files = [os.path.split(i)[-1] for i in glob.glob('{}/*.{}'.format(samplesheet_path[0], 'txt'))]
    sample_list = [f for f in sequence_number if '{0}_samplesheet.txt'.format(f) not in txt_files]
    
    # get the unique box number and the sequence path for the samples that need a sample sheet generated into a list   
    generated = []
    for i in sample_list:
        for samp in item:
            if i in samp[1]:
                generated.append(samp)
    
    # combine any samples that have the same path/sequence file, as they will be one file only
    dict_of_paths = {}
    for boxes in generated:
        if boxes[1] in dict_of_paths:
            dict_of_paths[boxes[1]].append(boxes[0])
        else:
            dict_of_paths[boxes[1]] = [boxes[0]]
    
    
    # connect to the database and make a dataframe out of each dict entry
    for box in dict_of_paths.items():

        # make a file name for each df you pull from database
        save_path = "L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/5.  Adapter Sets/2.  Pipeline sample sheets/"
        file_save = os.path.split(box[0])[1].rsplit('_', 1)[0]  # get the file name without the pathway
        fname = '{0}{1}_samplesheet.txt'.format(save_path, file_save)        
        
        if len(box[1]) == 1:
            # select all the info you need for the sample -- Sample_number (autoincrement), Index_name, sample_id(seqid), Sequence_file
            query = '''SELECT index_name, seq_id, box_details.sequence_path
                    FROM sample_information
                    INNER JOIN box_details 
                    ON sample_information.box_number = box_details.box_number 
                    WHERE sample_information.box_number = {}'''.format(box[1][0])
            
            dbinfo = cur.execute(query).fetchall()
            df = pd.DataFrame(dbinfo, columns = ['Index_name', 'Sample_ID', 'Sequence_file'])
            df.index = np.arange(1, len(df) + 1)
            df.index.name='Sample_number'
            
        elif len(box[1]) == 2:
            query1 = '''SELECT index_name, seq_id, box_details.sequence_path
                    FROM sample_information
                    INNER JOIN box_details 
                    ON sample_information.box_number = box_details.box_number 
                    WHERE sample_information.box_number = {}'''.format(box[1][0])
                    
            query2 = '''SELECT index_name, seq_id, box_details.sequence_path
                    FROM sample_information
                    INNER JOIN box_details 
                    ON sample_information.box_number = box_details.box_number 
                    WHERE sample_information.box_number = {}'''.format(box[1][1])
            
            dbinfo1 = cur.execute(query1).fetchall()
            df1 = pd.DataFrame(dbinfo1, columns = ['Index_name', 'Sample_ID', 'Sequence_file'])
            
            dbinfo2 = cur.execute(query2).fetchall()
            df2 = pd.DataFrame(dbinfo2, columns = ['Index_name', 'Sample_ID', 'Sequence_file'])
            
            frames = [df1, df2]
            
            df = pd.concat(frames)
            df.index = np.arange(1, len(df) + 1)
            df.index.name='Sample_number'
        
        df.to_csv(fname, header=True, index=True, sep='\t', mode='w')
        
        guilogupdate = '{0} {1}'.format(guilogupdate, file_save)

    
    return guilogupdate
 
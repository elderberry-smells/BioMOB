# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 13:16:40 2018

Script for creating a metrics sheet, showcasing how many of each type of plant that has been 
extracted, and wether they were greenhosue or field lines.  This is the type of output you can send to 
PGRC to give updates on what has been done to date in the BioMOB project.

@author: jamesbc
"""

import sqlite3
import pandas as pd
from datetime import date
import openpyxl

def generateMetrics():
    
    # ----------------------------------------------------------------------------------------------------------------
    # ----------------------------------------- Connection to Database  ----------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    
    # connect to the database to grab the information needed to run metrics
    conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
    conn.text_factory = str 
    cur = conn.cursor() 
    
    # join info from 3 tables, plant, box number, plant type, and accession (unique key to join on) 
    shipments = cur.execute('''SELECT 
                            sample_information.accession, 
                            sample_information.box_number, 
                            shipment_details.plant, 
                            box_details.plant_type,
                            box_details.sequence_path
                            from sample_information 
                            INNER JOIN shipment_details 
                            ON 
                            shipment_details.accession = sample_information.accession 
                            INNER JOIN box_details 
                            ON 
                            box_details.box_number = sample_information.box_number''').fetchall()
    
    # ----------------------------------------------------------------------------------------------------------------
    # ----------------------------------------- CREATING THE DATAFRAMES ----------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    
    cols = ['accession', 'box', 'Plant', 'shipment_info', 'sequence_path']  # columns for the dataframe
    
    df = pd.DataFrame(shipments, columns=cols)
    df['Plant'] = df['Plant'].str.lower()  # lower case the plant column
    
    
    #  create a seperate dataframe for the sequenced plant types
    df['sequence_path'] = df.sequence_path.apply(lambda x: 0 if x==None else 1)  # bool 1 if sequenced, 0 if not sequenced
    
    # count the sequence_path columns 0's and 1's for each plant type (plants joined in groupby) 
    seq_num = df.groupby(['Plant', 'sequence_path']).size().reset_index().rename(columns={0:'Sequence Count'})  
    seq_num = seq_num[seq_num.sequence_path != 0]  # remove any lines (plants) that have 0 as sequence_count
    seq_num = seq_num.drop('sequence_path', 1)  # drop the sequence_path column, leaving only plant and sequence_count in DF
    
    # make a dataframe for just field data
    field_df = df[df['shipment_info'].str.contains('field')]
    field_df2 = field_df.groupby(['Plant']).size().reset_index().rename(columns={0:'Field Count'})  # count the plant types for field  
    
    # make a dataframe for just greenhosue data
    gh_df = df[~df['shipment_info'].str.contains('field')]  #  isolate greenhouse data
    gh_df2 = gh_df.groupby(['Plant']).size().reset_index().rename(columns={0:'GH Count'})  # count the plant types for greenhouse
    
    # merge the field and greenhouse dataframes, then merge that with the sequence data
    field_gh_merge = pd.merge(gh_df2, field_df2, how='outer')  
    final_metrics = pd.merge(field_gh_merge, seq_num, how='outer')
    
    # clean up the final metric dataframe
    final_metrics = final_metrics.fillna(0)  # remove NaN values, replace with 0's
    final_metrics['Total'] = final_metrics['Field Count'] + final_metrics['GH Count']  # add a total column
    final_metrics = final_metrics.sort_values(['Total'], ascending=False)  # sort the rows by number of Total plants done
    
    # change the order of the columns
    metric_columns = ['Plant', 'GH Count', 'Field Count', 'Total', 'Sequence Count']
    final_metrics = final_metrics[metric_columns]
    
    conn.close()
    
    return final_metrics
    

def graph_metrics(df, pathway="L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/7.  Lab Book and miscellaneous/metrics/"):
    
    # ----------------------------------------------------------------------------------------------------------------
    # -------------------------------------------- VISUALIZATIONS ----------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    
    #make a stacked bar graph visualization
    vis_df = df[['Plant', 'GH Count', 'Field Count']]
    vis_df = vis_df[vis_df['GH Count'] + vis_df['Field Count'] > 10]
    ax = vis_df.plot.bar(stacked=True, x=['Plant'], rot=90, figsize=(20,15), title='BioMOB Metrics {}'.format(date.today()))
    
    # save the figure so it can be inserted into an excel sheet
    fig = ax.get_figure()
    figure_filename = '{0}BioMOB Metrics graph_{1}.png'.format(pathway, date.today())
    fig.savefig(figure_filename)
    metrics_filename = '{0}BioMOB Metrics_{1}.xlsx'.format(pathway, date.today())  # name of the image
    
    
    # ----------------------------------------------------------------------------------------------------------------
    # --------------------------------------------- EXCEL WORK -------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------
    
    df.to_excel(metrics_filename, index=False)  # write to excel
    
    #  add the graph to the excel sheet
    wb = openpyxl.load_workbook(metrics_filename)
    ws = wb.active
    img = openpyxl.drawing.image.Image(figure_filename)
    img.anchor(ws.cell('F1'))
    ws.add_image(img)
    wb.save(metrics_filename)
    
    
    guilogupdate = "Metrics sheet generated.  View in {}".format(pathway)
    
    return guilogupdate

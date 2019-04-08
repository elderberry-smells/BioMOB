# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 10:47:33 2018

@author: JamesBC
"""

import sqlite3


#conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/bioMOB_database.db")
conn = sqlite3.connect("L:/MolecularGroup/Molecular/Parkin Lab/Brian James/Genetic Diversity Program/8.  Database and sampling schedule/db/test_biomobDB.db")
conn.text_factory = str
cur = conn.cursor()

cur.execute('''CREATE TABLE shipment_details (
        shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        accession TEXT UNIQUE,
        taxon TEXT,
        plant TEXT,
        name TEXT,
        habit TEXT,
        country TEXT,
        "donor type" TEXT,
        barcode TEXT,
        alt TEXT,
        "donor institute" TEXT,
        "donor country" TEXT,
        origin TEXT, 
        received TEXT
)''')


cur.execute('''CREATE TABLE box_details (
          box_number INTEGER UNIQUE,
			plant_type TEXT,
			sampled TEXT,
          submitted TEXT,
			extracted TEXT,
			quantified TEXT,
          adapter_set TEXT,
		   sequenced TEXT,
          library_id TEXT,
          sequence_path TEXT,
          avg_fragment INTEGER,
          lib_conc REAL
)''')


cur.execute('''CREATE TABLE sample_information (
          sample_id INTEGER PRIMARY KEY AUTOINCREMENT,
          seq_id TEXT UNIQUE NOT NULL,
			accession TEXT UNIQUE,
			box_number INTEGER,
			well TEXT,
			box_id TEXT,
          number_plants INTEGER,
			quant REAL,
          adapter_set TEXT,
		   index_name TEXT
)''')


cur.execute('''CREATE TABLE adapter_sets (
          adapter_id INTEGER PRIMARY KEY AUTOINCREMENT,
			adapter_set TEXT,
			plate TEXT,
			well TEXT,
			index_name TEXT,
			barcode TEXT,
			date TEXT
)''')

cur.execute('''CREATE TABLE no_tissue_sampling (
          tissue_id INTEGER PRIMARY KEY AUTOINCREMENT,
			accession TEXT,
          taxon TEXT,
          plant TEXT,
          name TEXT,
          comments TEXT
)''')

cur.execute('''CREATE TABLE failed_extraction (
			accession TEXT,
			box_number INTEGER,
			well TEXT

)''')

cur.execute('''CREATE TABLE DNA_storage_details (
        box_number INTEGER UNIQUE,
        room_number TEXT,
        storage_unit TEXT,
        compartment TEXT,
        shelf_number TEXT
        
)''')


conn.commit()
conn.close()

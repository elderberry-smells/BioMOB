# BioMOB Application

## Background to Research Project
### Biodiversity and bioresources

Plant and animal germplasm is acquired and characterized to identify superior characteristics for use in science and breeding programs. This includes:

    •Characterizing ecological and evolutionary processes relevant to agricultural crops to ensure efficient conservation of genetic diversity of cultivated plants of relevance for Canada and their wild relatives to prevent genetic erosion.

    •Acquiring and characterizing material for plant breeders for existing and new crops; screening germplasm relevant to Canada for disease resistance; characterizing plants with improved traits such as resistance to diseases and drought; development and refinement of techniques for successful conservation of animal germplasm from different livestock spps.

### How the application works

This application is used to manage the day-to-day data and logistics of the BioMOB project.  The application is the front end interface to an SQLite database, which houses the project info for samples being grown, extracted, and sequenced in GBS protocols.  The utility of the application is to make fillable sample sheets (written in excel xlsx files) for the lab and greenhouse staff to use and then import/write that information back into the database.  Some metrics related and bioinformatics related exports from the database are also done.


### Main Window
![Main Window](https://raw.github.com/elderberry-smells/BioMOB/screenshots/main_window.PNG)

This is the main window for the application.  There are certain stage gates that the samples move through in the project, and a button is assigned for essentially each one of those steps.  

    •Load Shipment details - Take the accession data from the samples being planted, and any relevant data to the line and insert it into the database.  Return a sampling sheet for greenhosue crew.
    •Load GH Samples - Load the box and well locations into the database, update any samples that failed to germinate
    •Load Quantification Data - update the samples to have a quantification (post DNA extraction) in the database
    •Update sampling sheet - update the database to reflect the current sampling sheet (which is an excel working sheet being updated by greenhouse and lab personnel)
    •Table view - opens a "database viewer" window, that can visualize the database tables and metrics
    •analyze flourometer data - this does not link to the database, but is used to analyze the typical output of the flourimeter (a csv file with flourescent data)

### Table view window

This new window is a database viewer with a bit of different utility.  The Qt label is utilizing PandasModel to view data that is queried from the database.  The viewer also has a count on samples for each specific view.  

If you sort the table in any way, you can export the data from the application while retaining the sorted features, it will export it as "(SORTED)table_name.xlsx"

![Table View](https://raw.github.com/elderberry-smells/BioMOB/screenshots/table_view.PNG)

You can view individual tables, such as sample information

![Sample View](https://raw.github.com/elderberry-smells/BioMOB/screenshots/table_sampleinfo.PNG)

Or you can view sample information specific to a certain crop using the drop down.  
![Sorted View](https://raw.github.com/elderberry-smells/BioMOB/screenshots/table_sampleinfo_barley.PNG)

view individual boxes
![Box View](https://raw.github.com/elderberry-smells/BioMOB/screenshots/table_boxview.PNG)

Or generate a metrics (summarized by crop type, where sample was collected, and how many have been sequenced).  If you choose to save the table view when metrics is selected in the drop down, it will write a new excel file with the metrics info, the date it was saved, and include a matplotlib chart that breaks down the plant numbers in GH versus field.
![Metrics View](https://raw.github.com/elderberry-smells/BioMOB/screenshots/table_metrics.PNG)


## Individual script utility

#### BioMOB_UI.py
This is the script to run the application.  All other python files need to be in the same folder for importing into this script

#### biomob_db.py
create the database based on the following schema:
![DB schema](https://raw.github.com/elderberry-smells/BioMOB/screenshots/schema.png)

#### adapter.py
upload the adapters for GBS into the database

#### box_details.py
update the information from the sampling sheet into the database

#### gh_sampling.py 
Upload any sampling information from lines grown and sampled into the database.  This should be done based off the form created by running pgrc_shipment.py (the button "Load Shipment Details" creates the form)

#### metrics.py
Queries the database and produces a sorted table and graph for plants sampled, GH versus field, # sequenced runs etc.

#### pgrc_shipments.py
uploads any sample information into the database for seed collected, and outputs a fillable excel form for GH staff to use for sampling

#### quant_program.py
analyzes the output from a flourimeter csv file, splits the samples in the file, averages the values if multiple reads, and outputs the DNA concentrations in split xlsx files, ready for upload into the database

#### quant_upload.py
take quantification data and update the sample_information with those values.  If samples failed to extract, move that sample information into a new table "failed extraction"

#### samplesheet.py
Create a txt document of sample number, sample name, index, and location of sequence data for use in our bioinformatics pipeline

## Acknowledgements
I utilized the PandasModel module, which is a great script for visualizing pandas data in the PyQt5 GUI.  It can be found [here](https://github.com/Winand/dataframemodel/blob/master/pandasmodel.py).  

GUI was created using [PyQt5](https://pypi.org/project/PyQt5/)

Everything else was written by myself.

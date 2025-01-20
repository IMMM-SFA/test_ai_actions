# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import os 
import geopandas
import contextily as cx
import rasterio
from rasterio.mask import mask
from rasterio.plot import show

os.chdir(Path to Step 1b folder)

# Import water provider service region boundaries used for clipping the 
# population rasters
service_bnds = geopandas.read_file("Artes_service_regions_esri_102003.shp")  
service_bnds = service_bnds.where(service_bnds.Artes_se_3 == 1)
service_bnds = service_bnds.dropna(thresh = 3)
service_bnds = service_bnds.reset_index(drop = True)
service_ids = service_bnds.Artes_serv

#%% 

# 'SSP5' or 'SSP3' to process population rasters for SSP scenario and generate 
# a single CSV of population outputs 
ssp = 'SSP3' # 'SSP5' or 'SSP3'

raster_files = os.listdir()
raster_names = []

for file in raster_files:
    if file[0:7] == 'LA_' + ssp and file[-3:] == 'tif':
        raster_names.append(file)

# Create dataframe to store urban class area for each provider for each decade 
columns = ['2010','2020','2030','2040','2050','2060','2070','2080','2090','2100']

data = np.zeros((len(service_ids), 10))

pop_df = pd.DataFrame(data = data.copy(), columns = columns)

pop_df.insert(0, 'Service_region', service_ids)

# Import urban landclass raster 
for decade in range(10):
    inRas = raster_names[decade] # list of all input rasters 
    src = rasterio.open(inRas)
    # show(src) # visualize raster (optional)
    for provider in range(len(service_ids)):
        # select service region polygon used for mask
        region_bounds = service_bnds[service_bnds['Artes_serv'] == service_ids[provider]] 

        # clip raster by service region boundary 
        with rasterio.open(inRas) as src:
            region_bounds=region_bounds.to_crs(src.crs)

            out_image, out_transform=mask(src,region_bounds.geometry,crop=True)
            out_meta=src.meta.copy() # copy the metadata of the source DEM
    
        # area of clipped raster
        area = np.array(out_image[0,:,:])
        area_filt = np.where(area > 0, area, np.nan)
        area_filt = area_filt.flatten()
        area_filt = area_filt[~np.isnan(area_filt)]
        region_pop = sum(area_filt)
    
        # update datframes with results 
        pop_df.iloc[provider, decade+1] = region_pop


pop_df.to_csv('service_region_population_' + ssp +'_2010_2100.csv')

#%% plot results 

pop_ssp3 = pd.read_csv('service_region_population_SSP3_2010_2100.csv', index_col = 0)
pop_ssp5 = pd.read_csv('service_region_population_SSP5_2010_2100.csv', index_col = 0)

# All LA
Fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(7,5))
axs.plot(np.linspace(2010, 2100, 10), np.sum(pop_ssp5.iloc[:,1:], axis = 0), color = 'black', label = 'SSP5')
axs.plot(np.linspace(2010, 2100, 10), np.sum(pop_ssp3.iloc[:,1:], axis = 0), color = 'blue', label = 'SSP3')
axs.set_ylabel('Population')
axs.legend()
plt.tight_layout()
plt.grid(visible = True)

# Specific service region 
Fig, axs = plt.subplots(nrows=1, ncols=1, figsize=(4,3))
i = 67
axs.plot(np.linspace(2010, 2100, 10), pop_ssp5.iloc[i,1:], color = 'black', label = 'SSP5')
axs.plot(np.linspace(2010, 2100, 10), pop_ssp3.iloc[i,1:], color = 'blue', label = 'SSP3')
axs.set_ylabel('Population')
axs.legend()
axs.set_title('Service Region: ' + service_ids[i])
plt.tight_layout()
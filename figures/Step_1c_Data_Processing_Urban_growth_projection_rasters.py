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

path = Path to Step 1c Folder

os.chdir(path)

# Import service regions boundaries 
service_bnds = geopandas.read_file("Artes_service_regions_updated.shp")  
service_bnds = service_bnds.to_crs(epsg=3857) # convert CRS to basemap CRS 
service_bnds = service_bnds.where(service_bnds.Artes_se_3 == 1)
service_bnds = service_bnds.dropna(thresh = 3)
service_bnds = service_bnds.reset_index(drop = True)
service_ids = service_bnds.Artes_serv


#%% Urban land projection data processing. Pixel counts for each NLCD 
# Urban Land Class (LC) for each water provider region in LA 

ssp = 'SSP3' # Select SSP scenario 'SSP3' or 'SSP5' 
ssp_num = 3 # integer, either 3 or 5
scenarios = ['low', 'med', 'hi'] # zoning restrictiveness scenarios 

for n in range(3):
    
    scenario = scenarios[n]
    
    # Path to dataset folder 
    path_loc = path + ssp + "/" + ssp + "_" + scenario
    os.chdir(path_loc)
    
    raster_files = os.listdir()
    raster_names = []
    
    for file in raster_files:
        if file[-5] == 'f' and file[-3:] == 'tif':
            raster_names.append(file)
    
    output_names = [ssp + '_' + scenario + '_21_f', ssp + '_' + scenario + '_22_f', 
                    ssp + '_' + scenario + '_23_f', ssp + '_' + scenario + '_24_f']
    
    # Create dataframes to store urban class area for each provider for each decade 
    columns = ['2010','2020','2030','2040','2050','2060','2070','2080','2090','2100']
    
    data = np.zeros((len(service_ids), 10))
    
    class_21_df = pd.DataFrame(data = data.copy(), columns = columns)
    class_22_df = pd.DataFrame(data = data.copy(), columns = columns)
    class_23_df = pd.DataFrame(data = data.copy(), columns = columns)
    class_24_df = pd.DataFrame(data = data.copy(), columns = columns)
    class_21_df.insert(0, 'Service_region', service_ids)
    class_22_df.insert(0, 'Service_region', service_ids)
    class_23_df.insert(0, 'Service_region', service_ids)
    class_24_df.insert(0, 'Service_region', service_ids)
    
    # name of clipped output raster, can be continuosly overwritten, uncomment this and 
    # code within loop below to visualize clipped provider region for each decade and 
    # provider  
    # outRas = 'test.tif' 
    
    # Import urban landclass raster 
    for decade in range(10):
        inRas = raster_names[decade] # list of all input rasters (i.e ssp5_2010_f, ssp5_2020_f, .... )
        src = rasterio.open(inRas)
        #show(src)
        for provider in range(len(service_ids)):
            # select service region polygon used for mask
            region_bounds = service_bnds[service_bnds['Artes_serv'] == service_ids[provider]] 
    
            # clip raster by service region boundary 
            with rasterio.open(inRas) as src:
                region_bounds=region_bounds.to_crs(src.crs)
                # print(region_bounds.crs)
                out_image, out_transform=mask(src,region_bounds.geometry,crop=True)
                out_meta=src.meta.copy() # copy the metadata of the source DEM
        
                # out_meta.update({
                #     "driver":"Gtiff",
                #     "height":out_image.shape[1], # height starts with shape[1]
                #     "width":out_image.shape[2], # width starts with shape[2]
                #     "transform":out_transform
                # })
                
                # with rasterio.open(outRas,'w',**out_meta) as dst:
                #     dst.write(out_image)
            
            # visualize clipped region 
            # src = rasterio.open("test.tif")
            # show(src)
    
            # area of clipped raster
            area = np.array(out_image[0,:,:])
            area_filt = np.where(area > 0, area, np.nan)
            area_filt = area_filt.flatten()
            area_filt = area_filt[~np.isnan(area_filt)]
            region_area = len(area_filt)
            
            # save total provider region area (total pixel count) 
            if decade == 0 and provider == 0:
                region_areas = pd.DataFrame(data = np.zeros(len(service_ids)))
                region_areas.insert(0, 'Service_region', service_ids)
                region_areas.iloc[provider,1] = region_area
                
            elif decade == 0:
                region_areas.iloc[provider,1] = region_area
                
            else:
                pass
            
            # filter by each urban land use class 
            class_21 = np.where(area_filt == 21, area_filt, np.nan)
            class_21 = class_21[~np.isnan(class_21)]
            class_22 = np.where(area_filt == 22, area_filt, np.nan)
            class_22 = class_22[~np.isnan(class_22)]
            class_23 = np.where(area_filt == 23, area_filt, np.nan)
            class_23 = class_23[~np.isnan(class_23)]
            class_24 = np.where(area_filt == 24, area_filt, np.nan)
            class_24 = class_24[~np.isnan(class_24)]
            
    
            # update datframes with results (pixel counts)
            class_21_df.iloc[provider, decade+1] = len(class_21)
            class_22_df.iloc[provider, decade+1] = len(class_22)
            class_23_df.iloc[provider, decade+1] = len(class_23)
            class_24_df.iloc[provider, decade+1] = len(class_24)
    
    
    os.chdir("../")
    region_areas.to_csv('Provider_region_areas.csv') # this only needs to be saved once, this is total pixel count within water provider service regions 
    class_21_df.to_csv(output_names[0] + '.csv') # LC21 pixel counts by decade for each provider 
    class_22_df.to_csv(output_names[1] + '.csv') # LC22 pixel counts by decade for each provider 
    class_23_df.to_csv(output_names[2] + '.csv') # LC23 pixel counts by decade for each provider 
    class_24_df.to_csv(output_names[3] + '.csv') # LC24 pixel counts by decade for each provider 



# Create single Dataframe to aggregate landuse results from all 
# 3 sets of SSP results (SSP3_low, SSP3_med, SSP3_hi). 
# Columns are decades and rows are the various scenario names. 

# Import SPP3 or SSP5 CSVs (i.e., SSP5_hi_21_f, SSP5_hi_22_f, ...) generated 
# from preceding code 

files = os.listdir()
scenarios = []
for i in range(len(files)):
    if files[i][-5] == 'f':
        scenarios.append(files[i])

fields = ['Provider_ID', 'ssp', 'scenario', 'zoning_restriction', 
          'urban_class', '2010', '2020', '2030', '2040', '2050', '2060', '2070', 
          '2080', '2090', '2100']

# Populate dataframe with urban projection model settings 
intensity = ['int','int', 'int'] 
scenario = ['low', 'med', 'hi']
zoning_restriction = ['True', 'True', 'True']
LU_class = [21, 22, 23, 24]

Aggregated_LC_df = pd.DataFrame(columns = fields) 
LC_list = np.tile(LU_class, int((len(scenarios))/4))
LC_list = np.sort(LC_list)
intensity_list = np.tile(intensity, 4)
scenario_list = np.tile(scenario, 4)
zoning_restriction_list = np.tile(zoning_restriction, 4)

scenario_files = []

# load specific scenario output 
for k in range(len(LC_list)):
    string = ssp + '_' + scenario_list[k] + '_' + str(LC_list[k])
    string = string + '_f.csv'
    
    scenario_file = []
    for i in range(len(scenarios)):
        if string in scenarios[i]:
            scenario_file.append(scenarios[i])
    
    scenario_files.append(scenario_file) # find specific scenario and LC num CSV (SSP_low_21)
    
    # load scenario to dataframe 
    scenario_data = pd.read_csv(scenario_file[0], index_col= 0)
    
    # append scenario data for each Artes node 
    for r in range(len(scenario_data.iloc[:,0])):
        new_row = {'Provider_ID': scenario_data.iloc[r,0], 'ssp': ssp_num, 'scenario': scenario_list[k], 
                   'zoning_restriction': zoning_restriction_list[k], 'urban_class': LC_list[k], 
                   '2010': scenario_data.iloc[r, 1], '2020': scenario_data.iloc[r, 2], 
                   '2030': scenario_data.iloc[r, 3], '2040': scenario_data.iloc[r, 4], 
                   '2050': scenario_data.iloc[r, 5], '2060': scenario_data.iloc[r, 6], 
                   '2070': scenario_data.iloc[r, 7], '2080': scenario_data.iloc[r, 8], 
                   '2090': scenario_data.iloc[r, 9], '2100': scenario_data.iloc[r, 10]}
        
        Aggregated_LC_df = Aggregated_LC_df.append(new_row, ignore_index = True)

Aggregated_LC_df.to_csv(ssp + '_Aggregated_landclass_projection_data.csv')

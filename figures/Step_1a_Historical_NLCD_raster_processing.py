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

os.chdir(Step 1a folder path)

# Import water provider service regions boundaries 
service_bnds = geopandas.read_file("Artes_service_regions_updated.shp")  
service_bnds = service_bnds.to_crs(epsg=3857) # convert CRS to basemap CRS 
service_bnds = service_bnds.where(service_bnds.Artes_se_3 == 1)
service_bnds = service_bnds.dropna(thresh = 3)
service_bnds = service_bnds.reset_index(drop = True)
service_ids = service_bnds.Artes_serv

#%% 

# outRas = 'test.tif' # name of clipped output raster, can be coninuosly overwritten
NLCD_dataset = "NLCD_2019_Land_Cover_L48_20210604_clNjCWtDUmB6F5woFH6g.tiff"

# create dataframes to store urban class area for each provider for each decade 
columns = ['LC_21','LC_22','LC_23','LC_24']

data = np.zeros((len(service_ids), 4))

provider_NLCD_LC_df = pd.DataFrame(data = data.copy(), columns = columns)
provider_NLCD_LC_df.insert(0, 'Service_region', service_ids)

# Import urban landclass raster 
inRas = NLCD_dataset 
src = rasterio.open(inRas)
show(src)
for provider in range(len(service_ids)):
    # select service region polygon used for mask
    region_bounds = service_bnds[service_bnds['Artes_serv'] == service_ids[provider]] 

    # clip raster by service region boundary 
    with rasterio.open(inRas) as src:
        region_bounds=region_bounds.to_crs(src.crs)
        # print(region_bounds.crs)
        out_image, out_transform=mask(src,region_bounds.geometry,crop=True)
        out_meta=src.meta.copy() # copy the metadata of the source DEM

    #     out_meta.update({
    #         "driver":"Gtiff",
    #         "height":out_image.shape[1], # height starts with shape[1]
    #         "width":out_image.shape[2], # width starts with shape[2]
    #         "transform":out_transform
    #     })
        
    #     with rasterio.open(outRas,'w',**out_meta) as dst:
    #         dst.write(out_image)
    
    # #visualize clipped region 
    # src = rasterio.open("test.tif")
    # show(src)

    # area of clipped raster
    area = np.array(out_image[0,:,:])
    area_filt = np.where(area > 0, area, np.nan)
    area_filt = area_filt.flatten()
    area_filt = area_filt[~np.isnan(area_filt)]
    region_area = len(area_filt)
    
    # save total provider region areas 
    if provider == 0:
        region_areas = pd.DataFrame(data = np.zeros(len(service_ids)))
        region_areas.insert(0, 'Service_region', service_ids)
        region_areas.iloc[provider,1] = region_area
        
    else:
        pass
    
    # filter by each urban land class 
    class_21 = np.where(area_filt == 21, area_filt, np.nan)
    class_21 = class_21[~np.isnan(class_21)]
    class_22 = np.where(area_filt == 22, area_filt, np.nan)
    class_22 = class_22[~np.isnan(class_22)]
    class_23 = np.where(area_filt == 23, area_filt, np.nan)
    class_23 = class_23[~np.isnan(class_23)]
    class_24 = np.where(area_filt == 24, area_filt, np.nan)
    class_24 = class_24[~np.isnan(class_24)]
    

    # update datframes with results 
    provider_NLCD_LC_df.iloc[provider, 1] = len(class_21)
    provider_NLCD_LC_df.iloc[provider, 2] = len(class_22)
    provider_NLCD_LC_df.iloc[provider, 3] = len(class_23)
    provider_NLCD_LC_df.iloc[provider, 4] = len(class_24)

provider_NLCD_LC_df.to_csv("NLCD_LC_areas_historic.csv")


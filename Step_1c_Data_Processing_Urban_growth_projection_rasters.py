Here's a refactored version of your script, organized for readability, maintainability, and reproducibility. I've added comments and structured the code into functions where appropriate:

```python
# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from pathlib import Path

def setup_environment(path):
    """Set up the environment by changing the directory to the specified path."""
    os.chdir(path)

def load_service_boundaries(file_path):
    """Load and preprocess service region boundaries."""
    service_bnds = gpd.read_file(file_path)
    service_bnds = service_bnds.to_crs(epsg=3857)  # Convert CRS to basemap CRS
    service_bnds = service_bnds[service_bnds.Artes_se_3 == 1].dropna(thresh=3).reset_index(drop=True)
    return service_bnds, service_bnds.Artes_serv

def filter_raster_files(files):
    """Filter out raster files ending with 'tif' and 'f'."""
    return [file for file in files if file.endswith('.tif') and file[-5
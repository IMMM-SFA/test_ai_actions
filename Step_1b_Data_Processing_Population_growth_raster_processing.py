Here's the revised version of the script with improvements for readability, organization, and reproducibility. I've added comments and used functions to encapsulate logic, which helps in maintaining and reusing code:

```python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os
import geopandas as gpd
import contextily as cx
import rasterio
from rasterio.mask import mask
from rasterio.plot import show

def load_service_boundaries(filepath):
    """Load service region boundaries and filter for specific criteria."""
    service_bnds = gpd.read_file(filepath)
    service_bnds = service_bnds[service_bnds.Artes_se_3 == 1]
    service_bnds = service_bnds.dropna(thresh=3).reset_index(drop=True)
    return service_bnds

def get_raster_files(path, ssp):
    """Get list of raster files for a given SSP scenario."""
    return [file for file in os.listdir(path) if file.startswith('LA_' + ssp) and file.endswith('.tif')]

def calculate_population(service_bnds, raster_names):

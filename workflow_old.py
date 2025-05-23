#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Filename: workflow.py
Author: Lukas Kaleta
Date: 2025-01-31
Version: 1.0
Description: 
    This script showcases the typical workflow of training an CNN module
    for rain event detection using data from CML.
License: 
Contact: 211312@vutbr.cz
"""


""" Imports """
# Import python libraries

import math
import numpy as np
import itertools
import matplotlib.pyplot as plt

import xarray as xr
import pandas as pd

import torch
import torch.nn as nn
import sklearn.metrics as skl
from sklearn.utils import shuffle
from tqdm import tqdm
import datetime
#from IPython.display import clear_output

# Import external packages
import pycomlink as pycml

# Import own modules
import telcosense_classification.module.cnn_orig as cnn
import telcosense_classification.preprocess_utility_old as preprocess_utility
import telcosense_classification.cnn_utility_old as cnn_utility
# import plot_utility


""" ConstantVariable definitions """
sample_size = 60 #min
num_cmls = 10

cnn_wd_threshold = 0.5
""" Function definitions """


""" Main """

# load 500 CMLs with 1 min time step
cml_set = xr.open_dataset('example_data/example_cml_data.nc', engine='netcdf4') 
cml_set = preprocess_utility.cml_preprocess(cml_set, interp_max_gap='5min')

# load path averaged reference RADOLAN data aligned with all 500 CML IDs with 5 min time step
ref_set = xr.open_dataset('example_data/example_path_averaged_reference_data.nc', engine='netcdf4')
ref_set = ref_set.rename_vars({'rainfall_amount':'rain'})
ref_set = preprocess_utility.ref_preprocess(ref_set, interp_max_gap='20min', resample=sample_size)

ds = preprocess_utility.build_dataset(cml_set, ref_set, sample_size, num_cmls)

## TRAINING
cnn_utility.cnn_train(ds, sample_size, epochs=30, batchsize=int(128), save_param=False)

## CLASSIFICATION
#cnn_prediction = cnn_utility.cnn_classify(ds, sample_size=10, batchsize=50)


ds['cnn_out'] = (('cml_id', 'sample_num'), np.array(cnn_prediction).reshape(num_cmls,-1))
ds['cnn_wd'] = (('cml_id', 'sample_num'), ds.cnn_out.values > cnn_wd_threshold)

# predicted TP, FP, FN
ds['true_wet'] = ds.cnn_wd & ds.ref_wd 
ds['false_alarm'] = ds.cnn_wd & ~ds.ref_wd
ds['missed_wet'] = ~ds.cnn_wd & ds.ref_wd


#plot_utility.plot_cnn_output(ds, cnn_wd_threshold=0.5)




input("Press Enter to continue...")

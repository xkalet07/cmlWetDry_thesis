#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Filename: cnn_telcorain.py
Author: Lukas Kaleta
Date: 2025-03-19
Version: 1.1
Description: 
    CNN architecture for the puirpose of Telcorain CML precipitation detection.
    Inspired by: https://github.com/jpolz/cml_wd_pytorch/tree/main

License: 
Contact: 211312@vutbr.cz
"""

""" Imports """
# Import python libraries
import torch
import torch.nn as nn
import torch.nn.functional as F


""" CNN module architecture definition """

class ConvBlock(nn.Module):
    def __init__(self, kernel_size, dim_in, dim, dim_out):
        super().__init__()
        self.kernelsize = kernel_size
        self.dim_in = dim_in
        self.dim = dim
        self.dim_out = dim_out
        self.proj1 = nn.Conv1d(dim_in, dim, self.kernelsize, padding='same') 	# padding same, padds the input data to match the output dimension 
        self.proj2 = nn.Conv1d(dim, dim_out, self.kernelsize, padding='same')
        self.act1 = nn.ReLU()
        self.act2 = nn.ReLU()

    def forward(self, x,):
        x = self.proj1(x)            
        x = self.act1(x)
        x = self.proj2(x)            
        x = self.act2(x)
        return x

class cnn_class(nn.Module):
    def __init__(self, channels = 2, sample_size = 100, kernel_size = 3, dropout = 0.2, n_fc_neurons = 64, n_filters = [16, 32, 96, 192]):
        super().__init__()
        self.channels = channels
        self.sample_size = sample_size
        self.kernelsize = kernel_size
        self.dropout = dropout
        self.n_fc_neurons = n_fc_neurons
        self.n_filters = n_filters

        ### Convolutional part
        # ConvBlock: def __init__(self, kernel_size, dim_in, dim, dim_out):
        self.cb1 = ConvBlock(self.kernelsize, self.channels, self.n_filters[0], self.n_filters[0])
        self.cb2 = ConvBlock(self.kernelsize, self.n_filters[0], self.n_filters[1], self.n_filters[1])
        self.cb3 = ConvBlock(self.kernelsize, self.n_filters[1], self.n_filters[2], self.n_filters[2]) 
        self.cb4 = ConvBlock(self.kernelsize, self.n_filters[2], self.n_filters[3], self.n_filters[3])
        self.act = nn.ReLU()

        ### Fully Connected part 
        # no pooling implemented: no need
        # neuron layers interlieved with dropout functions
        self.dense1 = nn.Linear(self.n_filters[3], self.n_fc_neurons)
        self.drop1 = nn.Dropout(self.dropout)
        self.dense2 = nn.Linear(self.n_fc_neurons, self.n_fc_neurons)
        self.drop2 = nn.Dropout(self.dropout)
        self.denseOut = nn.Linear(self.n_fc_neurons, self.sample_size)
        self.final_act = nn.Sigmoid()                                  # ACT = activation func, Sigmoid function to diverse values further to 1/0

    
    def forward(self, x):
        ### Conv part
        x = self.cb1(x)
        x = self.cb2(x)
        x = self.cb3(x)
        x = self.cb4(x)
        x = torch.mean(x,dim=-1)
        
        ### FC part
        x = self.act(self.dense1(x))
        x = self.drop1(x)
        x = self.act(self.dense2(x))
        x = self.drop2(x)
        x = self.final_act(self.denseOut(x))

        return x

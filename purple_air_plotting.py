#!/usr/bin/env python3

import time, csv, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

from datetime import datetime


'''
Ploting code for remote purple air

To do:

    Write code that pulls in CSVs every ten minutes and plots the data
    Write code that sends out alerts if data are outside of criteria
    
    CRITERIA (subject to change with more data collection):
    
    All voltages: voltage < 11V & voltage > 15V
    Currents:
        PurpleAir:      current < 50mA & current > 200mA
        WiFi:           current < 50mA & current > 200mA
        Raspberry Pi:   current < 150mA & current > 350mA
        Comms:
            raven:      current < 150mA & current > 1.25A
            satellite:  current < 150mA & current > 1.5A #THIS WILL CHANGE ONCE MORE DATA ON CURRENT CONSUMPTION IS COLLECTED#

    #CSV HEADER DATA#
    Time, PA Current, PA Power, PA Voltage, WIFI Current, WIFI Power, WIFI Voltage, RPi current, RPi Power, RPi Voltage, Comms Current, Comms Power, Comms Voltage
    Time is a datetime string in the form %m%d%Y %H:%M:%S

'''

def reader(path):
    '''
    Reads the csv as a pandas dataframe and returns it for plotting
    
    input param: file_name, the file that has been rsynced from the raspberry pi to the linux box and discovered by the watchdog
    input type: string

    output param: df, pandas dataframe containing the csv data from file
    output type: pandas dataframe
    '''

    df = pd.read_csv(path, header=0)

    return df


def plot_data(file_name, frame):
    '''
    Plot the data from the file
    
    input param: frame, pandas data frame containing all the data from csv file
    input type: pandas dataframe
    '''

    props = dict(boxstyle='round', facecoler='wheat', alpha=0.4)
    fig, ax = plt.subplots(2, sharex=True, figsize=(10,10))

    frame = frame.sort_values('Time', ascending=True)
    ax[0].plot(frame['Time'], frame['PA Current'], label='Purple Air', c='m')
    ax[0].plot(frame['Time'], frame['WIFI Current'], label='Wifi', c='b')
    ax[0].plot(frame['Time'], frame['RPi Current'], label='Raspberry Pi', c='r')
    ax[0].plot(frame['Time'], frame['Comms Current'], label='Communication', c='g')
    
    ax[0].set_ylim(0.0, 400)
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Current (mA)')
    ax[0].grid(True)
    ax[0].set_title('Remote PurpleAir Current and Power Diagnostics') #eventually have the code differentiate between different units    
    ax[0].legend(loc='upper left')
    ax[0].xaxis.set_major_locator(plt.MaxNLocator(5))

    ax[1].plot(frame['Time'], frame['PA Power'], label='Purple Air', c='m')
    ax[1].plot(frame['Time'], frame['WIFI Power'], label='WIFI', c='b')
    ax[1].plot(frame['Time'], frame['RPi Power'], label='Raspberry Pi', c='r')
    ax[1].plot(frame['Time'], frame['Comms Power'], label='Communcation', c='g')    
    
    ax[1].set_ylim(0.0, 5)
    ax[1].set_ylabel('Power (W)')
    ax[1].grid(True)
    ax[1].legend(loc='upper left')
    ax[1].xaxis.set_major_locator(plt.MaxNLocator(5))
    
    plt.xticks(rotation=45)
    plt.savefig(os.getcwd() + '/plots/cellular/' + file_name[:-4] + '.png', bbox_inches='tight', dpi=300)    


def plot_list(src_dir):
    '''
    Make a list of data files that still need to be plotted
    '''
    plot_dir = os.getcwd() + '/plots/cellular/'
    
    for x in range(0, 2): #try 2 times  
        try: 
            for f in os.listdir(src_dir):
                plot_file = f[:-4] + '.png'
                #print(f, plot_file)
                if plot_file not in os.listdir(plot_dir):
                    print(plot_file, os.listdir(plot_dir))
                    print("Plotting data from {} as {}".format(f, plot_file))
                    frame = reader(src_dir + f)
                    plot_data(f, frame)
                else:
                    print("All data files plotted.")
        except:
            print("Sleeping 60 seconds")
            time.sleep(60)


if __name__ == "__main__":
    src_directory = os.getcwd() + '/data/data_cellular/'
    print(src_directory)
    plot_list(src_directory)


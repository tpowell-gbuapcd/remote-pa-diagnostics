#!/usr/bin/env python3

# plots the 10 minute averages of the purpleair data over the course of one day

import time, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import argparse
from datetime import date, datetime, timedelta


def reader(file_path):
    '''
    Reads CSV as a pandas datafreame and returns it for plotting

    input param: file_path, the file containing the 10 minute averages of diagnostic data for one day. 
    input type: string
    
    output param: df, pandas dataframe containing the data from file.
    output type: pandas, dataframe
    '''

    df = pd.read_csv(file_path, header=0)
    
    return df


def get_file(directory):
    '''
    This may be unnecessary, but it returns the name of the csv file in the directory. At some point, it would be nice to group
    the raw data by date in the appropriate direcotry, rather than grouping them in the data directory.

    input param: directory, the path to the directory of yesterdays data
    input type: string

    output param: f, yesterdays csv file of the 10-minute average data for plotting
    output type: string
    '''

    for f in os.listdir(directory):
        if f.endswith('data.csv'):
            return f

    
def plot_data(frame, file_dir, plat, day):
    '''
    Plot the data from file

    input param: frame, pandas data frame containing all the data from the csv file
    input type: pandas dataframe

    input param: src_dir, the directory where the csv file is located and where the plot will also be saved 
    input type: string 

    input param: plat, platform we are plotting data for
    input type: string

    input param: day, the day we are plotting data for
    input type: string
    '''
    
    prop = dict(boxstyle='round', facecolor='wheat', alpha=0.4)
    fig, ax = plt.subplots(3, sharex=True, figsize=(10, 15))

    frame = frame.sort_values('Time', ascending=True)

    ax[0].plot(frame['Time'], frame['PA Current'], label='PurpleAir', c='m')
    ax[0].plot(frame['Time'], frame['WIFI Current'], label='WiFi', c='b')
    ax[0].plot(frame['Time'], frame['RPi Current'], label='Raspberry Pi', c='r')
    ax[0].plot(frame['Time'], frame['Comms Current'], label='Communication', c='g')
    ax[0].plot(frame['Time'], frame['Total Current'], label='Total Current', c='y')
    
    ax[0].set_ylim(0, 1000)
    ax[0].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Current (mA)')
    ax[0].grid(True)
    ax[0].set_title('Remote PurpleAir Current and Power Diagnositcs') #eventually have to code to differentiate between different units
    ax[0].legend(loc='upper left')
    ax[0].xaxis.set_major_locator(plt.LinearLocator(12))

    ax[1].plot(frame['Time'], frame['PA Power'], label='PurpleAir', c='m')
    ax[1].plot(frame['Time'], frame['WIFI Power'], label='WiFi', c='b')
    ax[1].plot(frame['Time'], frame['RPi Power'], label='Raspberry Pi', c='r')
    ax[1].plot(frame['Time'], frame['Comms Power'], label='Communication', c='g')
    ax[1].plot(frame['Time'], frame['Total Power'], label='Total Current', c='y')

    ax[1].set_ylim(0, 15)
    ax[1].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
    ax[1].set_ylabel('Power (W)')
    ax[1].grid(True)
    ax[1].legend(loc='upper left')
    ax[1].xaxis.set_major_locator(plt.LinearLocator(12))

    ax[2].plot(frame['Time'], frame['PA Voltage'], label='PurpleAir', c='m')
    ax[2].plot(frame['Time'], frame['WIFI Voltage'], label='WiFi', c='b')
    ax[2].plot(frame['Time'], frame['RPi Voltage'], label='Raspberry Pi', c='r')
    ax[2].plot(frame['Time'], frame['Comms Voltage'], label='Communication', c='g')

    ax[2].set_ylim(0, 16)
    ax[2].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
    ax[2].set_ylabel('Voltage (V)')
    ax[2].grid(True)
    ax[2].legend(loc='upper left')
    ax[2].xaxis.set_major_locator(plt.LinearLocator(12))

    plt.xticks(rotation=35)
    plot_name = file_dir + plat + '_' + day + '.png'
    print(plot_name)
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(plot_name, dpi=300)
    plt.close()

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--platform', type=str, help='PLatform name of the unit to run the diagnostic code on e.g. GBUAPCDPI1')
    parser.add_argument('-d', '--date', type=str, help="Date that you would like to generate plots for. e.g. 08-05-2021", default=None)
    args = parser.parse_args()
    src_directory = os.getcwd() + '/data/' + args.platform + '/'

    # this code will run on the crontab everyday at 1:00AM for the PREVIOUS days worth of data. Because my rsync and crontab
    # aren't well synced, sometimes the files aren't complete until after 12:15ish. This can be corrected in the future
    if args.date == None:
        yesterday = (date.today() - timedelta(days=1)).strftime('%m-%d-%Y')
    else:
        yesterday = args.date

    print(yesterday)

    file_directory = src_directory + yesterday + '/'

    print(file_directory)
    
    csv_file = get_file(file_directory)
    csv_path = file_directory + csv_file

    print(csv_file, csv_path)

    pd_data = reader(csv_path)
    print(pd_data['Time'].iloc[0], pd_data['Time'].iloc[-1])

    plot_data(pd_data, file_directory, args.platform, yesterday)

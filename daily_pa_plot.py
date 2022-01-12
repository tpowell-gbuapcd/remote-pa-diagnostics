#!/usr/bin/env python3

# list of functions needed to plot the data from the remote purpleair
# currently building this script with functions to work with the newly acquired gas sensors that
# will be integrated into both units. The current script on the raspberry pi is smarter and should
# recognize what sensors are connected and what are not.

import time, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import argparse
import logging

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


def get_file(date, plat):
    '''
    Returns the name of the CSV file of 10-minute averages.    

    input param: date, the date of data we want to plot
    input type: string
        
    input param: plat, the platform where the data we want to plot are from
    input type: string
    
    output param: file_name, yesterdays csv file of the 10-minute average data for plotting
    output type: string
    '''
    
    return plat + date[0:2] + date[3:5] + date [6:10] + '.csv' 
  

def get_date(arg):
    '''
    Return the date of the file that we're plotting/making the text file for. If no argument is given, then the 
    date we want is the current day. If an argument is given, then we simply return the argument.

    input param: arg, the date that is passed as an argument to the script running in the crontab
    input type: string
    '''  

    if arg == None:
        return_date = date.today().strftime('%m-%d-%Y') 
    else:
        return_date = arg

    return return_date 
    

def set_directory(directory, date, plat):
    '''
    Set the save directory of plot and text/csv files. Directories are broken up by day.

    input param: directory, the path to the directory of data.
    input type: string

    input param: date, the date of data we want to plot
    input type: string

    input param: plat, the platform where the data we want to plot are from

    return param: day_dir, directory for plots with name of the format dd-mm-yyy.
    '''
    
    print(directory, date, plat)
    day_dir = directory + date + '/'
    
    if not os.path.exists(day_dir):
        os.makedirs(day_dir)
    
    #logging.info('Average Data Text Files Saved to {}'.format(avg_day_dir))
    #logging.info('Plots Saved to {}'.format(plot_day_dir))

    return day_dir


def make_text(file_name, save_directory, frame):
    '''
    Create a more easily readable text file of the data from the raspberry pi. Also calculate the total 
    current and power draw of the device. 

    input param: file_name, the csv file name with data we want to parse into a more easily read text file. 
    input type: string

    input param: save_directory, where the more easily readable text file will be saved
    input type: string

    input param: frame, the pandas dataframe containing our data
    input type: pandas dataframe
    '''
    text_file = file_name[:-4] + '.txt'

    header = ''

    try:
        # since the file is so small (~80kB at most) just rewrite the whole file each time a new line 
        # appears in the csv
        # this isn't the best way to do this, could probably append new lines to the end of the file
        with open(save_directory+text_file, 'w') as txt:
            for val in list(frame.columns):

                if val == 'Time':
                    header += '{:<25}'.format(val)
                else:
                    header += '{:<20}'.format(val)

            header += '{:<20}{:<20}'.format('Total Current', 'Total Power')
            txt.write(header+'\n')

            for index, row in frame.iterrows():

                str_vals = ''
                current_tot = 0
                power_tot = 0

                for val, ind in zip(row.values, row.index):

                    #Calculate total power and current draw
                    if 'Current' in ind:
                        current_tot += val
                    if 'Power' in ind:
                        power_tot += val

                    # if the value is the date, the format is different
                    if type(val) is str:
                        str_vals += '{:<25}'.format(val)
                    else:
                        str_vals += '{:<20.2f}'.format(val)

                str_vals += '{:<20.2f}{:<20.2f}\n'.format(current_tot, power_tot)
                txt.write(str_vals)
            txt.close()

    except Exception as e:
        print(e)
        logging.error('Error Encountered: {}'.format(e), exc_info=True)


def get_number_of_subplots(cols):
    '''
    Calculate the number of subplots based on the keys of the dataframe. There may be a better way to do this
    that doesn't depend on hardcoding the values. At the very least, maybe have a separate text file that 
    contains the expected keys and then use that to iterate through the expected values

    input param: cols, a list of all of the keys of the pandas dataframe
    input type: list

    ouput param: plot_count, the number of subplots needed to display the data
    output type: integer
    '''
    
    plot_count = 0
    counted_list = []
    
    try:    
        for val in cols:
            print(val)
            if 'PM' in val:
                if 'PM' not in counted_list:
                    counted_list.append('PM')
                    plot_count += 1
            if 'Temp' or 'RH' in val:
                if 'Temp' not in counted_list:
                    counted_list.append('Temp')
                    plot_count += 1
                if 'RH' not in counted_list:
                    counted_list.append('RH')
            if 'Current' in val:
                if 'Current' not in counted_list:
                    counted_list.append('Current')
                    plot_count += 1
            if 'Voltage' in val:
                if 'Voltage' not in counted_list:
                    counted_list.append('Voltage')
                    plot_count += 1
            if 'Power' in val:
                if 'Power' not in counted_list:
                    counted_list.append('Power')
                    plot_count += 1
            if 'Pressure' in val:
                if 'Pressure' not in counted_list:
                    counted_list.append('Pressure')
                    plot_count += 1
            if 'Gas' or 'CO2' in val:
                if 'Gas' not in counted_list:
                    counted_list.append('Gas')
                    plot_count += 1
                if 'CO2' not in counted_list:
                    counted_list.append('CO2')
    
    except Exception as e:
        print(e)
        logging.error('Error Encounted: {}'.format(e), exc_info=True)

    return plot_count  


def plot_data(frame, save_directory, plat, file_name, date):
    '''
    Plot the data from file

    input param: frame, pandas data frame containing all the data from the csv file
    input type: pandas dataframe

    input param: save_directory, the directory where the plot will be saved
    input type: string 

    input param: plat, platform we are plotting data for
    input type: string

    input param: file_name, the name of the csv file we're plotting from. Will share names but be different type
    input type: string
    
    input param: date
    input type: string
    '''
    
    number_of_plots = get_number_of_subplots(list(frame.columns))
    plot_file = file_name[:-4] + '.png'
    lg_size = 6
    
    fig, ax = plt.subplots(number_of_plots, sharex=True, figsize=(10, 15))
    ax3_share = ax[3].twinx()
    ax6_share = ax[6].twinx()

    '''
    #prints the key needed to access the data in the frame, and the data
    for val in list(frame.columns):
        print(val, frame[val])
    '''

    # these are used to make sure colors aren't duplicated in the temperature and RH plots
    hot_colors = ['r', '#F97306', 'm', '#FFFF14']
    cold_colors = ['b', 'g', 'c']
    h_i = 0
    c_i = 0

    # used for correctly applying handles in temp and rh plots
    temp_rh_handles = []    
    gas_handles = []

    # make sure the frames are in ascending order according to Time
    # this can be hard coded since we will alwasy have a Time frame and it will always be called Time
    frame = frame.sort_values('Time', ascending=True)
    try:
        for val in list(frame.columns):
            if 'Current' in val:
                ax[0].plot(frame['Time'], frame[val], label=val)
            if 'Power' in val:
                ax[1].plot(frame['Time'], frame[val], label=val)
            if 'Voltage' in val:
                ax[2].plot(frame['Time'], frame[val], label=val)  
            if 'Temp' or 'RH' in val:
                if 'Temp' in val: 
                    lg, = ax[3].plot(frame['Time'], frame[val], label=val, c=hot_colors[h_i])
                    temp_rh_handles.append(lg)
                    h_i += 1
                if 'RH' in val:
                    lg, = ax3_share.plot(frame['Time'], frame[val], label=val, c=cold_colors[c_i])
                    temp_rh_handles.append(lg)
                    c_i += 1
            if 'Pressure' in val:
                ax[4].plot(frame['Time'], frame[val], label=val)
            if 'PM' in val:
                ax[5].plot(frame['Time'], frame[val], label=val)
            if 'Gas' or 'CO2' in val:
                if 'Gas' in val:
                    lg, = ax[6].plot(frame['Time'], frame[val], label=val, c='r')
                    gas_handles.append(lg)
                if 'CO2' in val:
                    lg, = ax6_share.plot(frame['Time'], frame[val], label=val, c='b')
                    gas_handles.append(lg)
                   

        ax[0].set_ylim(0,500)
        ax[0].set_ylabel('Current (mA)')
        ax[0].grid(True)
        ax[0].legend(loc='upper left', prop={'size':lg_size})
        ax[0].xaxis.set_major_locator(plt.LinearLocator(12))

        ax[1].set_ylim(0, 15)
        ax[1].set_ylabel('Power (W)')
        ax[1].grid(True)
        ax[1].legend(loc='upper left', prop={'size':lg_size})
        ax[0].xaxis.set_major_locator(plt.LinearLocator(12))

        ax[2].set_ylim(0, 16)
        ax[2].set_ylabel('Voltage (V)')
        ax[2].grid(True)
        ax[2].legend(loc='upper left', prop={'size':lg_size})
        ax[2].xaxis.set_major_locator(plt.LinearLocator(12))

        ax[4].set_ylim(0, 1000)
        ax[4].set_ylabel('Pressure (hPa)')
        ax[4].grid(True)
        ax[4].legend(loc='upper left', prop={'size':lg_size})
        ax[4].xaxis.set_major_locator(plt.LinearLocator(12))
        
        ax[5].set_ylim(bottom=0)
        ax[5].set_ylabel('PM Conc (ug/m3)')
        ax[5].grid(True)
        ax[5].legend(loc='upper left', prop={'size':lg_size})
        ax[5].xaxis.set_major_locator(plt.LinearLocator(12))

        ax[3].set_ylim(-20, 80)
        ax[6].set_ylim(bottom=0)
        ax3_share.set_ylim(0, 100)
        ax6_share.set_ylim(bottom=0)

        ax[3].set_ylabel('Temp (C)')
        ax[6].set_ylabel('BME Gas (ohms)')
        ax3_share.set_ylabel('RH (%)')
        ax6_share.set_ylabel('CO2 CONC (PPM)')
        
        ax[3].grid(True)
        ax[6].grid(True)
        ax[3].legend(handles=temp_rh_handles, loc='upper right', prop={'size':lg_size})
        ax[6].legend(handles=gas_handles, loc='upper right', prop={'size':lg_size})
        
        ax[6].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
        ax[6].xaxis.set_major_locator(plt.LinearLocator(12))

        plt.xticks(rotation=35)
        plot_name = save_directory + plot_file
        print(plot_name)
        fig.suptitle(plat + "Data From " + date)
        plt.gcf().autofmt_xdate()
        #plt.set_loglevel('ERROR')
        plt.tight_layout()
        plt.savefig(plot_name, dpi=300)
        plt.close()

    except Exception as e:
        print(e)
        logging.error('Error Encountered: {}'.format(e), exc_info=True)



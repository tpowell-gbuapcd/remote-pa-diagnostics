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
    
    input param: path, the file that has been rsynced from the raspberry pi to the linux box and discovered by the watchdog
    input type: string

    output param: df, pandas dataframe containing the csv data from file
    output type: pandas dataframe
    '''

    df = pd.read_csv(path, header=0)

    return df


def set_directory(file_name):
    '''
    Set the save directory of plot and text/csv files. Directories are broken up by day.
    
    input param: file_name, the input csv file of diagnostic data from the raspberry pi.
    input type: string

    return param: avg_day_dir, directory for average csv files with name of the format dd-mm-yyyy. 
    return param: plot_day_dir, directory for plots with name of the format dd-mm-yyy.
    '''

    dd = file_name[11:13]
    mm = file_name[9:11]
    yy = file_name[13:17]
    
    print('function', file_name)
    print('function', dd, mm, yy)
    
    # data_cellular will need to be changed for satellite
    avg_day_dir = '{}/data/data_cellular/{}-{}-{}/'.format(os.getcwd(), dd, mm, yy)
    plot_day_dir = '{}/plots/cellular/{}-{}-{}/'.format(os.getcwd(), dd, mm, yy)
    
    print('function', avg_day_dir)
    print('function', plot_day_dir)

    if not os.path.exists(avg_day_dir):
        os.makedirs(avg_day_dir)

    if not os.path.exists(plot_day_dir):
        os.makedirs(plot_day_dir)

    return avg_day_dir, plot_day_dir
        

def plot_data(file_name, frame, p_dir):
    '''
    Plot the data from the file
    
    input param: frame, pandas data frame containing all the data from csv file
    input type: pandas dataframe
    '''

    prop = dict(boxstyle='round', facecolor='wheat', alpha=0.4)
    fig, ax = plt.subplots(2, sharex=True, figsize=(10,10))
    frame = frame.sort_values('Time', ascending=True)


    avg_pa_current = frame['PA Current'].mean(axis=0)
    avg_wifi_current = frame['WIFI Current'].mean(axis=0)
    avg_rpi_current = frame['RPi Current'].mean(axis=0)
    avg_comms_current = frame['Comms Current'].mean(axis=0)

    total_current = frame['PA Current'] + frame['WIFI Current'] + frame['RPi Current'] + frame['Comms Current']
    avg_total_current = total_current.mean(axis=0)    
 
    avg_pa_power = frame['PA Power'].mean(axis=0)
    avg_wifi_power = frame['WIFI Power'].mean(axis=0)
    avg_rpi_power = frame['RPi Power'].mean(axis=0)
    avg_comms_power = frame['Comms Power'].mean(axis=0)
    
    total_power = frame['PA Power'] + frame['WIFI Power'] + frame['RPi Power'] + frame['Comms Power']
    avg_total_power = total_power.mean(axis=0)    

    ax[0].plot(frame['Time'], frame['PA Current'], label='Purple Air', c='m')
    ax[0].plot(frame['Time'], frame['WIFI Current'], label='Wifi', c='b')
    ax[0].plot(frame['Time'], frame['RPi Current'], label='Raspberry Pi', c='r')
    ax[0].plot(frame['Time'], frame['Comms Current'], label='Communication', c='g')
    ax[0].plot(frame['Time'], total_current, label='Total Current', c='y')
    
    ax[0].set_ylim(0.0, 1000)
    ax[0].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Current (mA)')
    ax[0].grid(True)
    ax[0].set_title('Remote PurpleAir Current and Power Diagnostics') #eventually have the code differentiate between different units    
    ax[0].legend(loc='upper left')
    ax[0].xaxis.set_major_locator(plt.MaxNLocator(10))
    ax[0].text(0.75, 0.74, 'Avg PA: {:.2f}mA\nAvg WiFi: {:.2f}ma\nAvg RPi: {:.2f}mA\nAvg Comms: {:.2f}mA\nAvg Total: {:.2f}mA'.format(avg_pa_current, avg_wifi_current, avg_rpi_current, avg_comms_current, avg_total_current),
                transform=ax[0].transAxes, bbox=prop)

    ax[1].plot(frame['Time'], frame['PA Power'], label='Purple Air', c='m')
    ax[1].plot(frame['Time'], frame['WIFI Power'], label='Wifi', c='b')
    ax[1].plot(frame['Time'], frame['RPi Power'], label='Raspberry Pi', c='r')
    ax[1].plot(frame['Time'], frame['Comms Power'], label='Communication', c='g')
    ax[1].plot(frame['Time'], total_power, label='Total Power', c='y')
    
    ax[1].set_ylim(0.0, 12)
    ax[1].set_xlim(frame['Time'].iloc[0], frame['Time'].iloc[-1])
    ax[1].set_ylabel('Power (W)')
    ax[1].grid(True)
    ax[1].legend(loc='upper left')
    ax[1].xaxis.set_major_locator(plt.MaxNLocator(10))
    ax[1].text(0.75, 0.75, 'Avg PA: {:.2f}W\nAvg WiFi: {:.2f}W\nAvg RPi: {:.2f}W\nAvg Comms: {:.2f}W\nAvg Total: {:.2f}W'.format(avg_pa_power, avg_wifi_power, avg_rpi_power, avg_comms_power, avg_total_power),
                transform=ax[1].transAxes, bbox=prop)

    plt.xticks(rotation=45)
    plt.savefig(p_dir + file_name[:-4] + '.png', bbox_inches='tight', dpi=300)    
    plt.close()


def write_averages(file_dir, frame):
    '''
    Write the ten minute averages of the csv data to a a csv and a human readable text file. Can be used later 
    for plotting or further data analysis. 

    input param: frame, the dataframe of the csv file. 
    input type: pandas dataframe
    '''

    avg_pa_current = frame['PA Current'].mean(axis=0)
    avg_wifi_current = frame['WIFI Current'].mean(axis=0)
    avg_rpi_current = frame['RPi Current'].mean(axis=0)
    avg_comms_current = frame['Comms Current'].mean(axis=0)

    avg_pa_power = frame['PA Power'].mean(axis=0)
    avg_wifi_power = frame['WIFI Power'].mean(axis=0)
    avg_rpi_power = frame['RPi Power'].mean(axis=0)
    avg_comms_power = frame['Comms Power'].mean(axis=0)

    avg_pa_voltage = frame['PA Voltage'].mean(axis=0)
    avg_wifi_voltage = frame['WIFI Voltage'].mean(axis=0)
    avg_rpi_voltage = frame['RPi Voltage'].mean(axis=0)
    avg_comms_voltage = frame['Comms Voltage'].mean(axis=0)

    total_current = frame['PA Current'] + frame['WIFI Current'] + frame['RPi Current'] + frame['Comms Current']
    total_power = frame['PA Power'] + frame['WIFI Power'] + frame['RPi Power'] + frame['Comms Power']
    avg_total_current = total_current.mean(axis=0)
    avg_total_power = total_power.mean(axis=0)

    header_vals = ['Time', 'PA Current', 'WIFI Current', 'RPi Current', 'Comms Current', 'PA Power', 'WIFI Power', 'RPi Power', 'Comms Power', 'PA Voltage', 'WIFI Voltage', 'RPi Voltage', 'Comms Voltage', 'Total Current', 'Total Power']
    row = [datetime.now().strftime('%m/%d/%Y %H:%M:%S'), avg_pa_current, avg_wifi_current, avg_rpi_current, avg_comms_current, avg_pa_power, avg_wifi_power, avg_rpi_power, avg_comms_power, 
            avg_pa_voltage, avg_wifi_voltage, avg_rpi_voltage, avg_comms_voltage, avg_total_current, avg_total_power]

    csv_file = 'cellular_average_data.csv'
    txt_file = 'cellular_average_data.txt'

    try:
        if csv_file not in os.listdir(file_dir):
            # if the file does not exist, create it and write the header row for and the first row
            with open(file_dir+csv_file, 'w') as f:
                #print('Writing CSV header')
                file_writer = csv.writer(f, delimiter=',')
                file_writer.writerow(header_vals)
                file_writer.writerow(row)
                f.close()
            with open(file_dir+txt_file, 'w') as txt:
                #print('Writing Text Header')
                txt.write('{:<25}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}{:<15}\n'.format('Time', 'PA Current', 'WIFI Current', 'RPi Current', 'Comms Current',
                            'PA Power', 'WIFI Power', 'RPi Power', 'Comms Power', 'PA Voltage', 'WIFI Voltage', 'RPi Voltage', 'Comms Voltage', 'Total Current', 'Total Power'))
                txt.write('{:<25}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}\n'.format(datetime.now().strftime('%m/%d/%Y %H:%M:%S'), 
                            avg_pa_current, avg_wifi_current, avg_rpi_current, avg_comms_current, avg_pa_power, avg_wifi_power, avg_rpi_power, avg_comms_power, avg_pa_voltage, avg_wifi_voltage, avg_rpi_voltage, avg_comms_voltage,
                                avg_total_current, avg_total_power))

                txt.close()
        else:
            with open(file_dir+csv_file, 'a') as f:
                #print('Appending to CSV')
                file_writer = csv.writer(f, delimiter=',')
                file_writer.writerow(row)
                f.close()
            with open(file_dir+txt_file, 'a') as txt:
                #print('Appending to Text')
                txt.write('{:<25}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}{:<15.2f}\n'.format(datetime.now().strftime('%m/%d/%Y %H:%M:%S'), 
                            avg_pa_current, avg_wifi_current, avg_rpi_current, avg_comms_current, avg_pa_power, avg_wifi_power, avg_rpi_power, avg_comms_power, avg_pa_voltage, avg_wifi_voltage, avg_rpi_voltage, avg_comms_voltage,
                                avg_total_current, avg_total_power))
                txt.close()
    except Exception as e:
        print('Womp womp')
        print(e)
    

def create_diagnostics(src_dir):
    '''
    Check to see what csv files already have been plotted, make plots if they haven't. 
    Append average values to a csv. Sometimes the rsync starts before data have been fully
    inserted into file, which gives us incomplete data and an error. If this happens, we wait
    5 minutes at (twice at most) to give the program time to completely fill the csv with data. 
    
    input param: src_dir, source directory of csv files
    input type: string
    '''

    #plot_dir = os.getcwd() + '/plots/cellular/'
    #avg_file_dir = os.getcwd() + '/data/'    

    for x in range(0, 2): #try 2 times  
        try: 
            for f in os.listdir(src_dir):
                
                path = os.path.join(src_dir, f)
                print(path)
                if os.path.isdir(path):
                    continue
             
                plot_file = f[:-4] + '.png'
                avg_dir, plot_dir = set_directory(f)
                #print('Test', f, plot_file)
                #print('Test', avg_dir, plot_dir)

                if plot_file not in os.listdir(plot_dir):
                    
                    #print(plot_file, os.listdir(plot_dir))
                    csv_file = src_dir + f
                    #set_directory(f)

                    while os.path.getsize(csv_file) < 2000:
                        print('File not big enough, waiting....')
                        time.sleep(1)

                    print("Plotting data from {} as {}".format(f, plot_file))
                    pd_frame = reader(csv_file)
                    #print(len(pd_frame['Time']))

                    while len(pd_frame['Time']) != 600: #600 is the number of datapoints we get from a ten minute file
                        time.sleep(1)
                        print(f, len(pd_frame['Time']))
                        pd_frame = reader(src_dir + f)
                    
                    plot_data(f, pd_frame, plot_dir)
                    write_averages(avg_dir, pd_frame)
                
                else:
                    print("All data files plotted.")
        except Exception as e:
            print(e)
            #print("Sleeping 60 seconds")
            #time.sleep(60)


if __name__ == "__main__":
    src_directory = os.getcwd() + '/data/data_cellular/'
    print(src_directory)
    create_diagnostics(src_directory)


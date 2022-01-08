#!/usr/bin/env python3

import os
import argparse
import daily_pa_plot as pa

parser = argparse.ArgumentParser()

parser.add_argument('-p', '--platform', type=str, help='Platform name of the unit to run the diagnostic code on e.g. GBUAPCDPI1')
parser.add_argument('-d', '--date', type=str, help='Date that you would like to generate plots for e.g. 08-05-2021', default=None)

args = parser.parse_args()
src_directory = os.getcwd() + '/data/' + args.platform + '/'

date = pa.get_date(args.date)
file_name = pa.get_file(date, args.platform)
file_path = src_directory + file_name
file_directory = pa.set_directory(src_directory, date, args.platform)

pa_frame = pa.reader(file_path)
pa.make_text(file_name, file_directory, pa_frame)
pa.plot_data(pa_frame, file_directory, args.platform, file_name, date)

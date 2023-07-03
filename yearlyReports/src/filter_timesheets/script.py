import os
import pandas as pd

# VIASH START
par = {
    'input': 'data.csv',
    'year': 0000,
    'min_duration_per_project': 0,
    'output': '../../results/filtered_data.csv'
}
# VIASH END

# Input data
data = pd.read_csv("C:/Users/nirmayi/Downloads/task_description/data.csv", parse_dates=['time_start', 'time_end'])
# data = pd.read_csv(par['input'], parse_dates=['time_start', 'time_end'])
year = 2010  # par['year']
duration = 150  # par['min_duration_per_project']

# Filter by year
year_filtered = data[pd.DatetimeIndex(data['time_end']).year == year]

# Total time for each project
project_times = year_filtered.groupby('project', as_index=False)['duration'].sum()
projects_above_threshold = project_times['project'][project_times['duration'] > duration]

# Filter by project duration
time_filtered = year_filtered[year_filtered['project'].isin(projects_above_threshold)]

# Create results directory
if not os.path.exists("../../results"):
    os.makedirs("../../results")

# Filtered data
time_filtered.to_csv(par['output'], index=False)

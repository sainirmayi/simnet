import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

# VIASH START
par = {
    'input': '../../results/filtered_data.csv',
    'output': '../../results/report.pdf'
}
# VIASH END

# Create results directory
if not os.path.exists("../../results"):
    os.makedirs("../../results")

# Input data
filtered_data = pd.read_csv(par['input'], parse_dates=['time_start', 'time_end'])
filtered_data['year_month'] = filtered_data['time_end'].apply(lambda x: x.strftime('%Y-%m'))
filtered_data.rename(columns={"person": "Person", "year_month": "Month", "duration": "Time", 'project': 'Project'}, inplace=True)

# Times per project per person
tpp = filtered_data.groupby(['Project', 'Person'], as_index=False)['Time'].sum()
num_people = len(tpp['Person'].unique())
num_projects = len(tpp['Project'].unique())

# Times per project
tp = filtered_data.groupby('Project', as_index=False)['Time'].sum()
total_time = tp['Time'].sum()

# Times per person per month
tpm = filtered_data.groupby(['Person', 'Month'], as_index=False)['Time'].sum()
tpm = pd.pivot_table(data=tpm, index=['Month'], columns=['Person'], values='Time')
# Plot
tpm.plot.bar(stacked=True, rot=30, ylabel='Time (h)', colormap='Set1', figsize=(9, 5))
plt.legend(loc='upper center', ncol=num_people, bbox_to_anchor=(0.5, -0.2), fontsize=8)
plt.savefig("../../results/figure.png", bbox_inches='tight', pad_inches=0)

# Text for report
year = filtered_data['time_end'].apply(lambda x: x.strftime('%Y'))[0]
title = f"Project report anno {year}"
tab1_desc = f"This year, {num_people} people worked on {num_projects} different projects."
tab1_title = f"Time per project and person (rounded down):"
tab2_desc = f"In total, {total_time} hours was worked across all projects."
tab2_title = f"Time per project (rounded down):"
fig_desc = f"Time per person per month:"

# Report
pdf = FPDF()
pdf.add_page()

pdf.set_font('Times', '', 16)
pdf.cell(0, 15, title, border=0, align='C', ln=1)
pdf.ln(3)

pdf.set_font('Times', '', 12)
pdf.cell(0, 10, tab1_desc, border=0, align='L', ln=1)
pdf.ln(3)
pdf.set_font('Times', '', 10)
pdf.cell(0, 5, tab1_title, border=0, align='C', ln=1)
pdf.cell(60, 5, 'Person', border='TB', align='L', ln=0)
pdf.cell(60, 5, 'Project', border='TB', align='L', ln=0)
pdf.cell(60, 5, 'Time (h)', border='TB', align='R', ln=1)
for i in range(0, len(tpp)):
    frame = 'B' if i == len(tpp) else 0
    pdf.cell(60, 5, f"{tpp['Person'].iloc[i]}", border=frame, align='L', ln=0)
    pdf.cell(60, 5, f"{tpp['Project'].iloc[i]}", border=frame, align='L', ln=0)
    pdf.cell(60, 5, f"{tpp['Time'].iloc[i]}", border=frame, align='R', ln=1)
pdf.ln(3)

pdf.set_font('Times', '', 12)
pdf.cell(0, 10, tab2_desc, border=0, align='L', ln=1)
pdf.ln(3)
pdf.set_font('Times', '', 10)
pdf.cell(0, 5, tab2_title, border=0, align='C', ln=1)
pdf.cell(80, 5, 'Project', border='TB', align='L', ln=0)
pdf.cell(80, 5, 'Time (h)', border='TB', align='R', ln=1)
for i in range(0, len(tp)):
    pdf.cell(80, 5, f"{tp['Project'].iloc[i]}", border=0, align='L', ln=0)
    pdf.cell(80, 5, f"{tp['Time'].iloc[i]}", border=0, align='R', ln=1)
pdf.cell(80, 5, "Total", border='B', align='L', ln=0)
pdf.cell(80, 5, f"{total_time}", border='B', align='R', ln=1)
pdf.ln(3)
pdf.cell(0, 5, fig_desc, border=0, align='C', ln=1)
pdf.ln(3)
pdf.image("../../results/figure.png", x=30, w=150, type='PNG')
pdf.output(par['output'])



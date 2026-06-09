import pandas as pd
from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa
import os

# Configuration
TARGET_COLUMN = "logfoldchanges" 

def get_color_style(value, col_name):
    if col_name != TARGET_COLUMN:
        return "color: black;"
    try:
        val = float(value)
        if val < -1: return "color: red; font-weight: bold;"
        if val > 1: return "color: blue; font-weight: bold;"
        return "color: black;"
    except (ValueError, TypeError):
        return "color: black;"

# Load Data
data_frames = {}
all_columns = []

for m in range(1, 7): # Adjust range as needed
    filename = f"markers/markers_filtered_{m}month_SRCIN1_annot_level_3_rev2.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        if not df.empty:
            data_frames[m] = df.to_dict(orient="records")
            all_columns = df.columns.tolist()
    else:
        print(f"WARNING: File not found -> {filename}") 

# Setup Template
env = Environment(loader=FileSystemLoader('.'))
env.globals.update(get_color_style=get_color_style)
template = env.get_template('report_template.html')

html_out = template.render(
    data_frames=data_frames,
    columns=all_columns
)

# Generate PDF
output_filename = "Organoidi24_Report_level_3_rev2.pdf"
with open(output_filename, "wb") as result_file:
    # Adding 'link_callback' or 'path' ensures images are found
    pisa_status = pisa.CreatePDF(html_out, dest=result_file, path=os.getcwd())

if not pisa_status.err:
    print(f"Done! Created {output_filename}")
else:
    print(f"Error: {pisa_status.err}")
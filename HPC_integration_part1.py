#!/usr/bin/env python3
# HPC_integration_part1.py

# ========== 1) HPC environment, Kaggle
# Note: We'll install these packages via shell command first
# !pip install pandas==1.4.0 requests==2.27.1 geopandas==0.10.2 shapely==1.8.1 PyYAML==6.0 kaggle==1.5.12

import os
import json
import yaml
import requests
import pandas as pd

# Kaggle JSON
kaggle_creds = {
  "username": "spencerkarns",
  "key": "78834d1b3e87034c2333ced3252649d1"
}
os.makedirs(os.path.expanduser("~/.kaggle"), exist_ok=True)
with open(os.path.expanduser("~/.kaggle/kaggle.json"), "w") as f:
   json.dump(kaggle_creds, f)

# Set proper permissions for Kaggle credentials
os.system("chmod 600 ~/.kaggle/kaggle.json")

# Create folder structure
os.system("mkdir -p data config notebooks scripts")

# ========== 2) HPC cost references
cost_yaml = """
hpc_tiers:
 - name: HPC_350KW
   capex: 300000
   cable_cooling: 25000
 - name: HPC_1000KW
   capex: 500000
   cable_cooling: 40000

electricity_rate: 0.15
staff_cost_monthly: 1200
maintenance_percent: 0.05
hpc_fee_per_kwh: 0.40
"""

with open("config/hpc_cost_params.yaml", "w") as f:
   f.write(cost_yaml)

with open("config/hpc_cost_params.yaml", "r") as f:
   cost_data = yaml.safe_load(f)
print("Loaded HPC cost config:\n", cost_data)

# ========== 3) Kaggle HPC data (3 sets)
datasets = [
  ("valakhorasani/electric-vehicle-charging-patterns", "ev_charging_patterns.csv"),
  ("michaelbryantds/electric-vehicle-charging-dataset", "station_data_dataverse.csv"),
  ("venkatsairo4899/ev-charging-station-usage-of-california-city", "EVChargingStationUsage.csv")
]

for dset, csvfile in datasets:
   print(f"Downloading {dset} from Kaggle ...")
   exit_code = os.system(f"kaggle datasets download -d {dset} -p data/ --unzip")
   if exit_code != 0:
       print(f"Kaggle CLI fail for {dset}; HPC data essential => stopping. Please check dataset acceptance or environment.")
       break

   path = f"data/{csvfile}"
   if not os.path.exists(path):
       print(f"File {path} not found after unzipping => stopping HPC ingestion.")
       break

   try:
      df = pd.read_csv(path)
      # Get row count and determine sample size (use entire dataset if less than 1000 rows)
      row_count = len(df)
      sample_size = min(1000, row_count)
      df_samp = df.sample(n=sample_size, random_state=42)
      sample_file = path.replace(".csv","_sample.csv")
      df_samp.to_csv(sample_file, index=False)
      print(f"Sample created: {sample_file} with {sample_size} rows from {row_count} total rows")
   except Exception as e:
      print(f"Could not read HPC CSV {path}, halting HPC data ingestion. Error: {e}")
      break

# ========== 4) Attempt TomTom O/D Analysis
tomtom_key = "rzn7XSV2ZQ6DLZ1goeM7VumkW2C1ZsvU"
od_base = "https://api.tomtom.com/trafficstats/1/odMatrix"
params = {
  "key": tomtom_key,
  # Possibly referencing the user's project or bounding polygons
}

print("Attempting TomTom O/D Analysis. If it fails, we comment out this block for future tests.")
try:
    resp = requests.get(od_base, params=params)
    if resp.status_code == 200:
        with open("data/tomtom_od.json", "wb") as f:
           f.write(resp.content)
        data_od = json.loads(resp.content)
        print("TomTom O/D snippet:", data_od)
    else:
       code = resp.status_code
       print(f"TomTom O/D call failed with status code {code}. We'll comment out this code block in subsequent runs.")
       print("Manus continues HPC pipeline but won't do O/D calls until you finalize or fix login/trial.")
       # Instead of halting, we skip or set a variable "tomtom_od_enabled = False"
       # (We do not stop the entire HPC build.)
except Exception as e:
    print(f"TomTom O/D call failed with exception: {e}. We'll comment out this code block in subsequent runs.")
    print("Manus continues HPC pipeline but won't do O/D calls until you finalize or fix login/trial.")

print("\nDocument 1 (Part 1) completed successfully.")
print("Environment setup, Kaggle API configuration, folder structure, HPC cost references, and dataset downloads are complete.")
print("TomTom O/D Analysis was attempted (success depends on API access).")
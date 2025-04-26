import json

# Load the notebook
with open('HPC Dashboard Collab (1).ipynb', 'r') as f:
    notebook = json.load(f)

# Find the cell with the dashboard code
code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
for cell in code_cells:
    source = ''.join(cell['source'])
    if '%%writefile hpc_dashboard.py' in source:
        dashboard_code = source.replace('%%writefile hpc_dashboard.py', '').strip()
        # Write to file
        with open('hpc_dashboard.py', 'w') as f:
            f.write(dashboard_code)
        print('Created hpc_dashboard.py')
        break 
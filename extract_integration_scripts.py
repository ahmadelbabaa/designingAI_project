import json
import re

# Load the notebook
with open('HPC Dashboard Collab (1).ipynb', 'r') as f:
    notebook = json.load(f)

# Find cells with integration scripts
code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']

# Extract the script parts
for i, cell in enumerate(code_cells):
    source = ''.join(cell['source'])
    
    # Check for HPC_integration_part1.py
    if "#!/usr/bin/env python3" in source and "# HPC_integration_part1.py" in source:
        with open('HPC_integration_part1.py', 'w') as f:
            f.write(source)
        print('Created HPC_integration_part1.py')
    
    # Check for HPC_integration_part2.py
    elif "#!/usr/bin/env python3" in source and "# HPC_integration_part2.py" in source:
        with open('HPC_integration_part2.py', 'w') as f:
            f.write(source)
        print('Created HPC_integration_part2.py')
    
    # Check for HPC_integration_part3.py
    elif "#!/usr/bin/env python3" in source and "# HPC_integration_part3.py" in source:
        with open('HPC_integration_part3.py', 'w') as f:
            f.write(source)
        print('Created HPC_integration_part3.py') 
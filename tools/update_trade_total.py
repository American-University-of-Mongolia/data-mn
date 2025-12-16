#!/usr/bin/env python3
"""
Update trade-total to be a regular dataset (not parent).
Both datasets should be standalone.
"""

import sys
from pathlib import Path

# Add registry module to path
sys.path.insert(0, str(Path(__file__).parent))

from registry import Registry

# Initialize registry
reg = Registry()

# Get the datasets
dataset1 = reg.get_dataset('trade-total')
dataset2 = reg.get_dataset('trade-exports-imports')

# Update trade-total to not be a parent
dataset1.is_parent = False
reg.update_dataset(dataset1)

# Update trade-exports-imports to not have a parent
dataset2.parent_id = None
reg.update_dataset(dataset2)

print("✅ Updated datasets:")
print("  - trade-total: is_parent = False")
print("  - trade-exports-imports: parent_id = NULL")
print("\nBoth are now standalone datasets with their own pages.")

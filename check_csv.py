# check_csv.py
import pandas as pd
import os

# Check if file exists
csv_path = 'smart_inventory_dataset.csv'
print(f"Looking for file: {csv_path}")
print(f"File exists: {os.path.exists(csv_path)}")
print(f"Current directory: {os.getcwd()}")

if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"\n✅ CSV loaded successfully!")
    print(f"📊 Rows: {len(df)}")
    print(f"📋 Columns: {list(df.columns)}")
    print(f"\nFirst 3 rows:")
    print(df.head(3))
else:
    print(f"\n❌ File not found! Please check the filename.")
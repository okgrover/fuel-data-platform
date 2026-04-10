import pandas as pd
import os

# Define paths
raw_dir = "data/raw"
processed_dir = "data/processed"

# Ensure processed directory exists
os.makedirs(processed_dir, exist_ok=True)

# Convert the known Excel files to CSV with the correct sheet names
sources = [
    ("source2_uk.xlsx", "4.1.1", "source2_uk.csv"),
    ("source3_uk.xlsx", 0, "source3_uk.csv"),
]

for excel_file, sheet_name, output_file in sources:
    file_path = os.path.join(raw_dir, excel_file)

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        csv_path = os.path.join(processed_dir, output_file)
        df.to_csv(csv_path, index=False)
        print(f"Converted {excel_file} to {output_file}")
    except Exception as e:
        print(f"Error converting {excel_file}: {e}")

print("Excel files converted to CSV.")
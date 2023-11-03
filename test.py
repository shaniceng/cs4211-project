import pandas as pd
import sys
import os

"""
    Processes all CSV files in a specified folder, extracting information from each file.

    Parameters:
    - folder_path (str): The path to the folder containing the CSV files.

    Returns:
    None
"""
def process_csv_files(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    for file in files:
        file_path = os.path.join(folder_path, file)
        match_df = pd.read_csv(file_path)
        file_parts = file.split('_')
        date = file_parts[2].split('.')[0]
        for index, row in match_df.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            # print(f"Home: {home_team}, Away: {away_team}, Date: {date}")

            # Function to write to a file

def main():
    folder_path = 'Datasets/matches'
    process_csv_files(folder_path)
    
if __name__ == "__main__":
    main()

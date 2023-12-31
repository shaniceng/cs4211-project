import os
import re
import numpy as np
import pandas as pd
import csv

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def shorten_year(year):
    # This function takes a year in the format 'YYYY' and returns it in the format 'YY'
    return year[-2:]

def modify_file_name(file_name):
    # This function takes a file name in the format 'YYYYYYYY.csv' and returns it in the format 'YYYY.csv'
    # It uses regular expressions to find all occurrences of four digit years in the file name
    # Then it uses the shorten_year function to replace each four digit year with a two digit year
    matches = re.findall(r'\d{4}', file_name)
    if len(matches) == 2:
        # If there are two matches, it means we have a file name in the format 'YYYYYYYY.csv'
        # We shorten both years and concatenate them
        return shorten_year(matches[0]) + shorten_year(matches[1]) + '.csv'
    elif len(matches) == 1:
        # If there is only one match, it means we have a file name in the format 'YYYY.csv'
        # We just shorten the year
        return shorten_year(matches[0]) + '.csv'
    else:
        # If there are no matches, we return the original file name
        return file_name

def extract_data(directory):
    for root, dirs, files in os.walk(directory):
        files.sort()
        for i in range(0, len(files), 2):
            file1_path = os.path.join(root, files[i])
            if i+1 < len(files):
                file2_path = os.path.join(root, files[i+1])
            else:
                continue  # Skip the rest of the loop for the last file if there's no matching pair

            with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
                data1 = f1.read()
                data2 = f2.read()

            matches_away = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data1)
            probabilities_away = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data1)
            matches_home = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data2)
            probabilities_home = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data2)

            # Modify the output file path here
            output_file_path = os.path.join(os.path.dirname(os.path.dirname(file1_path)), 'betting_simulation', 'new_probabilities', modify_file_name(os.path.splitext(os.path.basename(file1_path))[0].replace('_away', '')))
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)  # Ensure the directory exists

            with open(output_file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['match_url', 'home_prob_softmax'])  # Write the headers

                for match_away, probability_away, match_home, probability_home in zip(matches_away, probabilities_away, matches_home, probabilities_home):
                    average_probability_away = (float(probability_away[0]) + float(probability_away[1])) / 2
                    average_probability_home = (float(probability_home[0]) + float(probability_home[1])) / 2
                    softmax_probabilities = softmax(np.array([average_probability_home, average_probability_away]))
                    match_away = match_away.replace('-', ' ')
                    match_home = match_home.replace('-', ' ')
                    info_array = match_away.split('_')
                    year = info_array[0]
                    team1 = info_array[2]
                    team2 = info_array[3]
                    csv_file = pd.read_csv(f'Datasets/matches/epl_matches_{year}.csv')
                    match_row = csv_file[((csv_file['home_team'] == team1) & (csv_file['away_team'] == team2))]
                    if not match_row.empty:
                        match_url = match_row['match_url'].values[0]
                        writer.writerow([match_url, softmax_probabilities[0]])  # Write the data

# Call the function with your directory path
extract_data('probability_results')

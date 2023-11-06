import os
import re
import numpy as np
import pandas as pd

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

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

            matches1 = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data1)
            probabilities1 = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data1)

            matches2 = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data2)
            probabilities2 = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data2)

            output_file_path = os.path.splitext(file1_path)[0].replace('_away', '') + '.txt'
            with open(output_file_path, 'w') as f:
                for match1, probability1, match2, probability2 in zip(matches1, probabilities1, matches2, probabilities2):
                    average_probability1 = (float(probability1[0]) + float(probability1[1])) / 2
                    average_probability2 = (float(probability2[0]) + float(probability2[1])) / 2

                    softmax_probabilities = softmax(np.array([average_probability1, average_probability2]))

                    match1 = match1.replace('-', ' ')
                    match2 = match2.replace('-', ' ')
                    info_array = match1.split('_')
                    year = info_array[0]
                    team1 = info_array[2]
                    team2 = info_array[3]
                    csv_file = pd.read_csv(f'Datasets/matches/epl_matches_{year}.csv')
                    match_row = csv_file[((csv_file['home_team'] == team1) & (csv_file['away_team'] == team2))]
                    if not match_row.empty:
                        match_url = match_row['match_url'].values[0]

                        f.write(f'Match: {match1.replace("_away", "").replace("_home", "")}\n')
                        f.write(f'Softmax Probability: {softmax_probabilities[0]}\n')
                        f.write(f'Match Url: {match_url}\n\n')
# Call the function with your directory path
extract_data('probability_results')

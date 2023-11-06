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

            matches_away = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data1)
            probabilities_away = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data1)
            matches_home = re.findall(r'\*{3,}\n\*(.*?)\n\*{3,}', data2)
            probabilities_home = re.findall(r'The Assertion .* is Valid with Probability \[(.*?), (.*?)\];', data2)

            # Modify the output file path here
            output_file_path = os.path.join(os.path.dirname(os.path.dirname(file1_path)), 'softmax_probabilities', os.path.splitext(os.path.basename(file1_path))[0].replace('_away', '') + '.txt')
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)  # Ensure the directory exists

            with open(output_file_path, 'w') as f:
                for match_away, probability_away, match_home, probability_home in zip(matches_away, probabilities_away, matches_home, probabilities_home):
                    average_probability_away = (float(probability_away[0]) + float(probability_away[1])) / 2
                    average_probability_home = (float(probability_home[0]) + float(probability_home[1])) / 2
                    print("\n match 1: ", match_away)
                    print('\navg prob 1: ', average_probability_away)
                    print("\n match 2: ", match_home)
                    print('\navg prob 2: ', average_probability_home)
                    softmax_probabilities = softmax(np.array([average_probability_home, average_probability_away]))
                    print('\nsoftmax probabilities: ', softmax_probabilities[0])
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

                        f.write(f'Match: {match_away.replace("_away", "").replace("_home", "")}\n')
                        f.write(f'Softmax Probability: {softmax_probabilities[0]}\n')
                        f.write(f'Match Url: {match_url}\n\n')
# Call the function with your directory path
extract_data('probability_results')

import os
import re
import numpy as np

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def extract_data(directory):
    for root, dirs, files in os.walk(directory):
        files.sort()
        for i in range(0, len(files), 2):
            file1_path = os.path.join(root, files[i])
            file2_path = os.path.join(root, files[i+1])

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

                    f.write(f'Match: {match1.replace("_away", "")}\n')
                    f.write(f'Softmax Probability: {softmax_probabilities[0]}\n\n')
                    f.write(f'Match: {match2.replace("_home", "")}\n')
                    f.write(f'Softmax Probability: {softmax_probabilities[1]}\n\n')

# Call the function with your directory path
extract_data('probability_results')

import pandas as pd
import sys
import os
import traceback
import datetime

# Get match and team details
def find_match_and_teams(match_path, team_path, home_team, away_team):
    # Read CSV files into dataframes
    match_df = pd.read_csv(match_path)
    team_df = pd.read_csv(team_path)

    # Replace NaN values with 1 in team_df
    team_df = team_df.fillna(1)

    # Find match
    match_row_condition = (match_df['home_team'] == home_team) & (match_df['away_team'] == away_team)
    matching_rows = match_df[match_row_condition]

    # Find team
    home_row_condition = (team_df['club_name'] == home_team)
    away_row_condition = (team_df['club_name'] == away_team)
    home_rows = team_df[home_row_condition]
    away_rows = team_df[away_row_condition]

    # print("home_rows: " + str(home_rows))

    return matching_rows, home_rows, away_rows, team_df

# Get match details and team formation details
def find_team_formation_and_rating(matching_rows, team):

    if (team == "home"):
        # Find Home Formation
        formation = matching_rows.iloc[0]['home_formation']
        formation = process_formation_to_dict(formation)

        # Find Away Team Rating
        xi_names_array = matching_rows['home_xi_names'].iloc[0].split(',')
        sequence_array = matching_rows['home_sequence'].iloc[0].split(',')
        xi_ID_array = matching_rows['home_xi_sofifa_ids'].iloc[0].split(',')

        # Convert the substrings to integers
        xi_ID_array = [i.split('.')[0] for i in xi_ID_array]

    else:
        # Find Away Formation
        formation = matching_rows.iloc[0]['away_formation']
        formation = process_formation_to_dict(formation)

        # Find Away Team Rating
        xi_names_array = matching_rows['away_xi_names'].iloc[0].split(',')
        sequence_array = matching_rows['away_sequence'].iloc[0].split(',')
        xi_ID_array = matching_rows['away_xi_sofifa_ids'].iloc[0].split(',')

        # Convert the substrings to integers
        xi_ID_array = [i.split('.')[0] for i in xi_ID_array]

    return formation, xi_names_array, sequence_array, xi_ID_array

# Gets the player details for split by their row positions on the grid
def team_player_details(matching_rows, sequence_array, xi_ID_array, rows, team):
    if (team == "home"):
        # Find Away Formation
        formation = matching_rows.iloc[0]['home_formation']
        formation = process_formation_to_dict(formation)
    else:
        # Find Home Formation
        formation = matching_rows.iloc[0]['away_formation']
        formation = process_formation_to_dict(formation)

    # print("team: " + str(team))
    # print("formation: " + str(formation))
        
    # Split players by their formation positions
    atkKep_i = 1
    atkDefPos_i = formation['atkDefPos'] + atkKep_i
    atkMidPos_i = formation['atkMidPos'] + atkDefPos_i
    atkForPos_i = formation['atkForPos'] + atkMidPos_i
    # print("atkKep_i: " + str(atkKep_i) + ", atkDefPos_i: " + str(atkDefPos_i) + ", atkMidPos_i: " + str(atkMidPos_i) + ", atkForPos_i: " + str(atkForPos_i))

    atkKep_sequence_array = sequence_array[0:atkKep_i]
    atkDefPos_sequence_array = sequence_array[atkKep_i:atkDefPos_i]
    atkMidPos_sequence_array = sequence_array[atkDefPos_i:atkMidPos_i]
    atkForPos_sequence_array = sequence_array[atkMidPos_i:atkForPos_i]
    # print(atkKep_sequence_array)
    # print(atkDefPos_sequence_array)
    # print(atkMidPos_sequence_array)
    # print(atkForPos_sequence_array)

    atkKep_ID_array = xi_ID_array[0:atkKep_i]
    atkDefPos_ID_array = xi_ID_array[atkKep_i:atkDefPos_i]
    atkMidPos_ID_array = xi_ID_array[atkDefPos_i:atkMidPos_i]
    atkForPos_ID_array = xi_ID_array[atkMidPos_i:atkForPos_i]
    # print(atkForPos_ID_array)

    atkKep_ID_array = [int(x) for x in atkKep_ID_array]
    atkDefPos_ID_array = [int(x) for x in atkDefPos_ID_array]
    atkMidPos_ID_array = [int(x) for x in atkMidPos_ID_array]
    atkForPos_ID_array = [int(x) for x in atkForPos_ID_array]
    # print(atkForPos_ID_array)

    # Get player ratings based on atkMidPos_xi_ID_array from away_rows
    atkKep_player_details = pd.concat([rows[rows['sofifa_id'] == id] for id in atkKep_ID_array], ignore_index=True)
    atkDefPos_player_details = pd.concat([rows[rows['sofifa_id'] == id] for id in atkDefPos_ID_array], ignore_index=True)
    atkMidPos_player_details = pd.concat([rows[rows['sofifa_id'] == id] for id in atkMidPos_ID_array], ignore_index=True)
    atkForPos_player_details = pd.concat([rows[rows['sofifa_id'] == id] for id in atkForPos_ID_array], ignore_index=True)
    # print(atkForPos_player_details)

    # Add position to player details
    atkKep_player_details.loc[:, 'pos'] = atkKep_sequence_array.copy()
    atkDefPos_player_details.loc[:, 'pos'] = atkDefPos_sequence_array.copy()
    atkMidPos_player_details.loc[:, 'pos'] = atkMidPos_sequence_array.copy()
    atkForPos_player_details.loc[:, 'pos'] = atkForPos_sequence_array.copy()

    return atkKep_player_details,atkDefPos_player_details,atkMidPos_player_details,atkForPos_player_details

# Function to calculate the probabilities for each player in the atkMidPos
def cal_atkDef_values(atkDefPos_player_details, oppAtkForPos_player_details):

    atkDefPos_sequence_array = atkDefPos_player_details['pos']
    atkDefPos = process_sequence_to_formatted_array(atkDefPos_sequence_array)
    oppAtkForPos_sequence_array = oppAtkForPos_player_details['pos']
    
    # How the probability of losing the ball is calculated
    total_max_values = 0
    for i, position in enumerate(oppAtkForPos_sequence_array):
        max_value = max(oppAtkForPos_player_details['defending_standing_tackle'].iloc[i], oppAtkForPos_player_details['defending_sliding_tackle'].iloc[i], oppAtkForPos_player_details['mentality_interceptions'].iloc[i])
        total_max_values += max_value
    prob_lose_ball = round(total_max_values / len(oppAtkForPos_sequence_array))

    result = "AtkDef = "
    for i, position in enumerate(atkDefPos_sequence_array):
        result += f"["
        result += f"pos[{position}] == 1]Def("
        result += f"{atkDefPos_player_details['attacking_short_passing'].iloc[i]}, "
        result += f"{atkDefPos_player_details['skill_long_passing'].iloc[i]}, "
        result += f"{prob_lose_ball}, "
        result += f"{position}"
        result += ")"
        if i < len(atkDefPos_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    return atkDefPos, result

# Function to calculate the probabilities for each player in the atkMidPos
def cal_atkMid_values(atkMidPos_player_details, oppAtkMidPos_player_details):

    atkMidPos_sequence_array = atkMidPos_player_details['pos']

    atkMidPos = process_sequence_to_formatted_array(atkMidPos_sequence_array)

    oppAtkMidPos_sequence_array = oppAtkMidPos_player_details['pos']
    
    # How the probability of losing the ball is calculated
    total_max_values = 0
    for i, position in enumerate(oppAtkMidPos_sequence_array):
        max_value = max(oppAtkMidPos_player_details['defending_standing_tackle'].iloc[i], oppAtkMidPos_player_details['defending_sliding_tackle'].iloc[i], oppAtkMidPos_player_details['mentality_interceptions'].iloc[i])
        total_max_values += max_value
    prob_lose_ball = round(total_max_values / len(oppAtkMidPos_sequence_array))

    result = "AtkMid = "
    for i, position in enumerate(atkMidPos_sequence_array):
        result += f"["
        result += f"pos[{position}] == 1]Mid("
        result += f"{atkMidPos_player_details['attacking_short_passing'].iloc[i]}, "
        result += f"{atkMidPos_player_details['skill_long_passing'].iloc[i]}, "
        result += f"{atkMidPos_player_details['power_long_shots'].iloc[i]}, "
        result += f"{prob_lose_ball}, "
        result += f"{position}"
        result += ")"
        if i < len(atkMidPos_sequence_array) - 1:
            result += " [] "
    
    result += ";"

    Kov = "{"
    pos_list = ['L', 'LR', 'CL', 'C', 'CR', 'RL', 'R']

    for pos in pos_list:
        if any(pos == position for position in atkMidPos_sequence_array):
            Kov += f"pos[{pos}] = 1; "
        else:
            Kov += f"pos[{pos}] = 0; "

    Kov += "}"

    return atkMidPos, result, Kov

# Function to move duplicate positions to the next free space
def move_duplicates(sequence_array):
    position_switch = ["L", "LR", "CL", "C", "CR", "RL", "R"]
    position_count = {position: 0 for position in position_switch}
    sequence_array_copy = sequence_array.copy()

    for i in range(len(sequence_array)):
        position = sequence_array_copy[i]
        position_count[position] += 1

        if position_count[position] > 1:
            next_index = (position_switch.index(position) + 1) % len(position_switch)
            
            # Find the next available position, either to the right or left
            while position_count[position_switch[next_index]] > 0:
                next_index = (next_index + 1) % len(position_switch)
                if next_index == position_switch.index(position):
                    # If no more right positions, move to the left
                    next_index = (next_index - 2) % len(position_switch)
            
            # Replace the first occurrence of the position with the next available position in the copy
            sequence_array_copy[i] = position_switch[next_index]
            position_count[position_switch[next_index]] += 1

    return sequence_array_copy


# Function to calculate the probabilities for each player in the atkForPos
def cal_atkFor_values(atkForPos_player_details, homeDefPos_player_details, away_rows, home_rows):

    atkForPos_sequence_array = atkForPos_player_details['pos']
    homeDefPos_sequence_array = homeDefPos_player_details['pos']

    # Move duplicates in atkForPos_sequence_array
    atkForPos_sequence_array = move_duplicates(atkForPos_sequence_array)

    atkForPos = process_sequence_to_formatted_array(atkForPos_sequence_array)

    position_switch = {
        "L": ["RL", "R"],
        "LR": ["CR", "RL", "R"],
        "CL": ["C", "CR", "RL"],
        "C": ["CL", "C", "CR"],
        "CR": ["LR", "CL", "C"],
        "RL": ["L", "LR", "CL"],
        "R": ["L", "LR"],
    }

    result = "AtkFor = "
    for i, position in enumerate(atkForPos_sequence_array):
        positions_to_consider = position_switch.get(position)
        # Create a Series with 'mentality_aggression' values
        mentality_aggression_series = homeDefPos_player_details.loc[homeDefPos_sequence_array.isin(positions_to_consider), 'mentality_aggression']
        max_mentality_aggression = mentality_aggression_series.max()
        result += f"["
        result += f"pos[{position}] == 1]For("
        result += f"{atkForPos_player_details['attacking_finishing'].iloc[i]}, "
        result += f"{atkForPos_player_details['power_long_shots'].iloc[i]}, "
        result += f"{atkForPos_player_details['attacking_volleys'].iloc[i]}, "
        result += f"{atkForPos_player_details['attacking_heading_accuracy'].iloc[i]}, "
        result += f"{round((homeDefPos_player_details['defending_marking'].max() + homeDefPos_player_details['defending_standing_tackle'].max() + homeDefPos_player_details['defending_sliding_tackle'].max())/3)}, "
        result += f"{round(max_mentality_aggression)}, " 
        result += f"{away_rows['mentality_penalties'].max()}, "
        result += f"{round(0.1 * atkForPos_player_details.iloc[i]['power_jumping'] + 0.6 * atkForPos_player_details.iloc[i]['attacking_heading_accuracy'] + 0.3 * round((atkForPos_player_details.iloc[i]['height_cm'] / max(away_rows['height_cm'].max(), home_rows['height_cm'].max())) * 100))}, "
        result += f"{position}"
        result += ")"
        if i < len(atkForPos_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    return atkForPos, result

# Function to calculate the probabilities for each player in the atkKepPos
def cal_atkKep_values(atkKep_plyr_details, atkMidPos_plyr_details):
    
    # Initial goal keeper
    player_count = 1
    atkKep_sequence_array = atkKep_plyr_details['pos']
    atkKepPos = process_sequence_to_formatted_array(atkKep_sequence_array)

    atkMid_sequence_array = atkMidPos_plyr_details['pos']
    atkMidPos = process_sequence_to_formatted_array(atkMid_sequence_array)
    # Sets initial probability rating to 0
    prob_pass_mid = 0
    # Get the midfielders' positioning ratings and add them
    for i, position in enumerate(atkMid_sequence_array):
        player_count += 1
        prob_pass_mid += int(atkMidPos_plyr_details['mentality_positioning'].iloc[i])

    result = "AtkKep = ["
    for i, position in enumerate(atkKep_sequence_array):
        # Add gk_kicking rating and then divide by 4 to give equal weighting, then divide by 4 again as a scale factor
        prob_pass_mid += int(atkKep_plyr_details['gk_kicking'].iloc[i])
        prob_pass_mid = round((prob_pass_mid / player_count) / 1.5)

        result += f"pos[{position}] == 1]Kep_1("
        result += f"{int(atkKep_plyr_details['gk_kicking'].iloc[i])}, "
        result += f"{int(atkKep_plyr_details['gk_kicking'].iloc[i])}, "
        result += f"{prob_pass_mid}, "
        result += f"{position}"
        result += ")"
        if i < len(atkKep_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    return atkKepPos, result

# Function to calculate the probabilities for each player in the defKepPos
def cal_defKep_values(defKep_plyr_details):
    
    atkKep_sequence_array = defKep_plyr_details['pos']
    defKepPos = process_sequence_to_formatted_array(atkKep_sequence_array)

    prob_defending_value = 0
    for i, position in enumerate(atkKep_sequence_array):
        def_handling_value = round(0.3 * int(defKep_plyr_details['gk_diving'].iloc[i]) + 0.2 * int(defKep_plyr_details['gk_handling'].iloc[i]) + 0.05 * int(defKep_plyr_details['gk_kicking'].iloc[i]) + 0.2*int(defKep_plyr_details['gk_reflexes'].iloc[i]) + 0.05*int(defKep_plyr_details['gk_speed'].iloc[i]) + 0.2*int(defKep_plyr_details['gk_positioning'].iloc[i]))


    result = "DefKep = "
    for i, position in enumerate(atkKep_sequence_array):
        result += f"["
        result += f"pos[{position}] == 1]Kep_2("
        result += f"{def_handling_value},"
        result += f"{position}"
        result += ")"
        if i < len(atkKep_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    return defKepPos, result

# Process formation string to dictionary containing the number of players in each position atkDefPos, atkMidPos, atkForPos
def process_formation_to_dict(formation):
    positions = formation.split('-')
    if (positions[-1] == '0'):
        positions.pop()
    
    if len(positions) == 3: #def mid for
        atkDefPos = int(positions[0])
        atkMidPos = int(positions[1])
        atkForPos = int(positions[2])
    elif len(positions) == 4: #def mid mid for
        atkDefPos = int(positions[0])
        atkMidPos = int(positions[1]) + int(positions[2]) 
        atkForPos = int(positions[3]) 
    elif len(positions) == 5: #def mid mid mid for 
        atkDefPos = int(positions[0])
        atkMidPos = int(positions[1]) + int(positions[2]) + int(positions[3])
        atkForPos = int(positions[4])
    else:
        raise ValueError("Invalid input format. Must be in the format 'X-Y-Z' or 'X-Y-Z-W' or 'X-Y-Z-W-V.")
    
    return {"atkDefPos": atkDefPos, "atkMidPos": atkMidPos, "atkForPos": atkForPos}

# Converts an array of string sequences to defined grid positions used in PAT
def process_sequence_to_formatted_array(sequence_array):
    pos_array = [-1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]

    for item in sequence_array:
        if item == "L":
            pos_array[6] = 1
        elif item == "LR":
            pos_array[7] = 1
        elif item == "CL":
            pos_array[8] = 1
        elif item == "C":
            pos_array[9] = 1
        elif item == "CR":
            pos_array[10] = 1
        elif item == "RL":
            pos_array[11] = 1    
        elif item == "R":
            pos_array[12] = 1  
    
    return pos_array

# Generate pcsp file
def generate_pcsp(input, Kov, date, home_name, away_name, output_folder, team):
    output_folder = os.path.join('output', '%s_%s' % (date,team))
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    file_name = os.path.join(output_folder, '%s_%s_%s_%s.pcsp' % (date, home_name.replace(' ', '-'), away_name.replace(' ', '-'), team))

    lines_1 = []
    with open('var.txt') as f:
        lines_1 = f.readlines()

    lines_2 = [input]  # Use a list to hold the input string

    with open('body.txt') as f:
        lines_3 = f.readlines()
    
    for i, line in enumerate(lines_3):
        lines_3[i] = line.replace('<Keeper volley to midfielders>', Kov)

    lines = lines_1 + lines_2 + lines_3
    with open(file_name, 'w') as f:
        f.writelines(lines)

def generate_match(home_team, away_team, date):
    try:
        # Replace 'file1.csv' and 'file2.csv' with your actual file names
        match_path = 'Datasets/matches/epl_matches_'+ date + '.csv'
        team_path = 'Datasets/ratings/epl_ratings_'+ date + '.csv'

        # home_team = 'AFC Bournemouth'
        # away_team = 'Aston Villa'
        # date = '20152016'

        matching_rows, home_rows, away_rows, team_df = find_match_and_teams(match_path, team_path, home_team, away_team)

        # Get match details and team formation details
        away_formation, away_xi_names_array, away_sequence_array, away_xi_ID_array = find_team_formation_and_rating(matching_rows, "away")
        home_formation, home_xi_names_array, home_sequence_array, home_xi_ID_array = find_team_formation_and_rating(matching_rows, "home")

        # Get player team details by their grid row positions
        away_atkKep_plyr_details, away_atkDefPos_plyr_details, away_atkMidPos_plyr_details, away_atkForPos_plyr_details = team_player_details(matching_rows,away_sequence_array, away_xi_ID_array, team_df, "away")
        # print("away_atkKep_plyr_details: " + str(away_atkKep_plyr_details) + ", away_atkDefPos_plyr_details: " + str(away_atkDefPos_plyr_details) + ", away_atkMidPos_plyr_details: " + str(away_atkMidPos_plyr_details) + ", away_atkForPos_plyr_details: " + str(away_atkForPos_plyr_details) + ", away_defKepPos_plyr_details: ")
        home_atkKep_plyr_details, home_atkDefPos_plyr_details, home_atkMidPos_plyr_details, home_atkForPos_plyr_details = team_player_details(matching_rows,home_sequence_array, home_xi_ID_array, team_df, "home")
        # print("home_atkKep_plyr_details: " + str(home_atkKep_plyr_details) + ", home_atkDefPos_plyr_details: " + str(home_atkDefPos_plyr_details) + ", home_atkMidPos_plyr_details: " + str(home_atkMidPos_plyr_details) + ", home_atkForPos_plyr_details: " + str(home_atkForPos_plyr_details) + ", home_defKepPos_plyr_details: ")


        # Define position grid and dynamic code for AWAY team
        away_atkKepPos, away_AtkKep = cal_atkKep_values(away_atkKep_plyr_details, away_atkMidPos_plyr_details)
        away_atkDefPos, away_AtkDef = cal_atkDef_values(away_atkDefPos_plyr_details, home_atkForPos_plyr_details)
        away_atkMidPos, away_AtkMid, away_Kov = cal_atkMid_values(away_atkMidPos_plyr_details, home_atkMidPos_plyr_details)
        away_atkForPos, away_AtkFor = cal_atkFor_values(away_atkForPos_plyr_details, home_atkDefPos_plyr_details, away_rows, home_rows)
        away_defKepPos, away_DefKep = cal_defKep_values(home_atkKep_plyr_details)

        # Define position grid and dynamic code for HOME team
        home_atkKepPos, home_AtkKep = cal_atkKep_values(home_atkKep_plyr_details, home_atkMidPos_plyr_details)
        home_atkDefPos, home_AtkDef = cal_atkDef_values(home_atkDefPos_plyr_details, away_atkForPos_plyr_details)
        home_atkMidPos, home_AtkMid, home_Kov = cal_atkMid_values(home_atkMidPos_plyr_details, away_atkMidPos_plyr_details)
        home_atkForPos, home_AtkFor = cal_atkFor_values(home_atkForPos_plyr_details, away_atkDefPos_plyr_details, home_rows, away_rows)
        home_defKepPos, home_DefKep = cal_defKep_values(away_atkKep_plyr_details)
        
        #Print to check
        # print("Away team")
        # print("atkKepPos" + str(away_atkKepPos) + "\n" + str(away_AtkKep))
        # print("atkDefPos" + str(away_atkDefPos) + "\n" + str(away_AtkDef))
        # print("atkMidPos" + str(away_atkMidPos) + "\n" + str(away_AtkMid) + "\n" + str(away_Kov))
        # print("atkForPos" + str(away_atkForPos) + "\n" + str(away_AtkFor))
        # print("defKepPos" + str(away_defKepPos) + "\n" + str(away_DefKep))

        # # Print to check
        # print("Home team")
        # print("atkKepPos" + str(home_atkKepPos) + "\n" + str(home_AtkKep))
        # print("atkDefPos" + str(home_atkDefPos) + "\n" + str(home_AtkDef))
        # print("atkMidPos" + str(home_atkMidPos) + "\n" + str(home_AtkMid))
        # print("atkForPos" + str(home_atkForPos) + "\n" + str(home_AtkFor))
        # print("defKepPos" + str(home_defKepPos) + "\n" + str(home_DefKep))

        # Get away team's formation and stats
        away_input = (
        "var atkKepPos = " + str(away_atkKepPos) + ";\n" +
        "var atkDefPos = " + str(away_atkDefPos) + ";\n" +
        "var atkMidPos = " + str(away_atkMidPos) + ";\n" +
        "var atkForPos = " + str(away_atkForPos) + ";\n" +
        "var defKepPos = " + str(away_defKepPos) + ";\n" +
        str(away_AtkKep) + "\n" +
        str(away_AtkDef) + "\n" +
        str(away_AtkMid) + "\n" +
        str(away_AtkFor) + "\n" +
        str(away_DefKep) + "\n"
        )
        # print(away_input)
        home_input = (
        "var atkKepPos = " + str(home_atkKepPos) + ";\n" +
        "var atkDefPos = " + str(home_atkDefPos) + ";\n" +
        "var atkMidPos = " + str(home_atkMidPos) + ";\n" +
        "var atkForPos = " + str(home_atkForPos) + ";\n" +
        "var defKepPos = " + str(home_defKepPos) + ";\n" +
        str(home_AtkKep) + "\n" +
        str(home_AtkDef) + "\n" +
        str(home_AtkMid) + "\n" +
        str(home_AtkFor) + "\n" +
        str(home_DefKep) + "\n"
        )
        # print(home_input)

        # Generate pcsp file (to be completed)
        output_folder = 'Output'
        generate_pcsp(away_input, away_Kov, date, home_team, away_team, output_folder, "away")
        generate_pcsp(home_input, home_Kov, date, home_team, away_team, output_folder, "home")

    except Exception as e:
        # Log the error to a file
        log_file_path = 'error_log.txt'
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"{current_time} - Error for match {home_team} vs {away_team} on {date}:\n{str(e)}\n\n"
        
        # Append the error message to the log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(error_message)

        # Continue with the rest of the code
        pass
    
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
            print(f"Home: {home_team}, Away: {away_team}, Date: {date}")
            generate_match(home_team, away_team, date)

def process():
    file_path = "Datasets\matches\epl_matches_20152016.csv"
    match_df = pd.read_csv(file_path)
    file_parts = file_path.split('_')
    date = file_parts[2].split('.')[0]
    for index, row in match_df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        print(f"Home: {home_team}, Away: {away_team}, Date: {date}")
        generate_match(home_team, away_team, date)

def clear_error_log():
    # Clear the contents of the error log file
    log_file_path = 'error_log.txt'
    with open(log_file_path, 'w') as log_file:
        log_file.write("")

def main():
    clear_error_log()
    folder_path = 'Datasets/matches'
    process_csv_files(folder_path)

    # Tesing one csv file
    # process()

    # Testing one match
    # generate_match("Manchester City", "Watford", "20152016")

if __name__ == "__main__":
    main()





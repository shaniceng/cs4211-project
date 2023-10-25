# generate_pcsp_for_match()


#     find_match_and_teams(match_path, team_path, home_team, away_team)

#     // Get info of match 
#         - formation
#         - Name
#         - id 

#     // Get info of team
#         - all the player info in team 

#     // Create dictionary for stat
#     Example:
#     4-3-3
#     keeper: 1
#     defender: 4
#     midfielder: 3
#     forward: 3

#     Example:
#     4-2-3-1
#     keeper: 1
#     defender: 4
#     midfielder: 5
#     forward: 1
#     output: dictionary


#     // Get player position
#     output: Array
#     Example: atkKepPos = [-1(6), 0, 0, 0, 1, 0, 0, 0, -1(6)] (For Def Mid For)



# // Dynamic code (append)
# input:
# dictionary - data
# Array - grid 
# - dynamic macro
# - dynamic grid
# - dynamic attack and home team 


# // Able to read multiple match
# read_multiple_match(match_path, team_path) {

#     generate_pcsp_for_match()
# }


import pandas as pd
import sys

# generate pcsp file
def generate_pcsp(params, date, home_name, away_name):
    file_name = '%s_%s_%s.pcsp' % (date, home_name.replace(' ', '-'), away_name.replace(' ', '-'))
    # write to file
    lines =[]
    lines_1 = []
    for key, value in keeper_stats.items():
            lines_1.append('#define %s %s;\n' % (key, value))
    with open('away.txt') as f:
            lines_2 = f.readlines()

    lines = lines_1 + lines_2
    with open(file_name, 'w') as f:
        f.writelines(lines)

def find_match_and_teams(match_path, team_path, home_team, away_team):
    # Read CSV files into dataframes
    match_df = pd.read_csv(match_path)
    team_df = pd.read_csv(team_path)

    # Find match
    match_row_condition = (match_df['home_team'] == home_team) & (match_df['away_team'] == away_team)
    matching_rows = match_df[match_row_condition]

    # Find team
    home_row_condition = (team_df['club_name'] == home_team)
    away_row_condition = (team_df['club_name'] == away_team)
    home_rows = team_df[home_row_condition]
    away_rows = team_df[away_row_condition]

    return matching_rows, home_rows, away_rows

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
def team_player_details(matching_rows,away_sequence_array, away_xi_ID_array, away_rows, team):

    if (team == "home"):
        # Find Away Formation
        formation = matching_rows.iloc[0]['home_formation']
        formation = process_formation_to_dict(formation)
    else:
        # Find Home Formation
        formation = matching_rows.iloc[0]['away_formation']
        formation = process_formation_to_dict(formation)
        
    # Split players by their formation positions
    atkKep_i = 1
    atkDefPos_i = away_formation['atkDefPos'] + atkKep_i
    atkMidPos_i = away_formation['atkMidPos'] + atkDefPos_i
    atkForPos_i = away_formation['atkForPos'] + atkMidPos_i

    atkKep_sequence_array = away_sequence_array[0:atkKep_i]
    atkDefPos_sequence_array = away_sequence_array[atkKep_i:atkDefPos_i]
    atkMidPos_sequence_array = away_sequence_array[atkDefPos_i:atkMidPos_i]
    atkForPos_sequence_array = away_sequence_array[atkMidPos_i:atkForPos_i]

    atkKep_ID_array = away_xi_ID_array[0:atkKep_i]
    atkDefPos_ID_array = away_xi_ID_array[atkKep_i:atkDefPos_i]
    atkMidPos_ID_array = away_xi_ID_array[atkDefPos_i:atkMidPos_i]
    atkForPos_ID_array = away_xi_ID_array[atkMidPos_i:atkForPos_i]

    atkKep_ID_array = [int(x) for x in atkKep_ID_array]
    atkDefPos_ID_array = [int(x) for x in atkDefPos_ID_array]
    atkMidPos_ID_array = [int(x) for x in atkMidPos_ID_array]
    atkForPos_ID_array = [int(x) for x in atkForPos_ID_array]

    # Get player ratings based on atkMidPos_xi_ID_array from away_rows
    atkKep_player_details = pd.concat([away_rows[away_rows['sofifa_id'] == id] for id in atkKep_ID_array], ignore_index=True)
    atkDefPos_player_details = pd.concat([away_rows[away_rows['sofifa_id'] == id] for id in atkDefPos_ID_array], ignore_index=True)
    atkMidPos_player_details = pd.concat([away_rows[away_rows['sofifa_id'] == id] for id in atkMidPos_ID_array], ignore_index=True)
    atkForPos_player_details = pd.concat([away_rows[away_rows['sofifa_id'] == id] for id in atkForPos_ID_array], ignore_index=True)

    # Add position to player details
    atkKep_player_details.loc[:, 'pos'] = atkKep_sequence_array.copy()
    atkDefPos_player_details.loc[:, 'pos'] = atkDefPos_sequence_array.copy()
    atkMidPos_player_details.loc[:, 'pos'] = atkMidPos_sequence_array.copy()
    atkForPos_player_details.loc[:, 'pos'] = atkForPos_sequence_array.copy()

    return atkKep_player_details,atkDefPos_player_details,atkMidPos_player_details,atkForPos_player_details

# Function to calculate the probabilities for each player in the atkMidPos
def cal_atkMid_values(atkMidPos_player_details):

    atkMidPos_sequence_array = atkMidPos_player_details['pos']

    atkMidPos = process_sequence_to_formatted_array(atkMidPos_sequence_array)

    # TODO: calculate probabilities

    result = "AtkMid = ["
    for i, position in enumerate(atkMidPos_sequence_array):
        result += f"pos[{position}] == 1]Mid("
        result += f"{atkMidPos_player_details['attacking_short_passing'].iloc[i]}, "
        result += f"{atkMidPos_player_details['skill_long_passing'].iloc[i]}, "
        result += f"{atkMidPos_player_details['power_long_shots'].iloc[i]}, "
        result += "59, " # ask TA how it is calculated
        result += "68, " # ask TA how it is calculated
        result += f"{position}"
        result += ")"
        if i < len(atkMidPos_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    print(result)
    return atkMidPos, result

# XY old code -> now using cal_atk_def_KepPos_values method (can be removed?)
def find_away_keeper_stats(away_xi_names_array, away_xi_ID_array, away_rows):
    # Find Away Keeper
    Keeper = away_xi_names_array[0]
    Keeper_ID = away_xi_ID_array[0]
    print("Away Keeper name: " + Keeper + ", ID: " + str(Keeper_ID))

    # Atkkep Defkep Rating
    keeper_id_int = int(Keeper_ID)
    keeper_row = away_rows[away_rows['sofifa_id'] == keeper_id_int]
    keeper_short_pass = keeper_row.iloc[0]['gk_kicking']
    keeper_long_pass = keeper_row.iloc[0]['gk_kicking']
    keeper_handling = keeper_row.iloc[0]['gk_handling']
    print("Away Keeper short_pass: " + str(keeper_short_pass))
    print("Away Keeper long_pass: " + str(keeper_long_pass))
    print("Away Keeper handling: " + str(keeper_handling))

    keeper_stats = {
        'ATKKEP_SHORT_PASS': keeper_short_pass,
        'ATKKEP_LONG_PASS': keeper_long_pass,
        'DEFKEP_HANDLING': keeper_handling
    }

    return keeper_stats

# Function to calculate the probabilities for each player in the atkDefPos
def cal_atk_def_KepPos_values(away_atkKep_plyr_details):
    
    atkKep_sequence_array = away_atkKep_plyr_details['pos']
    atkKepPos = process_sequence_to_formatted_array(atkKep_sequence_array)

    result = "AtkKep = ["
    for i, position in enumerate(atkKep_sequence_array):
        result += f"pos[{position}] == 1]Kep_1("
        result += f"{int(away_atkKep_plyr_details['gk_kicking'].iloc[i])}, "
        result += f"{int(away_atkKep_plyr_details['gk_kicking'].iloc[i])}, "
        result += "68, " # TODO: ask Julian how it is calculated
        result += f"{position}"
        result += ")"
        if i < len(atkKep_sequence_array) - 1:
            result += " [] "
    
    result += ";"
    print(result)
    return atkKepPos, result

# Process formation string to dictionary containing the number of players in each position atkDefPos, atkMidPos, atkForPos
def process_formation_to_dict(away_formation):
    positions = away_formation.split('-')
    
    if len(positions) == 3:
        atkDefPos = int(positions[0])
        atkMidPos = int(positions[1])
        atkForPos = int(positions[2])
    elif len(positions) == 4:
        atkDefPos = int(positions[0])
        atkMidPos = int(positions[1]) + int(positions[2])
        atkForPos = int(positions[3])
    else:
        raise ValueError("Invalid input format. Must be in the format 'X-Y-Z' or 'X-Y-Z-W'.")
    
    return {"atkDefPos": atkDefPos, "atkMidPos": atkMidPos, "atkForPos": atkForPos}

# Converts an array of string sequences to defined grid positions used in PAT
def process_sequence_to_formatted_array(sequence_array):
    pos_array = [-1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1, -1, -1, -1]
    print("pos_array: " + str(pos_array))

    for item in sequence_array:
        if item == "L":
            pos_array[7] = 1
        elif item == "LR":
            pos_array[8] = 1
        elif item == "CL":
            pos_array[9] = 1
        elif item == "C":
            pos_array[10] = 1
        elif item == "CR":
            pos_array[11] = 1
        elif item == "RL":
            pos_array[12] = 1    
        elif item == "R":
            pos_array[13] = 1  
    
    return pos_array


# Replace 'file1.csv' and 'file2.csv' with your actual file names
match_path = 'Datasets/matches/epl_matches_20152016.csv'
team_path = 'Datasets/ratings/epl_ratings_20152016.csv'

home_team = 'AFC Bournemouth'
away_team = 'Aston Villa'


matching_rows, home_rows, away_rows = find_match_and_teams(match_path, team_path, home_team, away_team)

# Get match details and team formation details
away_formation, away_xi_names_array, away_sequence_array, away_xi_ID_array = find_team_formation_and_rating(matching_rows, "away")
home_formation, home_xi_names_array, home_sequence_array, home_xi_ID_array = find_team_formation_and_rating(matching_rows, "home")

# Get player team details by their grid row positions
away_atkKep_plyr_details, away_atkDefPos_plyr_details, away_atkMidPos_plyr_details, away_atkForPos_plyr_details = team_player_details(matching_rows,away_sequence_array, away_xi_ID_array, away_rows, "away")
print("away_atkKep_plyr_details: " + str(away_atkKep_plyr_details) + ", away_atkDefPos_plyr_details: " + str(away_atkDefPos_plyr_details) + ", away_atkMidPos_plyr_details: " + str(away_atkMidPos_plyr_details) + ", away_atkForPos_plyr_details: " + str(away_atkForPos_plyr_details) + ", away_defKepPos_plyr_details: ")
home_atkKep_plyr_details, home_atkDefPos_plyr_details, home_atkMidPos_plyr_details, home_atkForPos_plyr_details = team_player_details(matching_rows,home_sequence_array, home_xi_ID_array, home_rows, "home")
print("home_atkKep_plyr_details: " + str(home_atkKep_plyr_details) + ", home_atkDefPos_plyr_details: " + str(home_atkDefPos_plyr_details) + ", home_atkMidPos_plyr_details: " + str(home_atkMidPos_plyr_details) + ", home_atkForPos_plyr_details: " + str(home_atkForPos_plyr_details) + ", home_defKepPos_plyr_details: ")


# Define position grid and dynamic code for AWAY team
away_atkKepPos, away_AtkKep = cal_atk_def_KepPos_values(away_atkKep_plyr_details)
# TODO: [insert calcualtion for atkDefPos here]
away_atkMidPos, away_AtkMid = cal_atkMid_values(away_atkMidPos_plyr_details)
# TODO: [insert calculation for atkForPos here]
away_defKepPos, away_DefKep = cal_atk_def_KepPos_values(home_atkKep_plyr_details)


# Define position grid and dynamic code for HOME team
home_atkKepPos, home_AtkKep = away_defKepPos, away_DefKep
# TODO: insert calcualtion for atkDefPos HERE
home_atkMidPos, home_AtkMid = cal_atkMid_values(home_atkMidPos_plyr_details)
# TODO: insert calculation for atkForPos HERE
home_defKepPos, home_DefKep = away_atkKepPos, away_AtkKep


# Generate pcsp file (to be completed)
keeper_stats = find_away_keeper_stats(away_xi_names_array, away_xi_ID_array, away_rows)
generate_pcsp(keeper_stats, '2015-08-08', 'AFC Bournemouth', 'Aston Villa')






import pandas as pd
import sys

# Global variables for away atk forward players
position_mapping = {
    "L": 0 + 6,
    "LR": 1 + 6,
    "CL": 2 + 6,
    "C": 3 + 6,
    "CR": 4 + 6,
    "RL": 5 + 6,
    "R": 6 + 6
}
atkForPos = [-1] * 6 + [0, 1, 0, 1, 0, 1, 0] + [-1] * 6
AtkFor = ""

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

# finds the match and teams in the csv files
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

    # Get the match' home and away team formation
    home_sequence = matching_rows.iloc[0]['home_sequence']
    away_sequence = matching_rows.iloc[0]['away_sequence']

    return matching_rows, home_rows, away_rows, home_sequence, away_sequence

# returns the away formation, names and id
def find_away_formation_and_rating(matching_rows):
    # Find Away Formation
    away_formation = matching_rows.iloc[0]['away_formation']
    print("Away formation: " + away_formation)

    # Find Away Team Rating
    away_xi_names_array = matching_rows['away_xi_names'].iloc[0].split(',')
    away_xi_ID_array = matching_rows['away_xi_sofifa_ids'].iloc[0].split(',')

    # Convert the substrings to integers
    away_xi_ID_array = [i.split('.')[0] for i in away_xi_ID_array]

    return away_formation, away_xi_names_array, away_xi_ID_array

# returns the away formation, names and id
def find_home_formation_and_rating(matching_rows):
    # Find Away Formation
    home_formation = matching_rows.iloc[0]['home_formation']
    print("Home formation: " + home_formation)

    # Find Home Team Rating
    home_xi_names_array = matching_rows['home_xi_names'].iloc[0].split(',')
    home_xi_ID_array = matching_rows['home_xi_sofifa_ids'].iloc[0].split(',')

    # Convert the substrings to integers
    home_xi_ID_array = [i.split('.')[0] for i in home_xi_ID_array]

    return home_formation, home_xi_names_array, home_xi_ID_array

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

# do find_away_for_stats (return a dictionary that returns the pos and the stats)
def find_away_forward_stats(away_xi_names_array, away_xi_ID_array, away_rows, away_forward_formation, away_sequence, 
                            home_xi_ID_array, home_rows, home_def_formation, home_sequence):
    # Find Away Forward
    away_formation = int(away_forward_formation)
    away_forward_names = away_xi_names_array[-away_formation:]
    away_forward_ID = away_xi_ID_array[-away_formation:]
    away_forward_position = away_sequence.split(",")[-away_formation:]

    # Find Home Defenders
    home_formation = int(home_def_formation)
    home_forward_ID = home_xi_ID_array[1:home_formation+1]
    home_forward_position = home_sequence.split(",")[1:home_formation+1]

    # Dictionary to get current players positions and transform them into the opponents possible positions for penalties
    position_switch = {
        "L": ["RL", "R"],
        "LR": ["CR", "RL", "R"],
        "CL": ["C", "CR", "RL"],
        "C": ["CL", "C", "CR"],
        "CR": ["LR", "CL", "C"],
        "RL": ["L", "LR", "CL"],
        "R": ["L", "LR"],
    }

    # Iterate through each attacking forward player
    for name, ID, position in zip(away_forward_names, away_forward_ID, away_forward_position):
        # Declare AtkFor as a global variable
        global AtkFor
        print("Away Forward Name: " + name + ", ID: " + str(ID) + ", Position: " + position)

        # Convert the player's ID to an integer
        forward_id_int = int(ID)

        # Find the player's row in the DataFrame
        forward_row = away_rows[away_rows['sofifa_id'] == forward_id_int]

        # Obtain the player's AtkFor Rating attributes
        forward_atack_finish = forward_row.iloc[0]['attacking_finishing']
        forward_power_long_shots = forward_row.iloc[0]['power_long_shots']
        forward_attacking_volley = forward_row.iloc[0]['attacking_volleys']
        forward_attacking_heading_accuracy = forward_row.iloc[0]['attacking_heading_accuracy']
        
        # Calculations for probability of penalties
        positions_to_consider = position_switch.get(position)
        # print(positions_to_consider)
        opponent_df = pd.DataFrame()
        home_rows_df = pd.DataFrame()
        
        # Iterate through each home defending player
        for home_id, home_position in zip(home_forward_ID, home_forward_position):
            # Iterate through the positions to consider
            for home_position_to_consider in positions_to_consider:
                if (home_position == home_position_to_consider):
                    # Convert the player's ID to an integer
                    def_id_int = int(home_id)
                    # Find the player's row in the DataFrame
                    def_row = home_rows[home_rows['sofifa_id'] == def_id_int]
                    opponent_df = pd.concat([opponent_df, def_row], ignore_index=True)
            home_rows_df = pd.concat([home_rows_df, home_rows[home_rows['sofifa_id'] == int(home_id)]], ignore_index=True)
        # print(opponent_df)
        # losing ball: taking max of each of the 3 defending stats for the defending players and averaging them
        forward_probability_of_losing_ball = round((home_rows_df['defending_marking'].max() + home_rows_df['defending_standing_tackle'].max() + home_rows_df['defending_sliding_tackle'].max())/3)
        forward_probability_of_aggression = opponent_df['mentality_aggression'].max()
        forward_probability_of_mentality_penalties =  away_rows['mentality_penalties'].max() 
        forward_header = round(0.1 * forward_row.iloc[0]['power_jumping'] + 0.6 * forward_row.iloc[0]['attacking_heading_accuracy'] + 
                             0.3 * round((forward_row.iloc[0]['height_cm'] / max(away_rows['height_cm'].max(), home_rows['height_cm'].max())) * 100))
        forward_position = position

        # Calculate and print the AtkFor Rating for the current player
        atk_for_rating = f"[pos[{forward_position}] == 1]For({forward_atack_finish}, {forward_power_long_shots}, " \
             f"{forward_attacking_volley}, {forward_attacking_heading_accuracy}, {forward_probability_of_losing_ball}, " \
             f"{forward_probability_of_aggression}, {forward_probability_of_mentality_penalties}, " \
             f"{forward_header}, {forward_position})"
        
        # Append to the global AtkFor variable
        AtkFor += atk_for_rating + " [] "

        # Update the atkForPos array
        atkForPos[position_mapping.get(position)] = 1

    # Remove the last [] and add a semicolon
    AtkFor = AtkFor[:-4] + ";"
    print("AtkFor = ", AtkFor)
    print("atkForPos = ", atkForPos)





# Replace 'file1.csv' and 'file2.csv' with your actual file names
match_path = 'Datasets/matches/epl_matches_20152016.csv'
team_path = 'Datasets/ratings/epl_ratings_20152016.csv'

home_team = 'AFC Bournemouth'
away_team = 'Aston Villa'

matching_rows, home_rows, away_rows, home_sequence, away_sequence = find_match_and_teams(match_path, team_path, home_team, away_team)

away_formation, away_xi_names_array, away_xi_ID_array = find_away_formation_and_rating(matching_rows)
home_formation, home_xi_names_array, home_xi_ID_array = find_home_formation_and_rating(matching_rows)
away_formation_array = away_formation.split("-")
home_formation_array = home_formation.split("-")

keeper_stats = find_away_keeper_stats(away_xi_names_array, away_xi_ID_array, away_rows)

find_away_forward_stats(away_xi_names_array, away_xi_ID_array, away_rows, away_formation_array[-1], away_sequence, 
                        home_xi_ID_array, home_rows, home_formation_array[0], home_sequence)

generate_pcsp(keeper_stats, '2015-08-08', 'AFC Bournemouth', 'Aston Villa')






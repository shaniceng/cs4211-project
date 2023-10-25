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

# Replace 'file1.csv' and 'file2.csv' with your actual file names
match_path = 'Datasets/matches/epl_matches_20152016.csv'
team_path = 'Datasets/ratings/epl_ratings_20152016.csv'

home_team = 'AFC Bournemouth'
away_team = 'Aston Villa'

matching_rows, home_rows, away_rows = find_match_and_teams(match_path, team_path, home_team, away_team)

away_formation, away_xi_names_array, away_xi_ID_array = find_away_formation_and_rating(matching_rows)

keeper_stats = find_away_keeper_stats(away_xi_names_array, away_xi_ID_array, away_rows)

generate_pcsp(keeper_stats, '2015-08-08', 'AFC Bournemouth', 'Aston Villa')






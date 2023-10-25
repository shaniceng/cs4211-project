
generate_pcsp_for_match()


    find_match_and_teams(match_path, team_path, home_team, away_team)

    // Get info of match 
        - formation
        - Name
        - id 

    // Get info of team
        - all the player info in team 

    // Create dictionary for stat
    Example:
    4-3-3
    keeper: 1
    defender: 4
    midfielder: 3
    forward: 3

    Example:
    4-2-3-1
    keeper: 1
    defender: 4
    midfielder: 5
    forward: 1
    output: dictionary


    // Get player position
    output: Array
    Example: atkKepPos = [-1(6), 0, 0, 0, 1, 0, 0, 0, -1(6)] (For Def Mid For)



// Dynamic code (append)
input:
dictionary - data
Array - grid 
- dynamic macro
- dynamic grid
- dynamic attack and home team 


// Able to read multiple match
read_multiple_match(match_path, team_path) {

    generate_pcsp_for_match()
}
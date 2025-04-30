import const
import os
import pandas as pd



def get_zone_and_type(x, y, subEvent):
    # Check if the event is not in the field area
    if (x == 0 or y == 0 or x == 100 or y == 100) or subEvent == 'Ball out of the field':
        return const.OUT.capitalize(), ''
    
    if x < 50:
        zone = const.LEFT
    else:
        zone = const.RIGHT
    
    if (x < 12 or x > 88) and (30 < y < 60):
        area_type = const.AREA.get(const.GOALKEEPER)
    elif 25 <= x <= 75:
        area_type = const.AREA.get(const.MIDFIELD)
    else:
        area_type = const.AREA.get(const.DEFENSE)
    
    return area_type, zone


def process_area(data: pd.DataFrame, league: str):

    
    reference_teams = data.groupby('matchId').first().reset_index()[['matchId', 'teamId']]
    reference_teams = reference_teams.rename(columns={'teamId': 'referenceTeamId'})

    # Merge reference team info into original dataframe
    df = data.merge(reference_teams, on='matchId', how='left')
    
    def normalize_coordinates(row):
        if row['teamId'] != row['referenceTeamId']:
            row['pos_orig_x'] = 100 - row['pos_orig_x']
            row['pos_orig_y'] = 100 - row['pos_orig_y']
        return row

    data = df.apply(normalize_coordinates, axis=1)
    
    data = df.drop(columns=['referenceTeamId'])


    data[['type_orig', 'zone_orig']] = data.apply(
        lambda row: pd.Series(get_zone_and_type(row['pos_orig_x'], row['pos_orig_y'], row['subEventName'])), axis=1
    )

    data['pos_orig'] = data['type_orig'] + '-' + data['zone_orig']
    data.loc[data['type_orig'] == const.OUT.capitalize(), 'pos_orig'] = const.OUT

        
    area_df = pd.concat([
        data[['pos_orig', 'type_orig', 'zone_orig']].rename(columns={
            'pos_orig': 'id', 'type_orig': 'area', 'zone_orig': 'zone'
        }),
    ]).drop_duplicates(subset='id').reset_index(drop=True)

    area_file_path = os.path.join(os.getcwd(), 'ekg_data', league, 'entities', f'position_{league}.csv')
    os.makedirs(os.path.dirname(area_file_path), exist_ok=True)
    area_df.to_csv(area_file_path, index=False)
    
    data = data.drop(columns=['type_orig','zone_orig'])
    data = data.drop(columns=['pos_orig_y','pos_orig_x','pos_dest_y','pos_dest_x',])
    
    output_file = os.path.join(os.getcwd(), 'ekg_data', league, f'events_{league}_with_position.csv')
    data.to_csv(output_file, index=False)
    print(f'Successfully stored areas for {league}')


if __name__ == "__main__":
    for league in const.LEAGUE_LIST:
        file_path = os.path.join(os.getcwd(), 'ekg_data', f'{league}', f'events_{league}.csv')
        data = pd.read_csv(file_path)
        process_area(data,league)
    print('Successfully processed event areas')
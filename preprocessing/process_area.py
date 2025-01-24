import const
import os
import pandas as pd



def get_zone_and_type(x, y):
    if x < 50:
        zone = const.ZONE.get(const.DEFEND)
    else:
        zone = const.ZONE.get(const.ATTACK)
    
    if (x < 12 or x > 88) and (30 < y < 60):
        area_type = const.AREA.get(const.GOALKEEPER)
    elif 25 <= x <= 75:
        area_type = const.AREA.get(const.MIDFIELD)
    else:
        area_type = const.AREA.get(const.DEFENSE)
    
    return area_type, zone


def process_area(data: pd.DataFrame, league: str):
    data[['type_orig', 'zone_orig']] = data.apply(
        lambda row: pd.Series(get_zone_and_type(row['pos_orig_x'], row['pos_orig_y'])), axis=1
    )
    data[['type_dest', 'zone_dest']] = data.apply(
        lambda row: pd.Series(get_zone_and_type(row['pos_dest_x'], row['pos_dest_y'])), axis=1
    )

    data['pos_orig'] = data['type_orig'].str[0] + 'a-' + data['zone_orig'].astype(str).str[0] + 'z'
    data['pos_dest'] = data['type_dest'].str[0] + 'a-' + data['zone_dest'].astype(str).str[0] + 'z'

    area_df = pd.concat([
        data[['pos_orig', 'type_orig', 'zone_orig']].rename(columns={
            'pos_orig': 'id', 'type_orig': 'type', 'zone_orig': 'zone'
        }),
        data[['pos_dest', 'type_dest', 'zone_dest']].rename(columns={
            'pos_dest': 'id', 'type_dest': 'type', 'zone_dest': 'zone'
        })
    ]).drop_duplicates(subset='id').reset_index(drop=True)

    area_file_path = os.path.join(os.getcwd(), 'ekg_data', league, 'entities', f'areas_{league}.csv')
    os.makedirs(os.path.dirname(area_file_path), exist_ok=True)
    area_df.to_csv(area_file_path, index=False)
    
    data = data.drop(columns=['type_orig','zone_orig','type_dest','zone_dest'])

    output_file = os.path.join(os.getcwd(), 'ekg_data', league, f'events_{league}_with_area.csv')
    data.to_csv(output_file, index=False)
    print(f'Successfully stored areas for {league}')


if __name__ == "__main__":
    for league in const.LEAGUE_LIST:
        file_path = os.path.join(os.getcwd(), 'ekg_data', f'{league}', f'events_{league}.csv')
        data = pd.read_csv(file_path)
        process_area(data,league)
    print('Successfully processed event areas')
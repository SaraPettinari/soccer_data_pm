import const
import os
import pandas as pd



def get_zone_and_type(x, y):
    if x < 50:
        zone = 'Defend_Zone'
    else:
        zone = 'Attack_Zone'
    
    if (x < 12) and (30 < y < 60):
        area_type = 'Goalkeeper_Area'
    elif x >= 50:
        area_type = 'Midfield'
    else:
        area_type = 'Defense_Area'
    
    return area_type, zone


def process_area(data,league):
    type_orig = []
    zone_orig = []
    type_dest = []
    zone_dest = []

    for _, row in data.iterrows():
        # Origin type and zone
        type_o, zone_o = get_zone_and_type(row['pos_orig_x'], row['pos_orig_y'])
        type_orig.append(type_o)
        zone_orig.append(zone_o)
        
        # Destination type and zone
        type_d, zone_d = get_zone_and_type(row['pos_dest_x'], row['pos_dest_y'])
        type_dest.append(type_d)
        zone_dest.append(zone_d)

    data['type_orig'] = type_orig
    data['zone_orig'] = zone_orig
    data['type_dest'] = type_dest
    data['zone_dest'] = zone_dest
    
    

    output_file = os.path.join(os.getcwd(), 'ekg_data', f'{league}', f'events_{league}_with_area.csv')
    data.to_csv(output_file, index=False)


if __name__ == "__main__":
    for league in const.LEAGUE_LIST:
        file_path = os.path.join(os.getcwd(), 'ekg_data', f'{league}', f'events_{league}.csv')
        data = pd.read_csv(file_path)
        process_area(data,league)
    print('Successfully processed event areas')
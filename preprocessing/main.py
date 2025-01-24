import const
import os
from process_datetime import assign_datetime
from clear_data import clean_events


if __name__ == "__main__":
    for league in const.LEAGUE_LIST:
        events_file = os.path.join(const.DATA_PATH, f'events_{league}.csv')
        matches_file = os.path.join(const.DATA_PATH, f'matches_{league}.csv') 
        out_file = os.path.join(os.getcwd(), 'out', f'events_with_datetime_{league}.csv')
        
        assign_datetime(events_file, matches_file, out_file)
        clean_events()
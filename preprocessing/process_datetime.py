import const
import os
import pandas as pd
from datetime import timedelta


def assign_datetime(events_file, matches_file, out_file):

    events_df = pd.read_csv(events_file)
    matches_df = pd.read_csv(matches_file)

    # Convert match date to datetime format
    matches_df['dateutc'] = pd.to_datetime(matches_df['dateutc'])

    match_datetime_dict = matches_df.set_index('wyId')['dateutc'].to_dict()

    # Calculate event datetime
    def calculate_event_datetime(row):
        global last_match_period, last_event_time, ref_datetime
        event_datetime = None
        match_datetime = match_datetime_dict.get(row['matchId'])
        
        if match_datetime:
            match_period = row['matchPeriod']
            if match_period == '1H':
                event_datetime = match_datetime + timedelta(seconds=row['eventSec'])
            elif match_period == '2H':
                if last_match_period != match_period:
                    ref_datetime = last_event_time + timedelta(minutes=15)    # Add interval time
                    event_datetime = ref_datetime + timedelta(seconds=row['eventSec'])   
                else:
                    event_datetime = ref_datetime + timedelta(seconds=row['eventSec'])
            
            last_match_period = match_period
            last_event_time = event_datetime
            
        return event_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] if event_datetime else None #Format compatible with memgraph

    last_match_period = ''
    last_event_time = None
    ref_datetime = None

    # Apply the function to calculate event datetime
    events_df['eventDatetime'] = events_df.apply(calculate_event_datetime, axis=1)

    # Save file
    events_df.to_csv(out_file, index=False)

    print(f"Updated events file with eventDatetime saved to {out_file}")


if __name__ == "__main__":
    for league in const.LEAGUE_LIST:
        # Load the CSV files
        a = const.DATA_PATH
        events_file = os.path.join(const.DATA_PATH, f'events_{league}.csv')
        matches_file = os.path.join(const.DATA_PATH, f'matches_{league}.csv') 
        out_file = os.path.join(os.getcwd(), 'out', f'events_with_datetime_{league}.csv')
        
        print()

        assign_datetime(events_file, matches_file, out_file)
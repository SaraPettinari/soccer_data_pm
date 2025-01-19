import const
import os 
import pandas as pd
  
  
out_dir = os.path.join(os.getcwd(), 'ekg_data')
league_list = ['England', 'France', 'Germany', 'Italy', 'Spain', 'European_Championship','World_Cup']

in_dir = os.path.join(os.getcwd(), 'out')

tags_file = os.path.join(const.DATA_PATH, 'tags2name.csv')
tags_df = pd.read_csv(tags_file)

def clean_events():
    for league in league_list:
        league_dir = os.path.join(out_dir, league)

        if not os.path.isdir(league_dir): 
            os.makedirs(league_dir) 
            
        out_file = os.path.join(league_dir, f'events_{league}.csv')
            
        events_file = os.path.join(in_dir, f'events_with_datetime_{league}.csv')
        events_df = pd.read_csv(events_file)
        
        # remove unwanted cols
        events_df = events_df.drop(columns=['eventId', 'tags', 'positions', 'eventSec', 'subEventId']) 

        events_df['tagsList'] = events_df['tagsList'].str.replace(r'["\[\]]', '', regex=True)

        tag_mapping = dict(zip(tags_df['Tag'].astype(str), tags_df['Label']))

        # Replace tags with labels
        def replace_tags(tag_list):
            if pd.isnull(tag_list):  # handle null values
                return []
            tags = tag_list.split()
            return [tag_mapping[tag] for tag in tags if tag in tag_mapping]

        events_df['tagsList'] = events_df['tagsList'].apply(replace_tags)
        
        
        events_df.to_csv(out_file, index=False)

        print(f"Updated events file with eventDatetime saved to {out_file}")
   
   
if __name__ == "__main__": 
    clean_events()
        
import const
import os 
import pandas as pd
import ast
  
out_dir = os.path.join(os.getcwd(), 'ekg_data')
league_list = ['England', 'France', 'Germany', 'Italy', 'Spain', 'European_Championship','World_Cup']

in_dir = os.path.join(os.getcwd(), 'out')

tags_file = os.path.join(const.DATA_PATH, 'tags2name.csv')
tags_df = pd.read_csv(tags_file)

def clean_events():
    for league in const.LEAGUE_LIST:
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
   
 
def clean_entities(league, ent_list):
    events_dir = os.path.join(out_dir, league, f'events_{league}.csv')
    events_df = pd.read_csv(events_dir)
    
    for ent in ent_list:
        ent_dir = os.path.join(out_dir, league, 'entities')

        if not os.path.isdir(ent_dir): 
            os.makedirs(ent_dir)
             
        if 'teams' in ent:
            ref_file = os.path.join(const.DATA_PATH, f'{ent}.csv')
            ent_df = pd.read_csv(ref_file)
            ent_df = ent_df.drop(columns=['officialName','type'])
            ent_df['area'] = ent_df['area'].apply(lambda x: ast.literal_eval(x)['name'])
            ent_df.rename(columns={'area': 'country'}, inplace=True)

            # if wyId is in teamId of df events
            filtered_teams = ent_df[ent_df['wyId'].isin(events_df['teamId'])].copy()
            
            filtered_teams.to_csv(os.path.join(ent_dir, f'{ent}_{league}.csv'), index=False)

        elif 'players' in ent:
            ref_file = os.path.join(const.DATA_PATH, f'{ent}.csv')
            ent_df = pd.read_csv(ref_file)
            ent_df = ent_df.drop(columns=['passportArea','weight','firstName','middleName','lastName',
                                          'height','birthArea','foot'])
            ent_df['role'] = ent_df['role'].apply(lambda x: ast.literal_eval(x)['code3'])
            
            # if wyId is in playerId of df events
            filtered_players = ent_df[ent_df['wyId'].isin(events_df['playerId'])].copy()
            
            #cast from float and fill NaN values with -1
            filtered_players['currentNationalTeamId'] = filtered_players['currentNationalTeamId'].fillna(-1).astype(int)
            filtered_players['currentTeamId'] = filtered_players['currentTeamId'].fillna(-1).astype(int)

            filtered_players.to_csv(os.path.join(ent_dir, f'{ent}_{league}.csv'), index=False)

        elif 'matches' in ent:
            ref_file = os.path.join(const.DATA_PATH, f'{ent}.csv')
            ent_df = pd.read_csv(ref_file)
            ent_df = ent_df.drop(columns=['roundId','teamsData','date','referees','team1.scoreET','team1.coachId','team1.scoreP','team1.hasFormation','team1.formation','team1.scoreHT','team1.formation.bench',
                                          'team1.formation.lineup','team1.formation.substitutions','team2.scoreET','team2.coachId','team2.scoreP','team2.hasFormation','team2.formation','team2.scoreHT',
                                          'team2.formation.bench','team2.formation.lineup','team2.formation.substitutions'])
            ent_df.to_csv(os.path.join(ent_dir, f'matches_{league}.csv'), index=False)
    
    print(f'Entities file created for {league}')        
   
if __name__ == "__main__": 
    for league in const.LEAGUE_LIST:
        ent_list = ['teams', 'players', f'matches_{league}']
        clean_entities(league, ent_list)  
    #clean_events()
        
import os 


DATA_PATH = os.path.join(os.getcwd(), 'soccer_data')
LEAGUE_LIST = ['England', 'France', 'Germany', 'Italy', 'Spain', 'European_Championship','World_Cup']

DEFEND = 'defend'
ATTACK = 'attack'
ZONE = {DEFEND: 'Defend_Zone', ATTACK: 'Attack_Zone'}

GOALKEEPER = 'goal'
MIDFIELD = 'mid'
DEFENSE = 'def'
OUT = 'Out'
AREA = {GOALKEEPER: 'GK', MIDFIELD: 'Mid', DEFENSE: 'Def'}
LEFT = 'LEFT'
RIGHT = 'RIGHT'

ENTITY = 'ent'
FOLDERS = {ENTITY: 'entities'}
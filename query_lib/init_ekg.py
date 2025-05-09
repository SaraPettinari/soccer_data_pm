import const as cn

def load_query_generator(node_type, path : str, log_name: str, header_data : list, type = None) -> str:
    data_list = ''
    for data in header_data:
        if 'time' in data:
            data_list += ', {}: datetime(line.{})'.format(
                data,data)
        else:
            data_list += ', {}: line.{}'.format(data, data)
    
    if type:
        data_list += f', {cn.ENTITY_TYPE_TAG}: "{type}"'

    load_query = f'LOAD CSV WITH HEADERS FROM "file:///{path}" as line CREATE (e:{node_type} {{Log: "{log_name}" {data_list} }})'

    data = data_list.split(', ')
    data.pop(0)  # the first occurrence is empty
    data_dict = {}
    for el in data:
        res = el.split(': ')
        data_dict[res[0]] = res[1]

    return load_query

def infer_corr_query(entity : str) -> str:
    return(f"""
        MATCH (e:Event)
        WHERE e.{entity} IS NOT NULL AND e.{entity} <> "null"
        WITH split(e.{entity}, ',') AS items, e
        UNWIND items AS entity_id
        WITH entity_id, e
        MATCH (t:Entity {{{cn.ENTITY_ID}: entity_id}})
        MERGE (e)-[:CORR {{{cn.ENTITY_TYPE_TAG}: '{entity}'}}]->(t)
    """)

def create_entity_index_query() -> str:
    return(f"""
        CREATE INDEX FOR (t:Entity) ON (t.{cn.ENTITY_ID})
        CREATE INDEX FOR (t:Entity) ON (t.{cn.ENTITY_TYPE_TAG})
    """)

def infer_df_query(entity : str) -> str:
    return(f"""
        MATCH (n:Entity {{{cn.ENTITY_TYPE_TAG}: '{entity}'}})<-[:CORR]-(e)
        WITH n, e AS nodes ORDER BY e.eventDatetime, ID(e)
        WITH n, collect(nodes) AS event_node_list
        UNWIND range(0, size(event_node_list)-2) AS i
        WITH n, event_node_list[i] AS e1, event_node_list[i+1] AS e2
        MERGE (e1)-[df:DF {{Type:n.{cn.ENTITY_TYPE_TAG}, ID:n.{cn.ENTITY_ID}, edge_weight: 1}}]->(e2)
        """)
    
def all_load() -> str:
    event_load = load_query_generator('Event', '/Users/sara/Documents/Repo/soccer-data/ekg_data/Italy/events_Italy_with_position.csv', log_name, ['id', 'eventDatetime', 'eventName', 'playerId', 'matchId', 'teamId', 'pos_orig'])
    print('Event Query LOAD:\n', event_load)
    entity_player_load = load_query_generator('Entity', '/Users/sara/Documents/Repo/soccer-data/ekg_data/Italy/entities/players_Italy.csv', log_name, ['currentTeamId','birthDate','role','wyId','shortName','currentNationalTeamId'], type='playerId')
    print('Player Query LOAD:\n', entity_player_load)
    entity_team_load = load_query_generator('Entity', '/Users/sara/Documents/Repo/soccer-data/ekg_data/Italy/entities/teams_Italy.csv', log_name, ['city','name','wyId'], type='teamId')
    print('Team Query LOAD:\n', entity_team_load)
    entity_position_load = load_query_generator('Entity', '/Users/sara/Documents/Repo/soccer-data/ekg_data/Italy/entities/position_Italy.csv', log_name, ['wyId','area','zone'], type='pos_orig')
    print('Position Query LOAD:\n', entity_position_load)

if __name__ == "__main__":
    log_name = "soccer_italy_log"
    ## Load Queries
    all_load()
    ## Index Query
    print('Create Index Query:\n', create_entity_index_query())
    ## :CORR Query
    entities = ['playerId', 'teamId', 'pos_orig']
    for entity in entities:
        print(f'Correlation Query for {entity}:\n', infer_corr_query(entity))
        print(f'DF Query for {entity}:\n', infer_df_query(entity))
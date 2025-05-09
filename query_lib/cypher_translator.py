from grammar import *
import const as cn

def translate_aggr_function(attr: str, func: AggregationFunction):
    '''Translate aggregation functions to Neo4j Cypher syntax'''
    if func == AggregationFunction.SUM:
        return f"sum({attr})"
    elif func == AggregationFunction.AVG:
        return f"avg({attr})"
    elif func == AggregationFunction.MIN:
        return f"min({attr})"
    elif func == AggregationFunction.MAX:
        return f"max({attr})"
    elif AggregationFunction.MINMAX:
        return [f"min({attr})",f"max({attr})"]
    elif AggregationFunction.MULTISET: # TODO
        return f"({attr})"
    else:
        raise ValueError(f"Unsupported function: {func}")


def generate_cypher_from_step(step: AggrStep) -> str:
    '''Convert an aggregation step to a Cypher query'''
    node_type = "Event" if step.aggr_type == "EVENTS" else "Entity"
    match_clause = f"MATCH (n:{node_type})"
    
    of_clause = f"WHERE n.Type = '{step.ent_type}'" if step.ent_type else ""
    
    where_clause = f"WHERE {step.where}" if step.where else ""
    
    class_query = aggregate_nodes(step.aggr_type.capitalize(), step.group_by, step.attr_aggrs)
    
    aggr_parts = []
    for attr_aggr in step.attr_aggrs:
        aggr_parts.extend(translate_aggr_function(attr_aggr.name, attr_aggr.function))
                
    clauses = [match_clause, of_clause, where_clause, class_query]
    cypher_query = "\n".join(clause for clause in clauses if clause)
    return cypher_query.strip()


def aggregate_nodes(node_type: str, group_by: List[str], attr_aggrs: List[str]) -> str:
    '''
    Cypher query construction for _nodes_ aggregation
    '''
    aliased_attrs = [f"n.{attr} AS {attr}" for attr in group_by]
    group_keys_clause = "WITH DISTINCT n, " + ", ".join(aliased_attrs)

    # Build a value based on distinct values of the group_by attributes
    val_expr = ' + "_" + '.join(group_by) # will be used to create a unique value for the node
    agg_type = "_".join(group_by) # will be used to create a type for the node
    new_val = ', '.join(group_by) + f", {val_expr} AS val"
    
    aggr_expressions = []
    merge_props = [] 

    if attr_aggrs:
        for attr_aggr in attr_aggrs:
            group_keys_clause += f", n.{attr_aggr.name} AS {attr_aggr.name}"
            exprs = translate_aggr_function(attr_aggr.name, attr_aggr.function)

            # Handle both lists and strings
            if isinstance(exprs, list):
                expr = f"[{', '.join(exprs)}] AS {attr_aggr.name}"
                aggr_expressions.append(expr)
                merge_props.append(f"{attr_aggr.name.capitalize()}: {attr_aggr.name}")
            else:
                expr = f"{exprs} AS {attr_aggr.name}"
                aggr_expressions.append(expr)
                merge_props.append(f"{attr_aggr.name.capitalize()}: {attr_aggr.name}")

    # add values aggregations in WITH clause
    if aggr_expressions:
        with_aggr = (
            f"WITH {new_val}, " + ", ".join(aggr_expressions)
        )
    else:
        with_aggr = ''

    # Small issue: I used CREATE since MERGE would loop infinitely 
    '''
    merge_clause = (
        f'CREATE (c:Class {{ Name: val, Type: "{node_type}", ID: val, Agg: "{agg_type}"'
    )
    if merge_props:
        merge_clause += ", " + ", ".join(merge_props)
    merge_clause += " })"
    '''
    
    merge_clause = (
        f'CREATE (c:Class {{ Name: val, Type: "{node_type}", ID: val, Agg: "{agg_type}"'
        + (", " + ", ".join(merge_props) if merge_props else "")
        + " })"
    )

        
    obs_clause = 'WITH n,c \nMERGE (n)-[:OBS]->(c)'

    # Build the query
    cypher_query_parts = [group_keys_clause, with_aggr, merge_clause]

    # Conditionally add the match_event if aggr_expressions exist
    if aggr_expressions:
        prop_val = ", ".join(f"{attr} : {attr}" for attr in group_by)
        vars = ', '.join(group_by)
        cypher_query_parts.append(f"WITH c, {vars}")
        cypher_query_parts.append(f"MATCH (n:Event {{{prop_val}}})")

    # Add the obs_clause at the end
    cypher_query_parts.append(obs_clause)

    # Join all 
    cypher_query = "\n".join(cypher_query_parts)

    return cypher_query


def generate_df_c_query():
    return '''
        MATCH ( c1 : Class ) <-[:OBS]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBS]-> ( c2 : Class )
        MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
        WHERE c1.Type = c2.Type AND n.Type = df.Type
        WITH n.Type as EType,c1,count(df) AS df_freq,c2
        MERGE ( c1 ) -[rel2:DF_C {EntityType:EType}]-> ( c2 ) 
        ON CREATE SET rel2.count=df_freq
        '''

def generate_corr_c_query():
    return '''
        MATCH ( c1 : Class ) <-[:OBS]- ( e1 : Event ) -[df:DF]-> ( e2 : Event ) -[:OBS]-> ( c2 : Class )
        MATCH (e1) -[:CORR] -> (n) <-[:CORR]- (e2)
        WHERE c1.Type = c2.Type AND n.Type = df.Type
        WITH n.Type as EType,c1,count(df) AS df_freq,c2
        MERGE ( c1 ) -[rel2:DF_C {EntityType:EType}]-> ( c2 ) 
        ON CREATE SET rel2.count=df_freq
        '''

def finalize_c_query():
    f'''
    MATCH (n:Event)
    WHERE  NOT EXISTS((n)-[:OBS]->())
    WITH n
    CREATE (c:Class {{ Name: n.{cn.EVENT_ACTIVITY}, Type: 'Event', ID: n.{cn.EVENT_ID}, Agg: "singleton"}})
    WITH n,c
    MERGE (n)-[:OBS]->(c)
    '''
    
    f'''
    MATCH (n:Entity)
    WHERE  NOT EXISTS((n)-[:OBS]->())
    WITH n
    CREATE (c:Class {{ Name: n.{cn.ENTITY_ID}, Type: 'Entity', ID: n.{cn.ENTITY_ID}, Agg: "singleton"}})
    WITH n,c
    MERGE (n)-[:OBS]->(c)
    '''

def generate_full_cypher(aggr_spec: AggrSpecification) -> str:
    return "\n\nUNION\n\n".join(generate_cypher_from_step(step) for step in aggr_spec.steps)


if __name__ == "__main__":
    # Example 
    step1 = AggrStep(aggr_type="ENTITIES", ent_type= "teamId", group_by=["country"], where=None, attr_aggrs=[])
    step2 = AggrStep(aggr_type="ENTITIES", ent_type= "playerId", group_by=["role"], where=None, attr_aggrs=[])
    step3 = AggrStep(aggr_type="EVENTS", ent_type= None, where=None, group_by=[cn.EVENT_ACTIVITY,"teamId","playerId"], 
                     attr_aggrs=[AttrAggr(name=cn.EVENT_TIMESTAMP, function=AggregationFunction.MINMAX)])
    
    aggr_spec = AggrSpecification(steps=[step1, step2,step3])
    
    cypher_query = generate_full_cypher(aggr_spec)
    print(cypher_query)
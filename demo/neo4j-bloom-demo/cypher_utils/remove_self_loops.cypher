MATCH (a:Person)-[rel:IS_RELATED_TO]->(a) 
DELETE rel;
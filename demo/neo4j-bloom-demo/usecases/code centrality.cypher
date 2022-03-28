// Reset node degree property
match (N) 
REMOVE N.code_centrality 
WITH count(*) as dummy
// Create a named graph for this task
CALL gds.graph.create('mygraph', ['ClassNode'], ['TOTAL_DEP_SUMMARY']) YIELD  graphName AS graph
WITH count(*) as dummy
// Compute and write centrality
CALL gds.pageRank.stream('mygraph')
YIELD nodeId, score
SET gds.util.asNode(nodeId).code_centrality = score
WITH count(*) as dummy
CALL gds.graph.drop('mygraph', false) YIELD graphName
WITH count(*) as dummy
MATCH (n) WHERE n.code_centrality IS NOT NULL AND n.code_centrality > 0.0 
WITH n, max(n.code_centrality) as MAXCENTRALITY
MATCH (m) WHERE m.code_centrality IS NOT NULL AND m.code_centrality > 0.0 AND m.code_centrality < MAXCENTRALITY
WITH m,n
MATCH p=(m)-[r:TOTAL_DEP_SUMMARY]-(n)
RETURN p ORDER BY n.code_centrality LIMIT 100
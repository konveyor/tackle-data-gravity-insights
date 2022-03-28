// Reset node degree property
match (N) 
REMOVE N.data_centrality 
WITH count(*) as dummy
// Create a named graph for this task
CALL gds.graph.create('mygraph', ['ClassNode', 'SQLTable'], ['TRANSACTION_READ', 'TRANSACTION_WRITE']) YIELD  graphName AS graph
WITH count(*) as dummy
// Compute and write centrality
CALL gds.degree.stream('mygraph')
YIELD nodeId, score
SET gds.util.asNode(nodeId).data_centrality = score
WITH count(*) as dummy
CALL gds.graph.drop('mygraph', false) YIELD graphName
WITH count(*) as dummy
MATCH (n) WHERE n.data_centrality IS NOT NULL AND n.data_centrality > 0.0 
WITH n, max(n.data_centrality) as MAXCENTRALITY
MATCH (m) WHERE m.data_centrality IS NOT NULL AND m.data_centrality > 0.0 AND m.data_centrality < MAXCENTRALITY
WITH m,n
MATCH p=(m)-[r]-(n)
RETURN p ORDER BY n.data_centrality
match (n:ClassNode)
with n
match (m:ClassNode)
with m,n
match p=(m)-[r]-(n)
with m, n, count(p) as rel_count
create (m)-[r:TOTAL_DEP_SUMMARY {total_rel: rel_count}]->(n)
WITH count(*) as dummy
match (n:ClassNode)
with n
match (m:ClassNode)
with m,n
match p=(m)-[r:HEAP_DEPENDENCY]-(n)
with m, n, count(p) as rel_count
create (m)-[r:HEAP_DEP_SUMMARY {total_rel: rel_count}]->(n)
WITH count(*) as dummy
match (n:ClassNode)
with n
match (m:ClassNode)
with m,n
match p=(m)-[r:DATA_DEPENDENCY]-(n)
with m, n, count(p) as rel_count
create (m)-[r:DATA_DEP_SUMMARY {total_rel: rel_count}]->(n)
WITH count(*) as dummy
match (n:ClassNode)
with n
match (m:ClassNode)
with m,n
match p=(m)-[r:CALL_RETURN_DEPENDENCY]-(n)
with m, n, count(p) as rel_count
create (m)-[r:CALL_RET_SUMMARY {total_rel: rel_count}]->(n)
return type(r)
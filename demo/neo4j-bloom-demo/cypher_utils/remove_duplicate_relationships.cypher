match ()-[r]->() 
match (s)-[r]->(e) 
with s,e,type(r) as typ, tail(collect(r)) as coll 
foreach(x in coll | delete x)
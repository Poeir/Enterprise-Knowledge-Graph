MATCH (a)-[r:HAS_SKILL]->(b)
RETURN a, r, b

MATCH (a:employee)-[r:HAS_SKILL]->(b:skill)
RETURN a, r, b

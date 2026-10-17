from rdflib import Graph

# Read the generated N-Triples file
graph = Graph()
graph.parse("rdf/knowledge-graph.nt", format="nt")

# Convert to Turtle
graph.serialize(
    destination="rdf/knowledge-graph.ttl",
    format="turtle"
)

print(f"Converted {len(graph)} triples to Turtle.")
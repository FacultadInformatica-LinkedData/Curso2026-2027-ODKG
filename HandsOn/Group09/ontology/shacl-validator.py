from pathlib import Path
from pyshacl import validate
from rdflib import Graph

BASE_DIR = Path(__file__).resolve().parent

data_graph = Graph()
data_graph.parse(BASE_DIR / 'ParkingMadrid-example.ttl', format='turtle')

shapes_graph = Graph()
shapes_graph.parse(BASE_DIR / 'ParkingMadrid-shapes.ttl', format='turtle')

ontology_graph = Graph()
ontology_graph.parse(BASE_DIR / 'ParkingMadrid.ttl', format='turtle')

conforms, report_graph, report_text = validate(
    data_graph,
    shacl_graph    = shapes_graph,
    ont_graph      = ontology_graph,
    inference      = 'rdfs',
    abort_on_first = False,
)

print(report_text)
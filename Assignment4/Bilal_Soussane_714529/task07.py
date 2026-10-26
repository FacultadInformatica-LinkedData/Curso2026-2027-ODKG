# Task 07: Querying RDF(s)

# !pip install rdflib
# !pip install oeg-sw-class

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report

github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG/master/Assignment4/course_materials"

# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage + "/rdf/data07.ttl", format="TTL")
report = Report()

ontology = Namespace("http://oeg.fi.upm.es/def/people#")

# Task 7.1a: (class, superclass) pairs with RDFLib
result = []
for c in g.subjects(RDF.type, RDFS.Class):
    sc = g.value(c, RDFS.subClassOf)
    result.append((c, sc))

report.validate_07_1a(result)

# Task 7.1b: same in SPARQL
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?c ?sc
WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
}
"""

report.validate_07_1b(query, g)

# Task 7.2a: individuals of Person and its subclasses with RDFLib
individuals = []
for c in g.transitive_subjects(RDFS.subClassOf, ontology.Person):
    for i in g.subjects(RDF.type, c):
        individuals.append(i)

report.validate_07_02a(individuals)

# Task 7.2b: same in SPARQL
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?ind
WHERE {
  ?ind a ?c .
  ?c rdfs:subClassOf* ontology:Person .
}
"""

report.validate_07_02b(g, query)

# Task 7.3: name and type of those who know Curry
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>
SELECT ?name ?type
WHERE {
  ?x ontology:knows ontology:Curry .
  ?x rdfs:label ?name .
  ?x a ?type .
}
"""

report.validate_07_03(g, query)

# Task 7.4: names of those with a colleague (or a colleague's colleague) who owns a pet
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ontology: <http://oeg.fi.upm.es/def/people#>
SELECT DISTINCT ?name
WHERE {
  ?x rdfs:label ?name .
  {
    ?x ontology:hasColleague ?c1 .
    ?c1 ontology:ownsPet ?pet .
  }
  UNION
  {
    ?x ontology:hasColleague ?c1 .
    ?c1 ontology:hasColleague ?c2 .
    ?c2 ontology:ownsPet ?pet .
  }
}
"""

report.validate_07_04(g, query)

report.save_report("_Task_07")

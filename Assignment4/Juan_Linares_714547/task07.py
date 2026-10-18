# -*- coding: utf-8 -*-
"""Task07_mandatory.ipynb

**Task 07: Querying RDF(s)**
"""

# !pip install rdflib
# !pip install oeg-sw-class
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG/master/Assignment4/course_materials"

"""Spanish: Primero leemos los ficheros RDF

English: First let's read the RDF file
"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data07.ttl", format="TTL")
report = Report()

"""**TASK 7.1a:**

English: For all classes, list each classURI. If the class belogs to another class, then list its superclass. Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass
"""

result = [] #list of tuples
for c in g.subjects(RDF.type, RDFS.Class):
  superclasses = list(g.objects(c, RDFS.subClassOf))
  if superclasses:
    for sc in superclasses:
      result.append((c, sc))
  else:
    result.append((c, None))

# Visualize the results
for r in result:
  print(r)

## Validation: Do not remove
report.validate_07_1a(result)

"""**TASK 7.1b:**

English: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)
"""

query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?c ?sc WHERE {
  ?c a rdfs:Class .
  OPTIONAL { ?c rdfs:subClassOf ?sc . }
}
"""

for r in g.query(query):
  print(r.c, r.sc)

## Validation: Do not remove
report.validate_07_1b(query,g)

"""**TASK 7.2a:**

English: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"
"""

ns = Namespace("http://oeg.fi.upm.es/def/people#")

# variable to return
individuals = []
# transitive_subjects includes ns.Person itself
for c in g.transitive_subjects(RDFS.subClassOf, ns.Person):
  for ind in g.subjects(RDF.type, c):
    if ind not in individuals:
      individuals.append(ind)

# visualize results
for i in individuals:
  print(i)

# validation. Do not remove
report.validate_07_02a(individuals)

"""**TASK 7.2b:**

English: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind
"""

query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?ind WHERE {
  ?class rdfs:subClassOf* ns:Person .
  ?ind a ?class .
}
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results

## Validation: Do not remove
report.validate_07_02b(g, query)

"""**TASK 7.3:**

English: List the name and type of those who know Curry (in SPARQL only). Use name and type as variables in the query
"""

query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?type WHERE {
  ?person ns:knows ns:Curry .
  ?person rdfs:label ?name .
  ?person a ?type .
}
"""
# Visualize the results
for r in g.query(query):
  print(r.name, r.type)

## Validation: Do not remove
report.validate_07_03(g, query)

"""**Task 7.4:**

English: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name
"""

query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name WHERE {
  ?person ns:hasColleague/ns:hasColleague? ?colleague .
  ?colleague ns:ownsPet ?pet .
  ?person rdfs:label ?name .
}
"""

for r in g.query(query):
  print(r.name)

# TO DO
# Visualize the results

## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")

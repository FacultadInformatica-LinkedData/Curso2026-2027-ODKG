# -*- coding: utf-8 -*-

# !pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials"

from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g1.parse(github_storage+"/rdf/data01.rdf", format="xml")
g2.parse(github_storage+"/rdf/data02.rdf", format="xml")

"""Spanish: Lista todos los elementos de la clase Person en el primer grafo (data01.rdf) y completa los campos (given name, family name y email) que puedan faltar con los datos del segundo grafo (data02.rdf). Puedes usar consultas SPARQL o iterar el grafo, o ambas cosas.

English: List all the elements of the Person class in the first graph (data01.rdf) and fill in any missing fields (given name, family name and email) using the data from the second graph (data02.rdf). You can use SPARQL queries or iterate through the graph, or both.
"""

query = '''
PREFIX ns: <http://data.org#>

SELECT DISTINCT ?s ?p ?o WHERE {
  ?s a ns:Person .
  ?s ?p ?o .
}
'''

print("Graph 1 Data:")
for r in g1.query(query):
  print(r.s, r.p, r.o)

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
ns = Namespace("http://data.org#")

for s, p, o in g1.triples((None, rdf.type, ns.Person)):
  for s2, p2, o2 in g2.triples((s, None, None)):
    if g1.value(s, p2) is None:
      g1.add((s2, p2, o2))

print("\nGraph 1 Data:")
for r in g1.query(query):
  print(r.s, r.p, r.o)

print("\nGraph 2 Data:")

for r in g2.query(query):
  print(r.s, r.p, r.o)
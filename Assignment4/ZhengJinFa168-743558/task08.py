#!/usr/bin/env python
# coding: utf-8

# **Task 08: Completing missing data**

# In[ ]:


# !pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials"

# In[ ]:


from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g1.parse(github_storage+"/rdf/data01.rdf", format="xml")
g2.parse(github_storage+"/rdf/data02.rdf", format="xml")

# Spanish: Lista todos los elementos de la clase Person en el primer grafo (data01.rdf) y completa los campos (given name, family name y email) que puedan faltar con los datos del segundo grafo (data02.rdf). Puedes usar consultas SPARQL o iterar el grafo, o ambas cosas.
# 
# English: List all the elements of the Person class in the first graph (data01.rdf) and fill in any missing fields (given name, family name and email) using the data from the second graph (data02.rdf). You can use SPARQL queries or iterate through the graph, or both.

# In[ ]:


from rdflib.namespace import RDF

vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")
person_uri = URIRef("http://data.org#Person")

for person in g1.subjects(RDF.type, person_uri):
    print("Person:", person)
    for p in [vcard.Given, vcard.Family, vcard.EMAIL]:
        for o in g2.objects(person, p):
            if not (person, p, o) in g1:
                g1.add((person, p, o))

for s, p, o in g1:
    print(s,p,o)


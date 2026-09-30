#!/usr/bin/env python
# coding: utf-8

# **Task 08: Completing missing data**

# In[1]:


# pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials"


# In[2]:


from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g1.parse(github_storage+"/rdf/data01.rdf", format="xml")
g2.parse(github_storage+"/rdf/data02.rdf", format="xml")


# Spanish: Lista todos los elementos de la clase Person en el primer grafo (data01.rdf) y completa los campos (given name, family name y email) que puedan faltar con los datos del segundo grafo (data02.rdf). Puedes usar consultas SPARQL o iterar el grafo, o ambas cosas.
# 
# English: List all the elements of the Person class in the first graph (data01.rdf) and fill in any missing fields (given name, family name and email) using the data from the second graph (data02.rdf). You can use SPARQL queries or iterate through the graph, or both.

# In[3]:


# Alternative approach:
query = """
PREFIX data: <http://data.org#>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>

SELECT ?person WHERE {
  ?person a data:Person.
  FILTER NOT EXISTS { ?person vcard:EMAIL ?e }
}
"""


# In[4]:


# Run the query over the first graph and list the persons without an email
for r in g1.query(query):
    print("Missing email:", r.person)


# In[6]:


# Import the RDF namespace
from rdflib.namespace import RDF

# Define the namespaces used in both data files
# Note: individuals use vcard-rdf/3.0# (with '#'), not '/3.0/'
data = Namespace("http://data.org#")
vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")


# In[7]:


# The three fields we need to check for each person
fields = [("Given", vcard.Given), ("Family", vcard.Family), ("EMAIL", vcard.EMAIL)]

# Show the state of the first graph before completing it
print("=== BEFORE ===")
for p in g1.subjects(RDF.type, data.Person):
    print(p)
    for label, prop in fields:
        # g1.value() returns the value of the property, or None if it is missing
        print("   ", label, "=", g1.value(p, prop))


# In[8]:


# Complete the missing fields using g2
for p in g1.subjects(RDF.type, data.Person):
    for label, prop in fields:
        if g1.value(p, prop) is None:
            value = g2.value(p, prop)
            if value is not None:
                g1.add((p, prop, value))
                print(f"Added {label} = {value} to {p}")
            else:
                print(f"Could not find {label} for {p} in the second graph")


# In[9]:


# Show the state of the first graph after completing it
print("\n=== AFTER ===")
for p in g1.subjects(RDF.type, data.Person):
    print(p)
    for label, prop in fields:
        print("   ", label, "=", g1.value(p, prop))


# In[10]:


# Save the completed graph to a Turtle file
g1.serialize(destination="data01_completed.ttl", format="turtle")


#!/usr/bin/env python
# coding: utf-8

# **Task 09: Data linking**

# In[1]:


# pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials/"


# In[2]:


from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g3 = Graph()
g1.parse(github_storage+"rdf/data03.rdf", format="xml")
g2.parse(github_storage+"rdf/data04.rdf", format="xml")


# Spanish: Busca individuos en los dos grafos y enlázalos mediante la propiedad OWL:sameAs, inserta estas coincidencias en g3. Consideramos dos individuos iguales si tienen el mismo apodo y nombre de familia. Ten en cuenta que las URI no tienen por qué ser iguales para un mismo individuo en los dos grafos.
# 
# English: Search for individuals in both graphs and link them using the OWL:sameAs property; insert these matches into g3. We consider two individuals to be the same if they have the same first name and surname. Please note that the URIs do not necessarily have to be the same for the same individual in both graphs.

# In[3]:


# Import the RDF and OWL namespaces
from rdflib.namespace import RDF, OWL

# Define the namespaces: each graph uses its own base URI
vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")
three = Namespace("http://data.three.org#")
four = Namespace("http://data.four.org#")


# In[4]:


# Bind the prefixes so the output of g3 is easier to read
g3.bind("owl", OWL)
g3.bind("three", three)
g3.bind("four", four)


# In[5]:


# Compare every person of g1 with every person of g2
for p1 in g1.subjects(RDF.type, three.Person):
    given1 = g1.value(p1, vcard.Given)
    family1 = g1.value(p1, vcard.Family)

    # Skip the individuals that do not have both fields: we cannot compare them
    if given1 is None or family1 is None:
        print(f"Skipping {p1}: it has no Given and/or Family")
        continue

    for p2 in g2.subjects(RDF.type, four.Person):
        given2 = g2.value(p2, vcard.Given)
        family2 = g2.value(p2, vcard.Family)

        # Two individuals are the same if both the first name and the surname match
        if given1 == given2 and family1 == family2:
            g3.add((p1, OWL.sameAs, p2))
            print(f"Match: {p1} owl:sameAs {p2}")


# In[6]:


# Show the resulting links
print("\n=== g3 (owl:sameAs links) ===")
print(g3.serialize(format="turtle"))


# With the strict rule (same Given + same Family), only 2 of the 4 individuals in g1 are linked. JohnSmith is missed because g2 stores the formal first name ("Jonathan" instead of "John"), and HarryPotter is missed because the Family field is absent in g1. Matching on the full name (vcard:FN) would link all four, which shows that relying on a single pair of fields is fragile for data linking.

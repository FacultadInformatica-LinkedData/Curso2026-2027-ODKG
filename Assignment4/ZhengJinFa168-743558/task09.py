#!/usr/bin/env python
# coding: utf-8

# **Task 09: Data linking**

# In[ ]:


# !pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials/"

# In[ ]:


from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g3 = Graph()
g1.parse(github_storage+"rdf/data03.rdf", format="xml")
g2.parse(github_storage+"rdf/data04.rdf", format="xml")

# Spanish: Busca individuos en los dos grafos y enlázalos mediante la propiedad OWL:sameAs, inserta estas coincidencias en g3. Consideramos dos individuos iguales si tienen el mismo apodo y nombre de familia. Ten en cuenta que las URI no tienen por qué ser iguales para un mismo individuo en los dos grafos.
# 
# English: Search for individuals in both graphs and link them using the OWL:sameAs property; insert these matches into g3. We consider two individuals to be the same if they have the same first name and surname. Please note that the URIs do not necessarily have to be the same for the same individual in both graphs.

# In[ ]:


from rdflib.namespace import OWL

vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")

for s1, p1, o1 in g1.triples((None, vcard.Given, None)):
    for s1_f, p1_f, o1_f in g1.triples((s1, vcard.Family, None)):
        for s2, p2, o2 in g2.triples((None, vcard.Given, o1)):
            for s2_f, p2_f, o2_f in g2.triples((s2, vcard.Family, o1_f)):
                g3.add((s1, OWL.sameAs, s2))

for s, p, o in g3:
    print(s,p,o)


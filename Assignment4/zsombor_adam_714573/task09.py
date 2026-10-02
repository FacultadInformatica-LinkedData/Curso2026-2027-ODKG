#!/usr/bin/env python
# coding: utf-8

# **Task 09: Data linking**

# In[6]:


#get_ipython().system('pip install rdflib')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG/master/Assignment4/course_materials/"


# In[7]:


from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g3 = Graph()
g1.parse(github_storage+"rdf/data03.rdf", format="xml")
g2.parse(github_storage+"rdf/data04.rdf", format="xml")


# Spanish: Busca individuos en los dos grafos y enlázalos mediante la propiedad OWL:sameAs, inserta estas coincidencias en g3. Consideramos dos individuos iguales si tienen el mismo apodo y nombre de familia. Ten en cuenta que las URI no tienen por qué ser iguales para un mismo individuo en los dos grafos.
# 
# English: Search for individuals in both graphs and link them using the OWL:sameAs property; insert these matches into g3. We consider two individuals to be the same if they have the same first name and surname. Please note that the URIs do not necessarily have to be the same for the same individual in both graphs.

# In[12]:


query = '''
PREFIX ns: <http://data.three.org#>

SELECT DISTINCT ?s ?p ?o WHERE {
  ?s a ns:Person .
  ?s ?p ?o .
}
'''

for r in g1.query(query):
  print(r.s, r.p, r.o)

print(30 * '---')

query = '''
PREFIX ns: <http://data.four.org#>

SELECT DISTINCT ?s ?p ?o WHERE {
  ?s a ns:Person .
  ?s ?p ?o .
}
'''

for r in g2.query(query):
  print(r.s, r.p, r.o)


# In[14]:


query1 = '''
PREFIX ns: <http://data.three.org#>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>

SELECT ?s ?given ?family WHERE {
    ?s a ns:Person .
    ?s vcard:Given ?given .
    ?s vcard:Family ?family .
}
'''

query2 = '''
PREFIX ns: <http://data.four.org#>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>

SELECT ?s ?given ?family WHERE {
    ?s a ns:Person .
    ?s vcard:Given ?given .
    ?s vcard:Family ?family .
}
'''

for r1 in g1.query(query1):
  for r2 in g2.query(query2):
    if r1.given == r2.given and r1.family == r2.family:
        g3.add((r1.s, URIRef('http://www.w3.org/2002/07/owl#sameAs'), r2.s))


# In[15]:


for s, p, o in g3:
  print(s, p, o)


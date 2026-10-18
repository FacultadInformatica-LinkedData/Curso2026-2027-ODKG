#!/usr/bin/env python
# coding: utf-8

# **Task 07: Querying RDF(s)**

# In[1]:


#get_ipython().system('pip install rdflib')
#get_ipython().system('pip install oeg-sw-class')
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG/master/Assignment4/course_materials"


# Spanish: Primero leemos los ficheros RDF
# 
# English: First let's read the RDF file

# In[55]:


from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data07.ttl", format="TTL")
report = Report()


# **TASK 7.1a:**
# 
# Spanish: Para todas las clases, enumera cada classURI. Si la clase pertenece a otra clase, indica su superclase. Realiza el ejercicio en RDFLib devolviendo una lista de tuplas: (clase, superclase) denominada "result". Si una clase no tiene superclase, devuelve None como superclase.
# 
# English: For all classes, list each classURI. If the class belogs to another class, then list its superclass. Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass

# In[33]:


result = [] #list of tuples

for s, p, o in g.triples((None, RDF.type, RDFS.Class)):
    if (s, RDFS.subClassOf, None) in g:
        for s2, p2, o2 in g.triples((s, RDFS.subClassOf, None)):
            result.append((s, o2))
    else:
        result.append((s, None))

# Visualize the results
for r in result:
  print(r)


# In[34]:


## Validation: Do not remove
report.validate_07_1a(result)


# **TASK 7.1b:**
# 
# Spanish: Repite el mismo ejercicio en SPARQL, devolviendo las variables ?c (clase) y ?sc (superclase)
# 
# English: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)

# In[12]:


query = """SELECT ?c ?sc WHERE {
    ?c a rdfs:Class .
    OPTIONAL { ?c rdfs:subClassOf ?sc }
}
"""

for r in g.query(query):
  print(r.c, r.sc)


# In[13]:


## Validation: Do not remove
report.validate_07_1b(query,g)


# **TASK 7.2a:**
# 
# Spanish: Enumera todos los individuos de "Person" con RDFLib (ten en cuenta las subclases). Devuelve los URI de los individuos en una lista llamada "individuals".
# 
# English: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"
# 

# In[41]:


ns = Namespace("http://oeg.fi.upm.es/def/people#")

# variable to return
individuals = []

# A javítás: kapcsos zárójeleket használunk, hogy a URIRef maga legyen a halmaz egyetlen eleme
subclasses = {ns.Person}
new_subclasses = {ns.Person}

while new_subclasses:
    next_level = set()
    for current_class in new_subclasses:
        for s, p, o in g.triples((None, RDFS.subClassOf, current_class)):
            subclasses.add(s)
            next_level.add(s)
    new_subclasses = next_level

for c in subclasses:
    for s, p, o in g.triples((None, RDF.type, c)):
        individuals.append(s)

# visualize results
for i in individuals:
  print(i)


# In[46]:


# validation. Do not remove
report.validate_07_02a(individuals)


# **TASK 7.2b:**
# 
# Spanish: Repite el mismo ejercicio en SPARQL, devolviendo los URI individuales en una variable ?ind.
# 
# English: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind

# In[58]:


query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>

SELECT ?ind WHERE {
    ?subClass rdfs:subClassOf* ns:Person .
    ?ind rdf:type ?subClass .
}
"""

# Visualize the results
for r in g.query(query):
  print(r.ind)


# In[59]:


## Validation: Do not remove
report.validate_07_02b(g, query)


# **TASK 7.3:**
# 
# Spanish: Enumera el nombre y el tipo de quienes conocen a Curry (solo en SPARQL). Utiliza el nombre y el tipo como variables en la consulta.
# 
# English: List the name and type of those who know Curry (in SPARQL only). Use name and type as variables in the query

# In[60]:


query =  """
PREFIX ns:  <http://oeg.fi.upm.es/def/people#>

SELECT ?name ?type WHERE {
    ?person ns:knows ns:Curry .
    ?person rdfs:label ?name .
    ?person rdf:type ?type .
}
"""

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# In[61]:


## Validation: Do not remove
report.validate_07_03(g, query)


# **Task 7.4:**
# 
# Spanish: Enumera los nombres de aquellas entidades que tengan un compañero de trabajo que tenga un perro, o que tengan un compañero de trabajo que tenga un compañero de trabajo que tenga un perro (en SPARQL). Devuelve los resultados en una variable llamada «name».
# 
# English: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name

# In[64]:


query =  """
PREFIX ns:  <http://oeg.fi.upm.es/def/people#>

SELECT DISTINCT ?name WHERE {
    ?person ns:hasColleague* ?colleague .
    ?colleague ns:ownsPet ?dog .
    ?dog rdf:type ns:Animal .
    ?person rdfs:label ?name .
}
"""

# Visualize the results
for r in g.query(query):
  print(r.name)


# In[65]:


## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")


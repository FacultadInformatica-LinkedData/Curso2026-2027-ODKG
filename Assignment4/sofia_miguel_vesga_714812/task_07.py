# %% [markdown]
# **Task 07: Querying RDF(s)**

# %%
#%pip install rdflib
#%pip install oeg-sw-class
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2026-2027-ODKG/master/Assignment4/course_materials"

# %% [markdown]
# Spanish: Primero leemos los ficheros RDF
# 
# English: First let's read the RDF file

# %%
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.parse(github_storage+"/rdf/data07.ttl", format="TTL")
report = Report()

# %% [markdown]
# **TASK 7.1a:**
# 
# Spanish: Para todas las clases, enumera cada classURI. Si la clase pertenece a otra clase, indica su superclase. Realiza el ejercicio en RDFLib devolviendo una lista de tuplas: (clase, superclase) denominada "result". Si una clase no tiene superclase, devuelve None como superclase.
# 
# English: For all classes, list each classURI. If the class belogs to another class, then list its superclass. Do the exercise in RDFLib returning a list of Tuples: (class, superclass) called "result". If a class does not have a super class, then return None as the superclass

# %%
classes = set(g.subjects(RDF.type, RDFS.Class))

result = [] #list of tuples

for cls in classes:
    superclasses = list(g.objects(cls, RDFS.subClassOf))
    if superclasses:
        for scls in superclasses:
            result.append((cls, scls))
    else:
        result.append((cls, None))

# Visualize the results
for r in result:
  print(r)

# %%
## Validation: Do not remove
report.validate_07_1a(result)

# %% [markdown]
# **TASK 7.1b:**
# 
# Spanish: Repite el mismo ejercicio en SPARQL, devolviendo las variables ?c (clase) y ?sc (superclase)
# 
# English: Repeat the same exercise in SPARQL, returning the variables ?c (class) and ?sc (superclass)

# %%
query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?c ?sc WHERE {
        ?c rdf:type rdfs:Class .
        OPTIONAL {
            ?c rdfs:subClassOf ?sc .
        }
    }
"""

for r in g.query(query):
  print(r.c, r.sc)


# %%
## Validation: Do not remove
report.validate_07_1b(query,g)

# %% [markdown]
# **TASK 7.2a:**
# 
# Spanish: Enumera todos los individuos de "Person" con RDFLib (ten en cuenta las subclases). Devuelve los URI de los individuos en una lista llamada "individuals".
# 
# English: List all individuals of "Person" with RDFLib (remember the subClasses). Return the individual URIs in a list called "individuals"
# 

# %%
ns = Namespace("http://oeg.fi.upm.es/def/people#")

# variable to return
individuals = []

classes = {ns.Person}
classes_to_explore = [ns.Person]

while classes_to_explore:
    current = classes_to_explore.pop()
    for sub in g.subjects(RDFS.subClassOf, current):
        if sub not in classes:
            classes.add(sub)
            classes_to_explore.append(sub)

for c in classes:
    for s in g.subjects(RDF.type, c):
        if s not in individuals:
            individuals.append(s)

# visualize results
for i in individuals:
  print(i)

# %%
# validation. Do not remove
report.validate_07_02a(individuals)

# %% [markdown]
# **TASK 7.2b:**
# 
# Spanish: Repite el mismo ejercicio en SPARQL, devolviendo los URI individuales en una variable ?ind.
# 
# English: Repeat the same exercise in SPARQL, returning the individual URIs in a variable ?ind

# %%
query = """
    PREFIX ns: <http://oeg.fi.upm.es/def/people#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?ind WHERE {
        ?sc rdfs:subClassOf* ns:Person .
        ?ind rdf:type ?sc .
    }
"""

for r in g.query(query):
  print(r.ind)
# Visualize the results

# %%
## Validation: Do not remove
report.validate_07_02b(g, query)

# %% [markdown]
# **TASK 7.3:**
# 
# Spanish: Enumera el nombre y el tipo de quienes conocen a Curry (solo en SPARQL). Utiliza el nombre y el tipo como variables en la consulta.
# 
# English: List the name and type of those who know Curry (in SPARQL only). Use name and type as variables in the query

# %%
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name ?type WHERE {
    { ?person foaf:knows ?curry } UNION { ?person ns:knows ?curry }
    FILTER(STRENDS(STR(?curry), "Curry"))
    
    ?person rdf:type ?type .
    
    { ?person foaf:name ?name } 
    UNION 
    { ?person rdfs:label ?name }
    UNION 
    { ?person ns:name ?name }
}
"""

# Visualize the results
for r in g.query(query):
  print(r.name, r.type)


# %%
## Validation: Do not remove
report.validate_07_03(g, query)

# %% [markdown]
# **Task 7.4:**
# 
# Spanish: Enumera los nombres de aquellas entidades que tengan un compañero de trabajo que tenga un perro, o que tengan un compañero de trabajo que tenga un compañero de trabajo que tenga un perro (en SPARQL). Devuelve los resultados en una variable llamada «name».
# 
# English: List the name of those entities who have a colleague with a dog, or that have a collegue who has a colleague who has a dog (in SPARQL). Return the results in a variable called name

# %%
#for s, p, o in g:
#    if any(k in str(p).lower() or k in str(o).lower() for k in ["dog", "colleague", "pet"]):
#        print(s, p, o)


for s, p, o in g:
    s_str = str(s).lower()
    if any(k in s_str for k in ["curry", "rocky", "fantasma", "asun", "juan", "raul", "oscar"]):
        print(f"{s}  -->  {p}  -->  {o}")

# %%
query = """
PREFIX ns: <http://oeg.fi.upm.es/def/people#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?name WHERE {
    ?person (ns:hasColleague|ns:hasColleague/ns:hasColleague) ?owner .
    ?owner ns:ownsPet ?pet .
    ?person rdfs:label ?name .
}
"""

for r in g.query(query):
  print(r.name)


# %%
## Validation: Do not remove
report.validate_07_04(g,query)
report.save_report("_Task_07")



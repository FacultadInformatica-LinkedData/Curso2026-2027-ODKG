# %% [markdown]
# **Task 08: Completing missing data**

# %%
# %pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials"

# %%
from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g1.parse(github_storage+"/rdf/data01.rdf", format="xml")
g2.parse(github_storage+"/rdf/data02.rdf", format="xml")

# %% [markdown]
# Spanish: Lista todos los elementos de la clase Person en el primer grafo (data01.rdf) y completa los campos (given name, family name y email) que puedan faltar con los datos del segundo grafo (data02.rdf). Puedes usar consultas SPARQL o iterar el grafo, o ambas cosas.
# 
# English: List all the elements of the Person class in the first graph (data01.rdf) and fill in any missing fields (given name, family name and email) using the data from the second graph (data02.rdf). You can use SPARQL queries or iterate through the graph, or both.

# %%
from rdflib import Namespace

vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")

query = """
PREFIX data: <http://data.org#>
PREFIX vcard: <http://www.w3.org/2001/vcard-rdf/3.0#>

SELECT ?person ?given ?family ?email
WHERE {
    ?person a data:Person .
    OPTIONAL { ?person vcard:Given ?given }
    OPTIONAL { ?person vcard:Family ?family }
    OPTIONAL { ?person vcard:EMAIL ?email }
}
"""

for row in g1.query(query):
    print(row.person,
        row.given or g2.value(row.person, vcard.Given),
        row.family or g2.value(row.person, vcard.Family),
        row.email or g2.value(row.person, vcard.EMAIL))



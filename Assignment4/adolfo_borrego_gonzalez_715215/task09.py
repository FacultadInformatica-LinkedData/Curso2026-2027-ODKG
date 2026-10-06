# %% [markdown]
# **Task 09: Data linking**

# %%
# %pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2021-2022/master/Assignment4/course_materials/"

# %%
from rdflib import Graph, Namespace, Literal, URIRef
g1 = Graph()
g2 = Graph()
g3 = Graph()
g1.parse(github_storage+"rdf/data03.rdf", format="xml")
g2.parse(github_storage+"rdf/data04.rdf", format="xml")

# %% [markdown]
# Spanish: Busca individuos en los dos grafos y enlázalos mediante la propiedad OWL:sameAs, inserta estas coincidencias en g3. Consideramos dos individuos iguales si tienen el mismo apodo y nombre de familia. Ten en cuenta que las URI no tienen por qué ser iguales para un mismo individuo en los dos grafos.
# 
# English: Search for individuals in both graphs and link them using the OWL:sameAs property; insert these matches into g3. We consider two individuals to be the same if they have the same first name and surname. Please note that the URIs do not necessarily have to be the same for the same individual in both graphs.

# %%
from rdflib import Namespace
from rdflib.namespace import OWL

vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0#")

for p1 in g1.subjects():
    given1 = g1.value(p1, vcard.Given)
    family1 = g1.value(p1, vcard.Family)

    for p2 in g2.subjects():
        given2 = g2.value(p2, vcard.Given)
        family2 = g2.value(p2, vcard.Family)

        if given1 == given2 and family1 == family2 and given1 is not None and family1 is not None:
            g3.add((p1, OWL.sameAs, p2))

for triple in g3:
    print(triple)



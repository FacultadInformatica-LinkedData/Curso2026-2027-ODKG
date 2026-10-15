# %% [markdown]
# # **Task 06: Modifying RDF(s)**

# %%
#!pip install rdflib
#!pip install oeg-sw-class

# %%
# %pip install rdflib
# %pip install oeg-sw-class

# %% [markdown]
# Spanish: Importar la librería RDFLib
# 
# English: Import RDFLib main methods

# %%
from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()

# %% [markdown]
# Spanish: Crear una nueva clase llamada "Researcher"
# 
# English: Create a new class named Researcher

# %%
ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)

# %% [markdown]
# ### **Task 6.0:**
# 
# Spanish: Crea nuevos prefijos para "ontology", "organization" and "person", con la siguiente información:
# 
# *   person: http://oeg.fi.upm.es/resource/person/
# *   organization: http://oeg.fi.upm.es/resource/organization/
# *   ontology: http://oeg.fi.upm.es/def/people#
# 
# English: Create new prefixes for "ontology", "organization" and "person", with the following information:
# 
# *   person: http://oeg.fi.upm.es/resource/person/
# *   organization: http://oeg.fi.upm.es/resource/organization/
# *   ontology: http://oeg.fi.upm.es/def/people#

# %%
person = Namespace("http://oeg.fi.upm.es/resource/person/")
g.namespace_manager.bind('person', person)
org = Namespace("http://oeg.fi.upm.es/resource/organization/")
g.namespace_manager.bind('org', org)
ont = Namespace("http://oeg.fi.upm.es/def/people#")
g.namespace_manager.bind('ont', ont)

# %% [markdown]
# ### **Task 6.1**
# 
# Spanish: Reproduce la taxonomía de clases que aparece en el diagrama (`Assignment4/course_materials/diagram/diagram.jpg`). Añade etiquetas para cada una de ellas tal y como aparecen en el diagrama (exactamente), sin etiquetas de idioma. Recuerda añadir el tipo de datos correcto (xsd:String) cuando sea necesario.
# 
# English: Reproduce the taxonomy of classes shown in the diagram (`Assignment4/course_materials/diagram/diagram.jpg`). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate.
# 

# %% [markdown]
# 

# %%
g.add((ont.Person, RDF.type, RDFS.Class))
g.add((ont.Person, RDFS.label, Literal("Person", datatype=XSD.string)))

g.add((ont.Professor, RDF.type, RDFS.Class))
g.add((ont.Professor, RDFS.subClassOf, ont.Person))
g.add((ont.Professor, RDFS.label, Literal("Professor", datatype=XSD.string)))

g.add((ont.FullProfessor, RDF.type, RDFS.Class))
g.add((ont.FullProfessor, RDFS.subClassOf, ont.Professor))
g.add((ont.FullProfessor, RDFS.label, Literal("FullProfessor", datatype=XSD.string)))

g.add((ont.AssistantProfessor, RDF.type, RDFS.Class))
g.add((ont.AssistantProfessor, RDFS.subClassOf, ont.Professor))
g.add((ont.AssistantProfessor, RDFS.label, Literal("AssistantProfessor", datatype=XSD.string)))

g.add((ont.AssociateProfessor, RDF.type, RDFS.Class))
g.add((ont.AssociateProfessor, RDFS.subClassOf, ont.Professor))
g.add((ont.AssociateProfessor, RDFS.label, Literal("AssociateProfessor", datatype=XSD.string)))

g.add((ont.InterimAssociateProfessor, RDF.type, RDFS.Class))
g.add((ont.InterimAssociateProfessor, RDFS.subClassOf, ont.AssociateProfessor))
g.add((ont.InterimAssociateProfessor, RDFS.label, Literal("InterimAssociateProfessor", datatype=XSD.string)))

# %%
#Validation: Do not remove
r.validate_task_06_01(g)

# %% [markdown]
# ### **Task 6.2**
# 
# Spanish: Crea la clase ontology:University.
# 
# English: Create the ontology:University class.

# %%
g.add((ont.University, RDF.type, RDFS.Class))
g.add((ont.University, RDFS.label, Literal("University", datatype=XSD.string)))

# %%
#Validation: Do not remove
r.validate_task_06_02(g)

# %% [markdown]
# ### **Task 6.3**
# 
# Spanish: Añade las propiedades que aparecen en el diagrama. Añade etiquetas para cada una de ellas (exactamente como aparecen en la diapositiva, sin etiquetas de idioma), así como sus dominios y rangos correspondientes utilizando RDFS. Recuerda añadir el tipo de datos correcto (xsd:String) cuando sea necesario. Si una propiedad no tiene rango, conviértela en un literal (cadena de caracteres). Por otra parte, ontology:affiliatedWith tendrá como dominio ontology:Person y rango ontology:University.
# 
# English: Add the properties shown in the previous diagram. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string). Furthermore, the ontology:affiliatedWith property will have ontology:Person as its domain and ontology:University as its range.
# 

# %%
g.add((ont.hasName, RDF.type, RDF.Property))
g.add((ont.hasName, RDFS.domain, ont.Person))
g.add((ont.hasName, RDFS.range, RDFS.Literal))
g.add((ont.hasName, RDFS.label, Literal("hasName", datatype=XSD.string)))

g.add((ont.hasColleague, RDF.type, RDF.Property))
g.add((ont.hasColleague, RDFS.domain, ont.Person))
g.add((ont.hasColleague, RDFS.range, ont.Person))
g.add((ont.hasColleague, RDFS.label, Literal("hasColleague", datatype=XSD.string)))

g.add((ont.hasHomePage, RDF.type, RDF.Property))
g.add((ont.hasHomePage, RDFS.domain, ont.FullProfessor))
g.add((ont.hasHomePage, RDFS.range, RDFS.Literal))
g.add((ont.hasHomePage, RDFS.label, Literal("hasHomePage", datatype=XSD.string)))

g.add((ont.affiliatedWith, RDF.type, RDF.Property))
g.add((ont.affiliatedWith, RDFS.domain, ont.Person))
g.add((ont.affiliatedWith, RDFS.range, ont.University))
g.add((ont.affiliatedWith, RDFS.label, Literal("affiliatedWith", datatype=XSD.string)))

# %%
#Validation: Do not remove
r.validate_task_06_03(g)

# %% [markdown]
# ### **Task 6.4**
# 
# Spanish: Crea los individuos que aparecen en el diagrama, en la sección «Datos». Vincúlalos con las mismas relaciones que se muestran en el diagrama.
# 
# English: Create the individuals shown in the diagram under "Datos". Link them with the same relationships shown in the diagram."

# %%

university = Namespace("http://oeg.fi.upm.es/resource/university/")
g.namespace_manager.bind("university", university)

# %%
g.add((person.Raul, RDF.type, ont.FullProfessor))
g.add((person.Raul, RDFS.label, Literal("Raúl", datatype=XSD.string)))
g.add((person.Raul, ont.hasHomePage, Literal("http://oeg.fi.upm.es", datatype=XSD.string)))
g.add((person.Raul, ont.hasColleague, person.Juan))

g.add((person.Juan, RDF.type, ont.AssistantProfessor))
g.add((person.Juan, RDFS.label, Literal("Juan", datatype=XSD.string)))
g.add((person.Juan, ont.hasName, Literal("Juan Cano de Benito", datatype=XSD.string)))
g.add((person.Juan, ont.hasColleague, person.Sven))

g.add((person.Sven, RDFS.label, Literal("Sven", datatype=XSD.string)))
g.add((person.Sven, ont.affiliatedWith, university.Mannheim))

# %%
#Validation: Do not remove
r.validate_task_06_04(g)

# %% [markdown]
# ### **Task 6.5**
# 
# Spanish: Añadir a person:Juan la dirección email (juan.cano@upm.es), el nombre (given) y los apellidos (family). Utiliza las propiedades que ya se incluyen en el ejemplo 4 para describir a Jane y John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). No importes los espacios de nombres; añádelos manualmente.
# 
# English: Add to the individual person:Juan the email address (juan.cano@upm.es), given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually.
# 

# %%
foaf = Namespace("http://xmlns.com/foaf/0.1/")

g.add((person.Juan, foaf.mbox, Literal("juan.cano@upm.es", datatype=XSD.string)))
g.add((person.Juan, foaf.givenName, Literal("Juan", datatype=XSD.string)))
g.add((person.Juan, foaf.familyName, Literal("Cano de Benito", datatype=XSD.string)))

# %%
#Validation: Do not remove
r.validate_task_06_05(g)

# %% [markdown]
# ### **Task 6.6**
# 
# Spanish: Añade que Juan y Raúl están afiliados (affiliatedWith) a university:UPM. También que Sven es de tipo InterimAssociateProfessor.
# 
# English:  Add that Juan and Raúl are affiliated (affiliatedWith) with the university:UPM. Also add that Sven is a InterimAssociateProfessor

# %%
g.add((person.Juan, ont.affiliatedWith, university.UPM))
g.add((person.Raul, ont.affiliatedWith, university.UPM))

g.add((person.Sven, RDF.type, ont.InterimAssociateProfessor))

# %%
#Validation: Do not remove
r.validate_task_06_06(g)

# %% [markdown]
# ### **Task 6.7**
# 
# Spanish: Tanto university:UPM como university:Mannheim son de tipo ontology:University.
# 
# English:  Both university:UPM and university:Mannheim are ontology:University type.

# %%
g.add((university.UPM, RDF.type, ont.University))
g.add((university.Mannheim, RDF.type, ont.University))

# %%
#Validation: Do not remove
r.validate_task_06_07(g)
r.save_report("_Task_06")



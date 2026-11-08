# -*- coding: utf-8 -*-
"""Task06_mandatory.ipynb

# **Task 06: Modifying RDF(s)**
"""

# !pip install rdflib
# !pip install oeg-sw-class

"""Spanish: Importar la librería RDFLib

English: Import RDFLib main methods
"""

from rdflib import Graph, Namespace, Literal, XSD
from rdflib.namespace import RDF, RDFS
from oeg_sw_class import Report
# Do not change the name of the variables
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
r = Report()

"""Spanish: Crear una nueva clase llamada "Researcher"

English: Create a new class named Researcher
"""

ns = Namespace("http://mydomain.org#")
g.add((ns.Researcher, RDF.type, RDFS.Class))
for s, p, o in g:
  print(s,p,o)

"""### **Task 6.0:**

English: Create new prefixes for "ontology", "organization" and "person", with the following information:

*   person: http://oeg.fi.upm.es/resource/person/
*   organization: http://oeg.fi.upm.es/resource/organization/
*   ontology: http://oeg.fi.upm.es/def/people#
"""

# this task is validated in the next step
person = Namespace("http://oeg.fi.upm.es/resource/person/")
organization = Namespace("http://oeg.fi.upm.es/resource/organization/")
ontology = Namespace("http://oeg.fi.upm.es/def/people#")
g.bind("person", person)
g.bind("organization", organization)
g.bind("ontology", ontology)

"""### **Task 6.1**

English: Reproduce the taxonomy of classes shown in the diagram (`Assignment4/course_materials/diagram/diagram.jpg`). Add labels for each of them as they are in the diagram (exactly) with no language tags. Remember adding the correct datatype (xsd:String) when appropriate.
"""

classes = ["Person", "Professor", "FullProfessor", "AssociateProfessor",
           "InterimAssociateProfessor", "AssistantProfessor"]
for name in classes:
  g.add((ontology[name], RDF.type, RDFS.Class))
  g.add((ontology[name], RDFS.label, Literal(name, datatype=XSD.string)))

g.add((ontology.Professor, RDFS.subClassOf, ontology.Person))
g.add((ontology.FullProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.AssociateProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.AssistantProfessor, RDFS.subClassOf, ontology.Professor))
g.add((ontology.InterimAssociateProfessor, RDFS.subClassOf, ontology.AssociateProfessor))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_01(g)

"""### **Task 6.2**

English: Create the ontology:University class.
"""

g.add((ontology.University, RDF.type, RDFS.Class))
g.add((ontology.University, RDFS.label, Literal("University", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_02(g)

"""### **Task 6.3**

English: Add the properties shown in the previous diagram. Add labels for each of them (exactly as they are in the slide, with no language tags), and their corresponding domains and ranges using RDFS. Remember adding the correct datatype (xsd:String) when appropriate. If a property has no range, make it a literal (string). Furthermore, the ontology:affiliatedWith property will have ontology:Person as its domain and ontology:University as its range.
"""

properties = {
  "hasName": (ontology.Person, RDFS.Literal),
  "hasColleague": (ontology.Person, ontology.Person),
  "hasHomePage": (ontology.FullProfessor, RDFS.Literal),
  "affiliatedWith": (ontology.Person, ontology.University),
}
for name, (domain, range_) in properties.items():
  g.add((ontology[name], RDF.type, RDF.Property))
  g.add((ontology[name], RDFS.label, Literal(name, datatype=XSD.string)))
  g.add((ontology[name], RDFS.domain, domain))
  g.add((ontology[name], RDFS.range, range_))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_03(g)

"""### **Task 6.4**

English: Create the individuals shown in the diagram under "Datos". Link them with the same relationships shown in the diagram."
"""

university = Namespace("http://oeg.fi.upm.es/resource/university/")
g.bind("university", university)

g.add((person.Raul, RDF.type, ontology.FullProfessor))
g.add((person.Raul, RDFS.label, Literal("Raúl", datatype=XSD.string)))
g.add((person.Raul, ontology.hasColleague, person.Juan))
g.add((person.Raul, ontology.hasHomePage, Literal("http://oeg.fi.upm.es", datatype=XSD.string)))

g.add((person.Juan, RDF.type, ontology.AssistantProfessor))
g.add((person.Juan, RDFS.label, Literal("Juan", datatype=XSD.string)))
g.add((person.Juan, ontology.hasColleague, person.Sven))
g.add((person.Juan, ontology.hasName, Literal("Juan Cano de Benito", datatype=XSD.string)))

g.add((person.Sven, RDFS.label, Literal("Sven", datatype=XSD.string)))
g.add((person.Sven, ontology.affiliatedWith, university.Mannheim))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_04(g)

"""### **Task 6.5**

English: Add to the individual person:Juan the email address (juan.cano@upm.es), given and family names. Use the properties already included in example 4 to describe Jane and John (https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2025-2026/master/Assignment4/course_materials/rdf/example4.rdf). Do not import the namespaces, add them manually.
"""

foaf = Namespace("http://xmlns.com/foaf/0.1/")
g.bind("foaf", foaf)

g.add((person.Juan, foaf.givenName, Literal("Juan", datatype=XSD.string)))
g.add((person.Juan, foaf.familyName, Literal("Cano de Benito", datatype=XSD.string)))
g.add((person.Juan, foaf.mbox, Literal("juan.cano@upm.es", datatype=XSD.string)))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_05(g)

"""### **Task 6.6**

English:  Add that Juan and Raúl are affiliated (affiliatedWith) with the university:UPM. Also add that Sven is a InterimAssociateProfessor
"""

g.add((person.Juan, ontology.affiliatedWith, university.UPM))
g.add((person.Raul, ontology.affiliatedWith, university.UPM))
g.add((person.Sven, RDF.type, ontology.InterimAssociateProfessor))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_06(g)

"""### **Task 6.7**

English:  Both university:UPM and university:Mannheim are ontology:University type.
"""

g.add((university.UPM, RDF.type, ontology.University))
g.add((university.Mannheim, RDF.type, ontology.University))

# Visualize the results
for s, p, o in g:
  print(s,p,o)

#Validation: Do not remove
r.validate_task_06_07(g)
r.save_report("_Task_06")

Noah Rose
Assignment 3 

Spanish endpoint was down due to traffic so I just used the normal one.

1.

PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property
WHERE {
  ?politician rdf:type dbo:Politician .
  ?politician ?property ?value .
}
ORDER BY ?property


RESULTS:


property
http://dbpedia.org/ontology/Person/height
http://dbpedia.org/ontology/Person/weight
http://dbpedia.org/ontology/PopulatedPlace/areaTotal
http://dbpedia.org/ontology/abbreviation
http://dbpedia.org/ontology/academicAdvisor
http://dbpedia.org/ontology/academicDiscipline
http://dbpedia.org/ontology/activeYearsEndDate
http://dbpedia.org/ontology/activeYearsEndYear
http://dbpedia.org/ontology/activeYearsStartDate
http://dbpedia.org/ontology/activeYearsStartYear

2. 

PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property
WHERE {
  ?politician rdf:type dbo:Politician .
  ?politician ?property ?value .
  FILTER (?property != rdf:type)
}
ORDER BY ?property


RESULTS:

property
http://dbpedia.org/ontology/Person/height
http://dbpedia.org/ontology/Person/weight
http://dbpedia.org/ontology/PopulatedPlace/areaTotal
http://dbpedia.org/ontology/abbreviation
http://dbpedia.org/ontology/academicAdvisor
http://dbpedia.org/ontology/academicDiscipline
http://dbpedia.org/ontology/activeYearsEndDate
http://dbpedia.org/ontology/activeYearsEndYear
http://dbpedia.org/ontology/activeYearsStartDate
http://dbpedia.org/ontology/activeYearsStartYear

3. 

PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property ?value
WHERE {
  ?politician rdf:type dbo:Politician .
  ?politician ?property ?value .
  FILTER (?property != rdf:type)
}
ORDER BY ?property ?value


RESULTS:

property	value
http://dbpedia.org/ontology/Person/height	
"157.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"165.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"167.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"170.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"170.18"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"173.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"174.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"175.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"175.26"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"176.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"178.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"179.0"^^<http://dbpedia.org/datatype/centimetre>

4. (actually same info as 3)


PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT DISTINCT ?property ?value
WHERE {
  ?politician rdf:type dbo:Politician .
  ?politician ?property ?value .
  FILTER (?property != rdf:type)
}
ORDER BY ?property ?value


RESULTS:

property	value
http://dbpedia.org/ontology/Person/height	
"157.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"165.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"167.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"170.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"170.18"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"173.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"174.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"175.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"175.26"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"176.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"178.0"^^<http://dbpedia.org/datatype/centimetre>
http://dbpedia.org/ontology/Person/height	
"179.0"^^<http://dbpedia.org/datatype/centimetre>


5. 

PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?property COUNT(DISTINCT ?value) AS ?distinctValueCount
WHERE {
  ?politician rdf:type dbo:Politician .
  ?politician ?property ?value .
  FILTER (?property != rdf:type)
}
GROUP BY ?property
ORDER BY DESC(?distinctValueCount)

RESULTS:


property	distinctValueCount
http://www.w3.org/2002/07/owl#sameAs	
1131503
http://dbpedia.org/ontology/wikiPageWikiLink	
1125612
http://www.w3.org/2000/01/rdf-schema#label	
466200
http://dbpedia.org/ontology/description	
357955
http://dbpedia.org/ontology/termPeriod	
321171
http://xmlns.com/foaf/0.1/depiction	
178205
http://purl.org/dc/terms/subject	
175412
http://xmlns.com/foaf/0.1/isPrimaryTopicOf	
172950
http://www.w3.org/ns/prov#wasDerivedFrom	
172950
http://dbpedia.org/ontology/wikiPageExternalLink	
172119

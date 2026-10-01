1. Get all the properties that can be applied to instances of the Politician class (<http://dbpedia.org/ontology/Politician>)

```
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT DISTINCT ?p
WHERE 
{
   ?x rdf:type dbo:Politician .
   ?x ?p ?y
} 
LIMIT 10
```

```
@prefix res: <http://www.w3.org/2005/sparql-results#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ a res:ResultSet .
_:_ res:resultVariable "p" .
@prefix rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value rdf:type ] ] .
@prefix owl:	<http://www.w3.org/2002/07/owl#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ] .
@prefix foaf:	<http://xmlns.com/foaf/0.1/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value foaf:name ] ] .
@prefix rdfs:	<http://www.w3.org/2000/01/rdf-schema#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value rdfs:label ] ] .
@prefix dbp:	<http://dbpedia.org/property/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:honorificSuffix ] ] .
@prefix dbo:	<http://dbpedia.org/ontology/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:deathPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:deathPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:deathDate ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:birthPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:birthPlace ] ] .
```

2. Get all the properties, except rdf:type, that can be applied to instances of the Politician class

```
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT DISTINCT ?p
WHERE 
{
   ?x rdf:type dbo:Politician .
   ?x ?p ?y .
   FILTER(?p != rdf:type)
} 
LIMIT 10
```

```
@prefix res: <http://www.w3.org/2005/sparql-results#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ a res:ResultSet .
_:_ res:resultVariable "p" .
@prefix owl:	<http://www.w3.org/2002/07/owl#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ] .
@prefix foaf:	<http://xmlns.com/foaf/0.1/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value foaf:name ] ] .
@prefix rdfs:	<http://www.w3.org/2000/01/rdf-schema#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value rdfs:label ] ] .
@prefix dbp:	<http://dbpedia.org/property/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:honorificSuffix ] ] .
@prefix dbo:	<http://dbpedia.org/ontology/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:deathPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:deathPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:deathDate ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:birthPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:birthPlace ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:birthDate ] ] .
```

3. Which different values exist for the properties, except for rdf:type, applicable to the instances of Politician?

```
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT DISTINCT ?y
WHERE 
{
   ?x rdf:type dbo:Politician .
   ?x ?p ?y .
   FILTER(?p != rdf:type)
} 
LIMIT 10
```

```
@prefix res: <http://www.w3.org/2005/sparql-results#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ a res:ResultSet .
_:_ res:resultVariable "y" .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://rdf.freebase.com/ns/m.0h65mdl> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://yago-knowledge.org/resource/Abdul_Rahman_(politician)> ] ] .
@prefix wikidata:	<http://www.wikidata.org/entity/> .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value wikidata:Q4665623 ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://ar.dbpedia.org/resource/\u0639\u0628\u062F_\u0627\u0644\u0631\u062D\u0645\u0646_(\u0633\u064A\u0627\u0633\u064A)> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://ta.dbpedia.org/resource/\u0B8E\u0BAE\u0BCD._\u0B85\u0BAA\u0BCD\u0BA4\u0BC1\u0BB2\u0BCD_\u0BB0\u0BB9\u0BCD\u0BAE\u0BBE\u0BA9\u0BCD> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <https://global.dbpedia.org/id/4Kdw2> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://rdf.freebase.com/ns/m.025snm8> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://yago-knowledge.org/resource/Chris_Nelson_(politician)> ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value wikidata:Q5107573 ] ] .
_:_ res:solution [
      res:binding [ res:variable "y" ; res:value <http://de.dbpedia.org/resource/Chris_Nelson_(Politiker)> ] ] .
```

4. For each of these applicable properties, except for rdf:type, which different values do they take globally for all those instances?

```
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT DISTINCT ?p ?y
WHERE 
{
   ?x rdf:type dbo:Politician .
   ?x ?p ?y .
   FILTER(?p != rdf:type)
} 
LIMIT 10
```

```
@prefix res: <http://www.w3.org/2005/sparql-results#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ a res:ResultSet .
_:_ res:resultVariable "p" , "y" .
@prefix owl:	<http://www.w3.org/2002/07/owl#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://rdf.freebase.com/ns/m.0h65mdl> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://yago-knowledge.org/resource/Abdul_Rahman_(politician)> ] ] .
@prefix wikidata:	<http://www.wikidata.org/entity/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value wikidata:Q4665623 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://ar.dbpedia.org/resource/\u0639\u0628\u062F_\u0627\u0644\u0631\u062D\u0645\u0646_(\u0633\u064A\u0627\u0633\u064A)> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://ta.dbpedia.org/resource/\u0B8E\u0BAE\u0BCD._\u0B85\u0BAA\u0BCD\u0BA4\u0BC1\u0BB2\u0BCD_\u0BB0\u0BB9\u0BCD\u0BAE\u0BBE\u0BA9\u0BCD> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <https://global.dbpedia.org/id/4Kdw2> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://rdf.freebase.com/ns/m.025snm8> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://yago-knowledge.org/resource/Chris_Nelson_(politician)> ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value wikidata:Q5107573 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "y" ; res:value <http://de.dbpedia.org/resource/Chris_Nelson_(Politiker)> ] ] .
```

5. For each of these applicable properties, except for rdf:type, how many distinct values do they take globally for all those instances?

```
PREFIX dbo: <http://dbpedia.org/ontology/>
SELECT ?p (COUNT(DISTINCT ?y) AS ?count)
WHERE 
{
   ?x rdf:type dbo:Politician .
   ?x ?p ?y .
   FILTER(?p != rdf:type)
}
GROUP BY ?p
LIMIT 10
```

```
@prefix res: <http://www.w3.org/2005/sparql-results#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
_:_ a res:ResultSet .
_:_ res:resultVariable "p" , "count" .
@prefix owl:	<http://www.w3.org/2002/07/owl#> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value owl:sameAs ] ;
      res:binding [ res:variable "count" ; res:value 342556 ] ] .
@prefix foaf:	<http://xmlns.com/foaf/0.1/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value foaf:nick ] ;
      res:binding [ res:variable "count" ; res:value 513 ] ] .
@prefix dbp:	<http://dbpedia.org/property/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:loser ] ;
      res:binding [ res:variable "count" ; res:value 49 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:birthPlace ] ;
      res:binding [ res:variable "count" ; res:value 25533 ] ] .
@prefix dbo:	<http://dbpedia.org/ontology/> .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:birthName ] ;
      res:binding [ res:variable "count" ; res:value 12010 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:country ] ;
      res:binding [ res:variable "count" ; res:value 55 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:thumbnail ] ;
      res:binding [ res:variable "count" ; res:value 29786 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbo:committee ] ;
      res:binding [ res:variable "count" ; res:value 372 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:governor ] ;
      res:binding [ res:variable "count" ; res:value 1914 ] ] .
_:_ res:solution [
      res:binding [ res:variable "p" ; res:value dbp:n ] ;
      res:binding [ res:variable "count" ; res:value 28 ] ] .
```

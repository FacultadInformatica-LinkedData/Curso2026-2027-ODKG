# Hands-on assignment 5 – Self assessment

## Checklist

**Every RDF file:**

- [X] Has at least one owl:sameAs property that links to another dataset

## Comments on the self-assessment

**Revisions Regarding HO_evaluation_1**

- [X] URIs for individuals should be human-readable and meaningful.
    - For human-readability, we decide to revise the URI design. Particularly, it uses name (of parking, district and neighbourhood) in URI path, instead of their codes. 
    - For accomplish above design, we also revise the `csv/inventario-updated.csv` and `csv/occupacion.csv`
- [X] Fragment identifiers in URIs must not contain the "/" character.
- [X] Individuals are missing human-readable labels (rdfs:label).

**Additional Revision**

- Revise the test.py and its usages (run in command):
    - validate internal knowledge graph: `python test.py --queries queries.sparql`
    - validate internal data links: `python test.py --queries queries-with-links.sparql`
import morph_kgc

# generate the triples and load them to an RDFLib graph
g_rdflib = morph_kgc.materialize('/path/to/config.ini')
# work with the RDFLib graph
q_res = g_rdflib.query('SELECT DISTINCT ?classes WHERE { ?s a ?classes }')

# generate the triples and load them to Oxigraph
g_oxigraph = morph_kgc.materialize_oxigraph('/path/to/config.ini')
# work with Oxigraph
q_res = g_oxigraph.query('SELECT DISTINCT ?classes WHERE { ?s a ?classes }')

# the methods above also accept the config as a string
config = """
            [DataSource1]
            mappings: /path/to/mapping/mapping_file.rml.ttl
            db_url: mysql+pymysql://user:password@localhost:3306/db_name
         """
g_rdflib = morph_kgc.materialize(config)
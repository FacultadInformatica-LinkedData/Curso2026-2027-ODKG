"""Validate linked CSVs, RML, Turtle, and application queries against the sources."""
import csv
from collections import Counter, defaultdict
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import re
import unicodedata

from pyoxigraph import Literal, NamedNode, Store

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://madridnoise.linkeddata.es/"
MN = BASE + "ontology#"
XSD = "http://www.w3.org/2001/XMLSchema#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
LABEL = "http://www.w3.org/2000/01/rdf-schema#label"
SAME_AS = "http://www.w3.org/2002/07/owl#sameAs"
DC = "http://purl.org/dc/terms/"
RML = "http://semweb.mmlab.be/ns/rml#"
RR = "http://www.w3.org/ns/r2rml#"
NAMES = ("estaciones_acusticas", "contaminacion_acustica", "terrazas_hosteleria")
ROW_COUNTS = dict(zip(NAMES, (31, 78230, 6594)))
TRIPLE_COUNTS = dict(zip(NAMES, (308, 1017217, 53220)))
LINK_COUNTS = dict(zip(NAMES, (17, 17, 150)))


def read_csv(path, **kwargs):
    with path.open(encoding=kwargs.pop("encoding", "utf-8-sig"), newline="") as f:
        reader = csv.DictReader(f, **kwargs)
        assert len(reader.fieldnames) == len(set(reader.fieldnames)), path
        rows = list(reader)
        assert all(None not in row for row in rows), path
        return reader.fieldnames, rows


def iri(kind, identifier):
    return NamedNode(BASE + "resource/" + kind + "/" + identifier)


def lit(value, datatype=None, language=None):
    return Literal(value, datatype=NamedNode(XSD + datatype) if datatype else None,
                   language=language)


def term_key(term):
    if isinstance(term, NamedNode):
        return ("iri", term.value)
    assert isinstance(term, Literal), term
    value = term.value
    datatype = term.datatype.value
    if datatype == XSD + "decimal":
        value = Decimal(value)
        assert value.is_finite(), term
    elif datatype == XSD + "integer":
        value = int(value)
    elif datatype == XSD + "boolean":
        assert value in ("true", "false", "1", "0"), term
        value = value in ("true", "1")
    return ("literal", datatype, term.language, value)


def objects(store, subject, predicate):
    return [quad.object for quad in store.quads_for_pattern(
        subject, NamedNode(predicate), None, None)]


def check_entity(store, subject, expected, checked):
    actual = defaultdict(set)
    for quad in store.quads_for_pattern(subject, None, None, None):
        actual[quad.predicate.value].add(term_key(quad.object))
    wanted = {predicate: {term_key(value) for value in values}
              for predicate, values in expected.items()}
    assert dict(actual) == wanted, (subject.value, dict(actual), wanted)
    checked.add(subject.value)


def add_if_present(expected, predicate, value, datatype):
    if value:
        expected[predicate] = [lit(value, datatype)]


def normalized(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub("[^A-Z0-9]", "", value.upper())


def check_inputs(evidence):
    rows = {}
    operation_counts = {}
    for name in NAMES:
        columns, original = read_csv(ROOT / "csv" / (name + "-updated.csv"))
        linked_columns, linked = read_csv(ROOT / "csv" / (name + "-with-links.csv"))
        assert len(original) == len(linked) == ROW_COUNTS[name], name
        assert [c for c in linked_columns if c in columns] == columns, name
        for index, (source, exported) in enumerate(zip(original, linked), 2):
            assert all(exported[key] == value for key, value in source.items()), (
                name, index, source, exported)
        rows[name] = linked
        ops = json.loads((ROOT / "lodrefine" / (name + "-with-links.json")).read_text())
        assert isinstance(ops, list) and ops, name
        for op in ops:
            assert op["op"].startswith("core/"), (name, op)
            if op["op"] == "core/recon":
                assert op["config"]["autoMatch"] is False, (name, op)
        operation_counts[name] = len(ops)

    assert len(evidence["districts"]) == 21
    assert len(evidence["neighbourhoods"]) == 129
    assert len(evidence["station_districts"]) == 31
    for value in evidence["districts"].values():
        assert "Q3032114" in value["evidence"]["P31"]
        assert "Q2807" in value["evidence"]["P131"]
    for value in evidence["neighbourhoods"].values():
        assert "Q10267336" in value["wikidata_P31"]
        assert value["expected_district_qid"] in value["wikidata_P131"]

    district_labels, neighbourhood_labels = {}, {}
    for row in rows["terrazas_hosteleria"]:
        did, nid = row["district_id"], row["neighbourhood_id"]
        assert row["district_wikidata"] == evidence["districts"][did]["wikidata"]
        neighbourhood = evidence["neighbourhoods"][nid]
        assert row["neighbourhood_wikidata"] == neighbourhood["uri"]
        assert neighbourhood["district_id"] == did
        assert row["neighbourhood_label"] == neighbourhood["source_label"]
        assert district_labels.setdefault(did, row["district_label"]) == row["district_label"]
        assert neighbourhood_labels.setdefault(nid, row["neighbourhood_label"]) == row["neighbourhood_label"]
    assert len(district_labels) == 21 and len(neighbourhood_labels) == 129
    _, raw_stations = read_csv(ROOT / "csv" / "estaciones_acusticas.csv",
                               encoding="cp1252", delimiter=";")
    source_districts = {row["ESTACIÓN"].strip(): row["DISTRITO"] for row in raw_stations}
    stations = {row["station_code"]: row for row in rows["estaciones_acusticas"]}
    assert len(stations) == 31
    for code, row in stations.items():
        reviewed = evidence["station_districts"][code]
        assert row["district_id"] == reviewed["district_id"]
        assert row["district_label"] == district_labels[row["district_id"]]
        assert normalized(source_districts[code]) == normalized(row["district_label"])
        assert row["district_wikidata"] == reviewed["wikidata_uri"]
    for row in rows["contaminacion_acustica"]:
        station = stations[row["station_code"]]
        for column in ("district_id", "district_label", "district_wikidata"):
            assert row["station_" + column] == station[column], row["observation_id"]
    assert Counter(row["percentile_order_violation"] for row in rows["contaminacion_acustica"]) == {
        "true": 213, "false": 78000, "": 17}
    for row in rows["contaminacion_acustica"]:
        assert bool(row["laeq"])
        if not row["percentile_order_violation"]:
            assert all(not row[key] for key in ("l1", "l10", "l50", "l90", "l99"))
    assert sum(not row["latitude"] and not row["longitude"]
               for row in rows["terrazas_hosteleria"]) == 60
    return rows, operation_counts


def check_mappings():
    counts = {}
    for name in NAMES:
        store = Store()
        store.load(ROOT / "mappings" / (name + "-with-links.rml"), "text/turtle")
        triples_maps = list(store.quads_for_pattern(
            None, NamedNode(RDF_TYPE), NamedNode(RR + "TriplesMap"), None))
        assert triples_maps, name
        for quad in store.quads_for_pattern(None, NamedNode(RML + "source"), None, None):
            source = quad.object.value
            assert source == "csv/periods.csv" or source.endswith("-with-links.csv"), source
            assert (ROOT / source).is_file(), source
        assert list(store.quads_for_pattern(None, NamedNode(RR + "predicate"), NamedNode(SAME_AS), None)), name
        counts[name] = len(triples_maps)
    return counts


def check_dataset(store, identifier, checked):
    subject = NamedNode(BASE + "dataset/" + identifier)
    source_ids = {"stations": "211346-0-estaciones-acusticas",
                  "daily-noise": "215885-0-contaminacion-ruido",
                  "terraces": "200085-0-censo-locales"}
    titles = {"stations": "Madrid acoustic station catalog (Linked Data)",
              "daily-noise": "Madrid daily noise measurements (Linked Data)",
              "terraces": "Madrid hospitality terraces (Linked Data)"}
    descriptions = objects(store, subject, DC + "description")
    assert len(descriptions) == 1 and descriptions[0].language == "en" and descriptions[0].value
    source = NamedNode("https://datos.madrid.es/dataset/" + source_ids[identifier])
    check_entity(store, subject, {
        RDF_TYPE: [NamedNode("http://www.w3.org/ns/dcat#Dataset")],
        LABEL: [lit(titles[identifier], language="en")],
        DC + "title": [lit(titles[identifier], language="en")],
        DC + "description": descriptions,
        DC + "source": [source],
        "http://www.w3.org/ns/prov#wasDerivedFrom": [source],
        DC + "license": [NamedNode("https://creativecommons.org/licenses/by/4.0/")],
        DC + "rightsHolder": [NamedNode("http://datos.gob.es/recurso/sector-publico/org/Organismo/L01280796")],
        DC + "created": [lit("2026-10-25", "date")],
    }, checked)


def check_rdf(name, rows, evidence):
    store = Store()
    store.load(ROOT / "rdf" / (name + "-with-links.ttl"), "text/turtle")
    assert len(store) == TRIPLE_COUNTS[name], (name, len(store))
    checked = set()
    station_rows = rows["estaciones_acusticas"] if name != "terrazas_hosteleria" else []
    for row in station_rows:
        check_entity(store, iri("station", row["station_code"]), {
            RDF_TYPE: [NamedNode(MN + "NoiseMonitoringStation")],
            LABEL: [lit(row["station_name"], language="es")],
            MN + "stationCode": [lit(row["station_code"])],
            MN + "stationName": [lit(row["station_name"])],
            MN + "latitude": [lit(row["latitude"], "decimal")],
            MN + "longitude": [lit(row["longitude"], "decimal")],
            DC + "isPartOf": [NamedNode(BASE + "dataset/stations")],
            DC + "spatial": [iri("district", row["district_id"])],
        }, checked)
    if name == "contaminacion_acustica":
        _, periods = read_csv(ROOT / "csv" / "periods.csv")
        for row in periods:
            check_entity(store, iri("period", row["period"]), {
                RDF_TYPE: [NamedNode(MN + "DayPeriod")],
                LABEL: [lit(row["label"], language="en")],
                MN + "periodCode": [lit(row["period"])],
            }, checked)
        for row in rows[name]:
            expected = {
                RDF_TYPE: [NamedNode(MN + "DailyNoiseObservation")],
                LABEL: [lit("Noise observation {station_code} {date} {period}".format(**row), language="en")],
                MN + "recordedAt": [iri("station", row["station_code"])],
                MN + "forPeriod": [iri("period", row["period"])],
                MN + "observationDate": [lit(row["date"], "date")],
                DC + "isPartOf": [NamedNode(BASE + "dataset/daily-noise")],
            }
            for column, predicate in {"laeq": "laeq", "l1": "las01", "l10": "las10",
                                      "l50": "las50", "l90": "las90", "l99": "las99"}.items():
                add_if_present(expected, MN + predicate, row[column], "decimal")
            add_if_present(expected, MN + "percentileOrderViolation", row["percentile_order_violation"], "boolean")
            check_entity(store, iri("observation", row["observation_id"]), expected, checked)
        check_dataset(store, "daily-noise", checked)
    if name == "terrazas_hosteleria":
        for row in rows[name]:
            expected = {
                RDF_TYPE: [NamedNode(MN + "Terrace")],
                LABEL: [lit(row["terrace_label"], language="en")],
                MN + "terraceId": [lit(row["terrace_id"], "integer")],
                MN + "hasDistrict": [iri("district", row["district_id"])],
                MN + "hasNeighbourhood": [iri("neighbourhood", row["neighbourhood_id"])],
                DC + "isPartOf": [NamedNode(BASE + "dataset/terraces")],
            }
            for column in ("latitude", "longitude"):
                add_if_present(expected, MN + column, row[column], "decimal")
            check_entity(store, iri("terrace", row["terrace_id"]), expected, checked)
        neighbourhood_rows = {row["neighbourhood_id"]: row for row in rows[name]}
        for nid, row in neighbourhood_rows.items():
            check_entity(store, iri("neighbourhood", nid), {
                RDF_TYPE: [NamedNode(MN + "Neighbourhood")],
                LABEL: [lit(row["neighbourhood_label"], language="es")],
                SAME_AS: [NamedNode(evidence["neighbourhoods"][nid]["uri"])],
                DC + "isPartOf": [iri("district", row["district_id"])],
            }, checked)
        check_dataset(store, "terraces", checked)
    else:
        check_dataset(store, "stations", checked)
    district_rows = {row["district_id"]: row for row in
                     (rows[name] if name == "terrazas_hosteleria" else station_rows)}
    for did, row in district_rows.items():
        check_entity(store, iri("district", did), {
            RDF_TYPE: [NamedNode(MN + "District")],
            LABEL: [lit(row["district_label"], language="es")],
            SAME_AS: [NamedNode(evidence["districts"][did]["wikidata"])],
        }, checked)
    assert {quad.subject.value for quad in store} == checked, name
    links = list(store.quads_for_pattern(None, NamedNode(SAME_AS), None, None))
    assert len(links) == LINK_COUNTS[name], (name, len(links))
    for link in links:
        assert link.subject.value.startswith(BASE + "resource/")
        assert isinstance(link.object, NamedNode)
        assert re.fullmatch(r"http://www\.wikidata\.org/entity/Q[0-9]+", link.object.value)
    return store


def check_queries(store, rows):
    text = (ROOT / "rdf" / "queries-with-links.sparql").read_text()
    queries = [part for part in re.split(r"(?=^# L[0-9]+\.)", text, flags=re.MULTILINE)
               if re.search(r"^SELECT\b", part, flags=re.MULTILINE)]
    assert len(queries) == 5, len(queries)
    results = []
    for number, (query, expected_count) in enumerate(zip(queries, (31, 31, 6534, 21, 2)), 1):
        body = "\n".join(line for line in query.splitlines() if not line.startswith("#"))
        assert "owl:sameAs" in body and re.search(r"\bmn:[A-Za-z]+", body)
        result = list(store.query(query))
        assert len(result) == expected_count, (number, len(result), expected_count)
        results.append(result)
    nights = defaultdict(list)
    for row in rows["contaminacion_acustica"]:
        if row["period"] == "N":
            nights[row["station_code"]].append(Decimal(row["laeq"]))
    for result in results[1]:
        values = nights[result["code"].value]
        assert int(result["nightsWithData"].value) == len(values)
        expected_mean = (sum(values) / len(values)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        assert Decimal(result["meanReportedNightLAeq"].value) == expected_mean
    assert sum(int(row["registeredTerraces"].value) for row in results[3]) == 6594
    assert sum(int(row["locatedTerraces"].value) for row in results[3]) == 6534
    assert {row["class"].value: int(row["linkedResources"].value) for row in results[4]} == {
        MN + "District": 21, MN + "Neighbourhood": 129}
    assert all(row["linkedResources"].value == row["wikidataIdentities"].value for row in results[4])
    return [len(result) for result in results]


def main():
    evidence = json.loads((ROOT / "linking" / "reconciliation-evidence.json").read_text())
    rows, operation_counts = check_inputs(evidence)
    mapping_counts = check_mappings()
    union = Store()
    counts = {}
    for name in NAMES:
        store = check_rdf(name, rows, evidence)
        counts[name] = {"rows": len(rows[name]), "triples": len(store), "sameAs": LINK_COUNTS[name]}
        union.extend(store)
        print(name + ": source values, labels, datatypes, omissions and links PASS", flush=True)
    assert len(union) == 1070386, len(union)
    query_counts = check_queries(union, rows)
    print(json.dumps({"status": "PASS", "datasets": counts,
                      "openrefine_operation_counts": operation_counts,
                      "rml_triples_map_counts": mapping_counts,
                      "union_triples": len(union), "distinct_identity_links": 150,
                      "application_query_rows": query_counts}, indent=2))


if __name__ == "__main__":
    main()

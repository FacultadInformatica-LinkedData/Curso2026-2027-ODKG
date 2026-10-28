"""Validate a generated TTL; optionally apply the reviewed postal-code fixes."""

import argparse
import csv
import io
from pathlib import Path
import subprocess
import tempfile


CUSTOM_SHAPES = r'''@prefix dbd: <https://example.org/db-delays/ontology/#> .
@prefix shape: <https://example.org/db-delays/shapes/#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Selected manual rules from shapes_ideas.md. Optional source fields may be absent.
# No global uniqueness or delay/status consistency constraint is imposed.
shape:LabelShape a sh:NodeShape ;
    sh:targetClass dbd:TrainStop, dbd:Station, dbd:City, dbd:State ;
    sh:property [
        sh:path rdfs:label ; sh:minCount 1 ; sh:maxCount 1 ;
        sh:datatype xsd:string ; sh:pattern "\\S" ;
        sh:message "Each resource must have exactly one non-blank string label."@en
    ] .

shape:TrainStopTimeShape a sh:NodeShape ;
    sh:targetClass dbd:TrainStop ;
    sh:property [
        sh:path dbd:plannedArrival ;
        sh:lessThanOrEquals dbd:plannedDeparture ;
        sh:message "Planned arrival must be no later than planned departure when both are present."@en
    ] ;
    sh:property [
        sh:path dbd:updatedArrival ;
        sh:lessThanOrEquals dbd:updatedDeparture ;
        sh:message "Updated arrival must be no later than updated departure when both are present."@en
    ] .

shape:StationValueShape a sh:NodeShape ;
    sh:targetClass dbd:Station ;
    sh:property [
        sh:path dbd:postalCode ; sh:datatype xsd:string ; sh:pattern "^[0-9]{5}$" ;
        sh:message "A German postal code must be a string of exactly five digits."@en
    ] ;
    sh:property [
        sh:path dbd:longitude ; sh:minInclusive -180 ; sh:maxInclusive 180 ;
        sh:message "Longitude must be between -180 and 180 degrees."@en
    ] ;
    sh:property [
        sh:path dbd:latitude ; sh:minInclusive -90 ; sh:maxInclusive 90 ;
        sh:message "Latitude must be between -90 and 90 degrees."@en
    ] .

# IF plannedArrival is absent THEN previousStations must be absent.
# This hypothesis is a warning, not proof of a first station or an equivalence.
shape:MissingArrivalPathShape a sh:NodeShape ;
    sh:targetClass dbd:TrainStop ; sh:severity sh:Warning ;
    sh:message "Check this observation: planned arrival is missing but a previous-stations path is present."@en ;
    sh:or (
        [ sh:property [ sh:path dbd:plannedArrival ; sh:minCount 1 ] ]
        [ sh:property [ sh:path dbd:previousStations ; sh:maxCount 0 ] ]
    ) .
'''


def regenerate_shapes(ontology_path, destination, astrea_dir, java):
    """Run the actual Astrea library, then add explicit repairs and our rules."""
    from rdflib import Graph, Namespace, OWL, RDF, RDFS

    libraries = astrea_dir / "extracted" / "BOOT-INF" / "lib"
    catalogue = astrea_dir / "catalog" / "dataset.ttl"
    if not (libraries / "astrea-1.2.1.jar").is_file() or not catalogue.is_file():
        raise FileNotFoundError("Official Astrea library/dependencies or catalogue missing in --astrea-dir")
    source = astrea_dir / "GenerateAstrea.java"
    raw_path = astrea_dir / "shapes-generated.ttl"
    source.write_text('''import astrea.generators.OwlGenerator;
import java.io.*;
import org.apache.jena.rdf.model.*;
class GenerateAstrea {
    public static void main(String[] args) throws Exception {
        OwlGenerator generator = new OwlGenerator(new File(args[0]));
        System.out.println("Astrea mapping queries: " + generator.getQueries().size());
        if (generator.getQueries().isEmpty()) throw new IllegalStateException("No mapping queries");
        Model ontology = ModelFactory.createDefaultModel();
        try (InputStream input = new FileInputStream(args[1])) { ontology.read(input, null, "TURTLE"); }
        Model shapes = generator.fromModel(ontology);
        if (shapes.isEmpty()) throw new IllegalStateException("No generated shapes");
        try (OutputStream output = new FileOutputStream(args[2])) { shapes.write(output, "TURTLE"); }
        System.out.println("Ontology triples: " + ontology.size());
        System.out.println("Generated shape triples: " + shapes.size());
    }
}
''', encoding="utf-8")
    command = [str(java), "--class-path", str(libraries / "*"), str(source),
               str(catalogue), str(ontology_path), str(raw_path)]
    log_path = astrea_dir / "generation.log"
    with log_path.open("w", encoding="utf-8") as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(("Astrea mapping queries:", "Ontology triples:", "Generated shape triples:")):
            print(line)
    ontology = Graph().parse(ontology_path, format="turtle")
    raw = Graph().parse(raw_path, format="turtle")
    sh = Namespace("http://www.w3.org/ns/shacl#")
    repairs = Graph()
    repairs.bind("dbd", Namespace("https://example.org/db-delays/ontology/#"))
    repairs.bind("sh", sh)
    properties = set(ontology.subjects(RDF.type, OWL.ObjectProperty)) | set(
        ontology.subjects(RDF.type, OWL.DatatypeProperty)
    )
    for prop in sorted(properties, key=str):
        matches = {
            shape for label in ontology.objects(prop, RDFS.label)
            for shape in raw.subjects(sh.name, label)
            if (shape, RDF.type, sh.PropertyShape) in raw
        }
        if len(matches) != 1:
            raise ValueError(f"Ambiguous or missing Astrea property shape: {prop}")
        shape = matches.pop()
        paths = set(raw.objects(shape, sh.path))
        if paths and paths != {prop}:
            raise ValueError(f"Unexpected generated path: {prop}")
        if not paths:
            repairs.add((shape, sh.path, prop))
        for domain in ontology.objects(prop, RDFS.domain):
            targets = set(raw.subjects(sh.targetClass, domain))
            if len(targets) != 1:
                raise ValueError(f"Ambiguous or missing Astrea node shape: {domain}")
            node = targets.pop()
            if (node, sh.property, shape) not in raw:
                repairs.add((node, sh.property, shape))
    text = (
        "# SECTION 1: Unmodified Astrea 1.2.1 generated output.\n"
        "# Input: ../ontology/db-delays.ttl. See README.md for provenance.\n\n"
        + raw_path.read_text(encoding="utf-8")
        + "\n# SECTION 2: Explicit repairs to the released generator output.\n\n"
        + repairs.serialize(format="turtle")
        + "\n# SECTION 3: Manually added dataset-specific constraints.\n\n"
        + CUSTOM_SHAPES
    )
    # Check syntax and meta-SHACL before replacing the previous deliverable.
    from pyshacl import validate
    assembled = Graph().parse(data=text, format="turtle")
    validate(Graph(), shacl_graph=assembled, meta_shacl=True, inference="none")
    destination.write_text(text, encoding="utf-8")
    print(f"Astrea structural repairs: {len(repairs)}; saved: {destination}")


def fix_source_csv(source_path, corrections_path):
    """Persist reviewed postcode replacements in every matching source row."""
    original = source_path.read_bytes()
    encoding = "utf-8-sig" if original.startswith(b"\xef\xbb\xbf") else "utf-8"
    reader = csv.DictReader(io.StringIO(original.decode(encoding), newline=""))
    fields = reader.fieldnames
    if not fields or not {"eva_nr", "zip"}.issubset(fields):
        raise ValueError("Source CSV must contain eva_nr and zip columns")
    rows = list(reader)
    with corrections_path.open(encoding="utf-8-sig", newline="") as stream:
        corrections = {}
        for correction in csv.DictReader(stream):
            eva = correction["eva_number"]
            replacement = correction["new_postal_code"]
            if eva in corrections:
                raise ValueError(f"Duplicate reviewed station: {eva}")
            if len(replacement) != 5 or not replacement.isascii() or not replacement.isdigit():
                raise ValueError(f"Invalid reviewed postal code: {eva}")
            if not correction.get("source_url") or not correction.get("verified_on"):
                raise ValueError(f"Missing review evidence: {eva}")
            corrections[eva] = correction
    changed_rows = 0
    changed_stations = set()
    for row in rows:
        review = corrections.get(row["eva_nr"])
        if review is None or row["zip"] == review["new_postal_code"]:
            continue
        if row["zip"] != review["old_postal_code"]:
            raise ValueError(f"Unexpected source postal code for station {row['eva_nr']}: {row['zip']}")
        row["zip"] = review["new_postal_code"]
        changed_rows += 1
        changed_stations.add(row["eva_nr"])
    if changed_rows:
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=fields,
                                lineterminator="\r\n" if b"\r\n" in original else "\n")
        writer.writeheader()
        writer.writerows(rows)
        content = output.getvalue().encode(encoding)
        # Verify all columns except zip, row ordering, and number of rows.
        before = list(csv.DictReader(io.StringIO(original.decode(encoding), newline="")))
        after = list(csv.DictReader(io.StringIO(content.decode(encoding), newline="")))
        if len(before) != len(after):
            raise ValueError("CSV row count changed")
        for old, new in zip(before, after):
            if any(old[field] != new[field] for field in fields if field != "zip"):
                raise ValueError("Unexpected source changes outside the zip column")
        with tempfile.NamedTemporaryFile(dir=source_path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        try:
            temporary.replace(source_path)
        finally:
            temporary.unlink(missing_ok=True)
    print(f"CSV rows: {len(rows)}; zip values corrected: {changed_rows}; stations: {len(changed_stations)}")
    print("Next: regenerate the linked RDF with generate_graph.py --with-links, then validate it.")


def main():
    group = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data", type=Path,
        default=group / "rdf" / "knowledge-graph-with-links.ttl",
        help="Input TTL (default: the main linked graph generated from the linked CSV).",
    )
    parser.add_argument("--shapes", type=Path, default=group / "shacl" / "shapes.ttl")
    parser.add_argument("--report", type=Path, default=group / "shacl" / "report.ttl")
    parser.add_argument("--fix-source-csv", action="store_true", help="Apply reviewed zip corrections to the source CSV and exit; regenerate RDF afterwards.")
    parser.add_argument("--source-csv", type=Path, default=group / "csv" / "DBtrainrides-with-links.csv")
    parser.add_argument("--regenerate-shapes", action="store_true", help="Run the official Astrea library and rebuild shapes.ttl.")
    parser.add_argument("--ontology", type=Path, default=group / "ontology" / "db-delays.ttl")
    parser.add_argument("--astrea-dir", type=Path, default=group.parents[1] / "tmp" / "astrea")
    parser.add_argument("--java", default="java", help="Java executable with source-file execution support.")
    parser.add_argument(
        "--refresh-corrections", action="store_true",
        help="Rewrite the reviewed CSV to contain only replacements applied to this input.",
    )
    parser.add_argument(
        "--apply-reviewed-corrections", action="store_true",
        help="Apply only old/new postal-code replacements listed in the reviewed CSV.",
    )
    parser.add_argument(
        "--corrections", type=Path,
        default=group / "shacl" / "postal-code-corrections.csv",
    )
    parser.add_argument(
        "--fixed-data", type=Path,
        default=group / "rdf" / "knowledge-graph-with-links-validated.ttl",
    )
    parser.add_argument(
        "--before-report", type=Path, default=group / "shacl" / "report-before.ttl",
    )
    args = parser.parse_args()
    if args.fix_source_csv:
        if args.source_csv.resolve() == args.corrections.resolve():
            parser.error("Source CSV and correction list must be different files")
        fix_source_csv(args.source_csv, args.corrections)
        return
    if args.refresh_corrections and not args.apply_reviewed_corrections:
        parser.error("--refresh-corrections requires --apply-reviewed-corrections")

    # Imports follow argument parsing so --help works without dependencies.
    from pyshacl import validate
    from rdflib import Graph, Literal, Namespace, RDF, URIRef, XSD

    inputs = [args.data, args.ontology if args.regenerate_shapes else args.shapes]
    outputs = [args.report]
    if args.regenerate_shapes:
        outputs.append(args.shapes)
    if args.apply_reviewed_corrections:
        inputs.append(args.corrections)
        outputs.extend([args.fixed_data, args.before_report])
    input_paths = {path.resolve() for path in inputs}
    output_paths = [path.resolve() for path in outputs]
    if len(set(output_paths)) != len(output_paths) or input_paths.intersection(output_paths):
        parser.error("Output paths must be distinct and must not overwrite any input.")

    if args.regenerate_shapes:
        regenerate_shapes(args.ontology.resolve(), args.shapes, args.astrea_dir.resolve(), args.java)
    data = Graph().parse(args.data, format="turtle")
    original_triples = set(data)
    shapes = Graph().parse(args.shapes, format="turtle")
    sh = Namespace("http://www.w3.org/ns/shacl#")
    dbd = Namespace("https://example.org/db-delays/ontology/#")

    def check(graph, destination):
        conforms, report, _ = validate(
            graph, shacl_graph=shapes, inference="none", meta_shacl=True
        )
        report.serialize(destination=str(destination), format="turtle")
        results = list(report.subjects(RDF.type, sh.ValidationResult))
        violations = sum(report.value(r, sh.resultSeverity) == sh.Violation for r in results)
        warnings = sum(report.value(r, sh.resultSeverity) == sh.Warning for r in results)
        print(f"Conforms: {conforms}; violations: {violations}; warnings: {warnings}")
        print(f"Report: {destination}")
        return conforms, report

    print(f"Input: {args.data}; triples: {len(data)}")
    if not args.apply_reviewed_corrections:
        conforms, _ = check(data, args.report)
        raise SystemExit(0 if conforms else 1)

    _, before_report = check(data, args.before_report)
    postal_findings = {
        (before_report.value(result, sh.focusNode), before_report.value(result, sh.value))
        for result in before_report.subjects(RDF.type, sh.ValidationResult)
        if before_report.value(result, sh.resultPath) == dbd.postalCode
        and before_report.value(result, sh.sourceConstraintComponent) == sh.PatternConstraintComponent
    }
    with args.corrections.open(encoding="utf-8-sig", newline="") as stream:
        corrections = list(csv.DictReader(stream))
    seen = set()
    changes = []
    applied_rows = []
    for row in corrections:
        eva = row["eva_number"]
        if eva in seen:
            raise ValueError(f"Duplicate correction for station {eva}")
        seen.add(eva)
        station = URIRef("https://example.org/db-delays/resource/Station/" + eva)
        values = set(data.objects(station, dbd.postalCode))
        if not values:
            print(f"Skipped {eva}: no postal code in this input")
            continue
        if len(values) != 1:
            print(f"Skipped {eva}: multiple postal codes require review")
            continue
        old = values.pop()
        if not isinstance(old, Literal) or old.language or old.datatype not in (None, XSD.string):
            print(f"Skipped {eva}: unexpected datatype requires review")
            continue
        if str(old) == row["new_postal_code"]:
            continue  # Already corrected in the updated dataset.
        if str(old) != row["old_postal_code"]:
            print(f"Skipped {eva}: value {old!s} differs from the reviewed old value")
            continue
        if (station, old) not in postal_findings:
            continue
        replacement = row["new_postal_code"]
        if len(replacement) != 5 or not replacement.isascii() or not replacement.isdigit():
            raise ValueError(f"Invalid reviewed replacement for station {eva}")
        if not row.get("source_url") or not row.get("verified_on"):
            raise ValueError(f"Missing review evidence for station {eva}")
        changes.append((station, old, Literal(replacement, datatype=old.datatype)))
        applied_rows.append(row)

    for station, old, new in changes:
        data.remove((station, dbd.postalCode, old))
        data.add((station, dbd.postalCode, new))
    if original_triples - set(data) != {(s, dbd.postalCode, old) for s, old, new in changes}:
        raise ValueError("Unexpected triple removals")
    if set(data) - original_triples != {(s, dbd.postalCode, new) for s, old, new in changes}:
        raise ValueError("Unexpected triple additions")
    data.serialize(destination=str(args.fixed_data), format="turtle")
    print(f"Reviewed replacements applied: {len(changes)}; saved: {args.fixed_data}")
    saved = Graph().parse(args.fixed_data, format="turtle")
    from rdflib.compare import isomorphic
    if not isomorphic(saved, data):
        raise ValueError("Saved graph differs from the corrected graph")
    if args.refresh_corrections:
        fields = ["eva_number", "station", "old_postal_code", "new_postal_code", "source_url", "verified_on"]
        with args.corrections.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(sorted(applied_rows, key=lambda row: row["eva_number"]))
        print(f"Correction list regenerated: {len(applied_rows)} rows")
    # Any new or unresolved issues remain visible in the report and exit status.
    conforms, _ = check(saved, args.report)
    raise SystemExit(0 if conforms else 1)


if __name__ == "__main__":
    main()

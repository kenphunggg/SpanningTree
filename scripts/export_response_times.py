#!/usr/bin/env python3
"""Export one CSV row per PingApp request from OMNeT++ vector files."""

from __future__ import annotations

import argparse
import csv
import glob
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


REQUIRED_VECTOR_NAMES = {"pingTxSeq:vector", "pingRxSeq:vector", "rtt:vector"}


@dataclass(frozen=True)
class Sample:
    event: str | None
    time: str
    value: str


@dataclass
class VectorDefinition:
    module: str
    name: str
    columns: str
    samples: list[Sample]


@dataclass
class VectorFile:
    path: Path
    run: str
    config: str
    attributes: dict[str, str]
    config_entries: dict[str, str]
    vectors: dict[str, VectorDefinition]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Join PingApp pingTxSeq, pingRxSeq, and rtt vectors and write one "
            "CSV row for every transmitted ping, including lost requests."
        )
    )
    parser.add_argument(
        "inputs",
        nargs="*",
        help=(
            "Input .vec files, directories, or glob patterns. "
            "Default: simulations/results/*.vec"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="simulations/results/response-times.csv",
        help="Output CSV path (default: simulations/results/response-times.csv)",
    )
    parser.add_argument(
        "--module",
        action="append",
        help=(
            "Only export an exact PingApp module path. May be repeated. "
            "By default, all modules containing the required vectors are exported."
        ),
    )
    return parser.parse_args()


def expand_inputs(arguments: list[str]) -> list[Path]:
    patterns = arguments or ["simulations/results/*.vec"]
    paths: set[Path] = set()

    for argument in patterns:
        candidate = Path(argument)
        if candidate.is_dir():
            paths.update(path.resolve() for path in candidate.glob("*.vec"))
            continue

        matches = glob.glob(argument, recursive=True)
        if matches:
            paths.update(
                Path(match).resolve()
                for match in matches
                if Path(match).is_file() and Path(match).suffix.lower() == ".vec"
            )
        elif candidate.is_file() and candidate.suffix.lower() == ".vec":
            paths.add(candidate.resolve())

    return sorted(paths)


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    value = value.replace(r"\"", '"').replace(r"\\", "\\")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def sample_from_fields(columns: str, fields: list[str], path: Path, line_no: int) -> Sample:
    if len(columns) != len(fields):
        raise ValueError(
            f"{path}:{line_no}: expected {len(columns)} vector fields "
            f"for columns {columns!r}, found {len(fields)}"
        )

    values = dict(zip(columns, fields))
    if "T" not in values or "V" not in values:
        raise ValueError(
            f"{path}:{line_no}: vector columns {columns!r} do not contain T and V"
        )
    return Sample(event=values.get("E"), time=values["T"], value=values["V"])


def parse_vector_file(path: Path) -> VectorFile:
    run = ""
    config = ""
    attributes: dict[str, str] = {}
    config_entries: dict[str, str] = {}
    vectors: dict[str, VectorDefinition] = {}

    with path.open("r", encoding="utf-8", errors="replace") as source:
        for line_no, raw_line in enumerate(source, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("run "):
                run = line[4:].strip()
                continue

            if line.startswith("attr "):
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    attributes[parts[1]] = unquote(parts[2])
                    if parts[1] == "configname":
                        config = attributes[parts[1]]
                continue

            if line.startswith("config "):
                parts = line.split(maxsplit=2)
                if len(parts) == 3:
                    config_entries[parts[1]] = unquote(parts[2])
                continue

            if line.startswith("vector "):
                parts = line.split()
                if len(parts) < 5:
                    raise ValueError(f"{path}:{line_no}: malformed vector declaration")
                vector_id, module, name, columns = parts[1], parts[2], parts[3], parts[4]
                vectors[vector_id] = VectorDefinition(module, name, columns, [])
                continue

            first_field = line.split(maxsplit=1)[0]
            definition = vectors.get(first_field)
            if definition is None:
                continue

            fields = line.split()
            definition.samples.append(
                sample_from_fields(definition.columns, fields[1:], path, line_no)
            )

    if not run:
        raise ValueError(f"{path}: no run declaration found")

    return VectorFile(
        path=path,
        run=run,
        config=config,
        attributes=attributes,
        config_entries=config_entries,
        vectors=vectors,
    )


def format_decimal(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def find_destination(vector_file: VectorFile, module: str) -> str:
    relative_module = module.split(".", 1)[1] if "." in module else module
    suffix = f"{relative_module}.destAddr"
    for key, value in vector_file.config_entries.items():
        if key.lstrip("*") == f".{suffix}" or key.endswith(suffix):
            return value
    return ""


def find_iteration_variable(vector_file: VectorFile, name: str) -> str:
    iteration_variables = vector_file.attributes.get("iterationvars", "")
    match = re.search(rf"(?:^|,\s*)\${re.escape(name)}=([^,]+)", iteration_variables)
    return match.group(1).strip() if match else ""


def group_ping_vectors(
    vector_file: VectorFile,
) -> dict[str, dict[str, VectorDefinition]]:
    grouped: dict[str, dict[str, VectorDefinition]] = defaultdict(dict)
    for definition in vector_file.vectors.values():
        if definition.name in REQUIRED_VECTOR_NAMES:
            grouped[definition.module][definition.name] = definition
    return {
        module: definitions
        for module, definitions in grouped.items()
        if REQUIRED_VECTOR_NAMES.issubset(definitions)
    }


def event_key(sample: Sample) -> tuple[str | None, str]:
    return sample.event, sample.time


def rows_for_module(
    vector_file: VectorFile,
    module: str,
    definitions: dict[str, VectorDefinition],
) -> list[dict[str, str]]:
    tx_samples = definitions["pingTxSeq:vector"].samples
    rx_samples = definitions["pingRxSeq:vector"].samples
    rtt_samples = definitions["rtt:vector"].samples

    rx_by_event: dict[tuple[str | None, str], list[Sample]] = defaultdict(list)
    for sample in rx_samples:
        rx_by_event[event_key(sample)].append(sample)

    received: dict[str, tuple[str, str]] = {}
    for rtt_sample in rtt_samples:
        candidates = rx_by_event.get(event_key(rtt_sample), [])
        if not candidates:
            raise ValueError(
                f"{vector_file.path}: RTT sample at t={rtt_sample.time} in {module} "
                "has no matching pingRxSeq sample"
            )
        sequence = candidates[0].value
        received.setdefault(sequence, (rtt_sample.time, rtt_sample.value))

    rx_times: dict[str, str] = {}
    for sample in rx_samples:
        rx_times.setdefault(sample.value, sample.time)

    destination = find_destination(vector_file, module)
    rows: list[dict[str, str]] = []
    for tx_sample in tx_samples:
        sequence = tx_sample.value
        if sequence in received:
            receive_time, rtt_seconds = received[sequence]
            status = "RECEIVED"
            rtt_ms = format_decimal(Decimal(rtt_seconds) * Decimal(1000))
        elif sequence in rx_times:
            receive_time = rx_times[sequence]
            rtt_seconds = ""
            rtt_ms = ""
            status = "RECEIVED_NO_RTT"
        else:
            receive_time = ""
            rtt_seconds = ""
            rtt_ms = ""
            status = "LOST"

        rows.append(
            {
                "run": vector_file.run,
                "config": vector_file.config,
                "network": vector_file.attributes.get("network", ""),
                "lambda_pps": find_iteration_variable(vector_file, "lambda"),
                "repetition": vector_file.attributes.get("repetition", ""),
                "source_file": vector_file.path.name,
                "module": module,
                "destination": destination,
                "sequence": sequence,
                "send_time_s": tx_sample.time,
                "receive_time_s": receive_time,
                "response_time_s": rtt_seconds,
                "response_time_ms": rtt_ms,
                "status": status,
            }
        )
    return rows


def main() -> int:
    args = parse_args()
    input_paths = expand_inputs(args.inputs)
    if not input_paths:
        print("error: no .vec input files found", file=sys.stderr)
        return 2

    selected_modules = set(args.module or [])
    rows: list[dict[str, str]] = []
    parsed_files = 0

    try:
        for input_path in input_paths:
            vector_file = parse_vector_file(input_path)
            ping_vectors = group_ping_vectors(vector_file)
            if selected_modules:
                ping_vectors = {
                    module: definitions
                    for module, definitions in ping_vectors.items()
                    if module in selected_modules
                }
            if not ping_vectors:
                continue
            parsed_files += 1
            for module, definitions in sorted(ping_vectors.items()):
                rows.extend(rows_for_module(vector_file, module, definitions))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if not rows:
        print(
            "error: no complete PingApp vector sets were found in the input files",
            file=sys.stderr,
        )
        return 2

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run",
        "config",
        "network",
        "lambda_pps",
        "repetition",
        "source_file",
        "module",
        "destination",
        "sequence",
        "send_time_s",
        "receive_time_s",
        "response_time_s",
        "response_time_ms",
        "status",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    received_count = sum(row["status"] == "RECEIVED" for row in rows)
    no_rtt_count = sum(row["status"] == "RECEIVED_NO_RTT" for row in rows)
    lost_count = sum(row["status"] == "LOST" for row in rows)
    print(
        f"Wrote {len(rows)} packet rows from {parsed_files} vector file(s) "
        f"to {output_path} "
        f"({received_count} received, {no_rtt_count} received without RTT, "
        f"{lost_count} lost)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

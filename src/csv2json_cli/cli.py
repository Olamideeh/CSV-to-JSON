
import argparse
import csv
import json
import sys
from pathlib import Path


def convert_csv(input_path: str) -> list[dict[str, str]]:
    """Read CSV records and return validated dictionaries."""
    path = Path(input_path)

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, strict=True)

        try:
            headers = next(reader)
        except StopIteration:
            raise ValueError("The CSV file is empty.") from None

        headers = [header.strip() for header in headers]

        if not headers or any(not header for header in headers):
            raise ValueError("CSV headers must not be empty.")

        if len(set(headers)) != len(headers):
            raise ValueError("CSV headers must be unique.")

        records = []

        for line_number, row in enumerate(reader, start=2):
            # Ignore completely blank lines.
            if not row or all(not value.strip() for value in row):
                continue

            if len(row) != len(headers):
                raise ValueError(
                    f"Line {line_number}: expected {len(headers)} "
                    f"columns but found {len(row)}."
                )

            records.append(dict(zip(headers, row)))

        return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv2json",
        description="Convert a CSV file into a JSON array."
    )
    parser.add_argument("input", help="Path to the input CSV file")
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file (prints to the terminal if omitted)"
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        records = convert_csv(args.input)
        output = json.dumps(records, indent=2, ensure_ascii=False) + "\n"

        if args.output:
            input_path = Path(args.input).resolve()
            output_path = Path(args.output).resolve()

            if input_path == output_path:
                parser.error("Input and output paths must be different.")

            output_path.write_text(output, encoding="utf-8")
            print(f"Converted {len(records)} records to {args.output}")
        else:
            sys.stdout.write(output)

        return 0

    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"csv2json: error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

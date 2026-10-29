
import json

import pytest

from csv2json_cli.cli import convert_csv, main


def test_converts_csv_to_records(tmp_path):
    source = tmp_path / "people.csv"
    source.write_text(
        "name,age\nAmina,22\nTunde,25\n",
        encoding="utf-8"
    )

    assert convert_csv(str(source)) == [
        {"name": "Amina", "age": "22"},
        {"name": "Tunde", "age": "25"},
    ]


def test_preserves_comma_inside_quoted_field(tmp_path):
    source = tmp_path / "people.csv"
    source.write_text(
        'name,city\n"Amina Yusuf","Lagos, Nigeria"\n',
        encoding="utf-8"
    )

    assert convert_csv(str(source)) == [
        {"name": "Amina Yusuf", "city": "Lagos, Nigeria"}
    ]


def test_rejects_empty_file(tmp_path):
    source = tmp_path / "empty.csv"
    source.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        convert_csv(str(source))


def test_rejects_duplicate_headers(tmp_path):
    source = tmp_path / "duplicate.csv"
    source.write_text("name,name\nAmina,Yusuf\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unique"):
        convert_csv(str(source))


def test_rejects_wrong_number_of_columns(tmp_path):
    source = tmp_path / "bad.csv"
    source.write_text("name,age\nAmina,22,extra\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected 2 columns"):
        convert_csv(str(source))


def test_missing_file_returns_helpful_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv", ["csv2json", str(tmp_path / "missing.csv")]
    )

    assert main() == 1
    assert "error:" in capsys.readouterr().err


def test_malformed_quoted_csv_is_rejected(tmp_path):
    source = tmp_path / "malformed.csv"
    source.write_text('name,city\nAmina,"Lagos\n', encoding="utf-8")

    with pytest.raises(Exception):
        convert_csv(str(source))


def test_help_option_shows_usage(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["csv2json", "--help"])

    with pytest.raises(SystemExit) as error:
        main()

    assert error.value.code == 0
    assert "usage:" in capsys.readouterr().out.lower()

import pytest

from conftest import load_script_module


@pytest.fixture
def fixer():
    return load_script_module("fix_metric_names.py", "fix_metric_names")


@pytest.fixture
def source_dir(tmp_path):
    pkg = tmp_path / "pkg" / "xds"
    pkg.mkdir(parents=True)
    (pkg / "consts.go").write_text(
        'package xds\n\nconst (\n\tsnapshotSubsystem = "xds_snapshot"\n\tgatewayLabel = "gateway"\n)\n'
    )
    (pkg / "metrics.go").write_text(
        "package xds\n\n"
        "var defers = metrics.NewCounter(\n"
        "\tmetrics.CounterOpts{\n"
        "\t\tSubsystem: snapshotSubsystem,\n"
        '\t\tName:      "defers_total",\n'
        '\t\tHelp:      "Deferred snapshots",\n'
        '\t}, []string{gatewayLabel, "reason"})\n\n'
        "var local = metrics.NewGauge(\n"
        "\tmetrics.GaugeOpts{\n"
        '\t\tName: "local_total",\n'
        '\t\tHelp: "Already correct",\n'
        '\t}, []string{"gateway"})\n'
    )
    return tmp_path


TABLE = (
    "Name|Type|Labels|Help\n"
    "--|--|--|--\n"
    "kgateway_defers_total|counter|gatewayLabel, reason|Deferred snapshots\n"
    "kgateway_local_total|gauge|gateway|Already correct\n"
)


def test_renames_metric_and_resolves_labels(fixer, source_dir):
    assert fixer.fix_metric_names(TABLE, str(source_dir)) == (
        "Name|Type|Labels|Help\n"
        "--|--|--|--\n"
        "kgateway_local_total|gauge|gateway|Already correct\n"
        "kgateway_xds_snapshot_defers_total|counter|gateway, reason|Deferred snapshots\n"
    )


def test_leaves_correct_table_unchanged(fixer, source_dir):
    table = "Name|Type|Labels|Help\n--|--|--|--\nkgateway_local_total|gauge|gateway|Already correct\n"
    (source_dir / "pkg" / "xds" / "metrics.go").write_text(
        'package xds\n\nvar local = metrics.NewGauge(metrics.GaugeOpts{Name: "local_total", Help: "Already correct"}, []string{"gateway"})\n'
    )
    assert fixer.fix_metric_names(table, str(source_dir)) == table


def test_warns_when_row_is_missing(fixer, source_dir, capsys):
    table = "Name|Type|Labels|Help\n--|--|--|--\n"
    assert fixer.fix_metric_names(table, str(source_dir)) == table
    assert "no row for kgateway_defers_total" in capsys.readouterr().err

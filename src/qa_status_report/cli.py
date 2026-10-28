"""Command-line entry point for generating the four-slide QA status report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from qa_status_report.data.fixed_workbook import WorkbookInputError, read_fixed_workbook
from qa_status_report.metrics.fixed_report import calculate_fixed_report_metrics
from qa_status_report.presentation.embed_chart_workbook import attach_editable_pie_data
from qa_status_report.reporting.payload import build_presentation_payload

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRESENTATION_SCRIPT = Path(__file__).with_name("presentation") / "generate_presentation.mjs"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower() or "projeto"


def _toolchain() -> tuple[str, str]:
    home = Path.home()
    runtime_root = home / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node"
    module = os.environ.get("QA_ARTIFACT_TOOL_MODULE") or str(
        runtime_root / "node_modules" / "@oai" / "artifact-tool" / "dist" / "artifact_tool.mjs"
    )
    node_env = os.environ.get("QA_NODE_EXECUTABLE")
    node_candidates = [Path(node_env)] if node_env else []
    node_candidates.extend((runtime_root / "bin" / "node.exe", runtime_root / "bin" / "node"))
    node = next((str(candidate) for candidate in node_candidates if candidate.is_file()), None)
    if node is None:
        node = shutil.which("node")
    if node is None:
        raise RuntimeError("Node.js não encontrado. Configure QA_NODE_EXECUTABLE com o caminho do executável Node.js.")
    if not Path(module).is_file():
        raise RuntimeError(
            "Gerador de PowerPoint do ambiente não encontrado. Configure QA_ARTIFACT_TOOL_MODULE com o caminho do módulo Artifact Tool."
        )
    return node, str(Path(module).resolve())


def _default_output(workbook, input_path: Path) -> Path:
    start = workbook.project.period_start.strftime("%Y%m%d")
    end = workbook.project.period_end.strftime("%Y%m%d")
    return PROJECT_ROOT / "outputs" / f"{_slug(workbook.project.name)}-status-report-{start}-{end}.pptx"


def generate_report(input_path: str | Path, output_path: str | Path | None = None) -> Path:
    source = Path(input_path).expanduser().resolve()
    original_hash = _sha256(source) if source.is_file() else None
    workbook = read_fixed_workbook(source)
    metrics = calculate_fixed_report_metrics(workbook)
    target = Path(output_path).expanduser() if output_path else _default_output(workbook, source)
    if not target.is_absolute():
        target = Path.cwd() / target
    target = target.resolve()
    if target.suffix.casefold() != ".pptx":
        raise ValueError("O caminho de saída deve terminar em .pptx.")
    if target == source:
        raise ValueError("O arquivo de saída não pode substituir o arquivo Excel de entrada.")
    if target.exists():
        raise FileExistsError(f"O arquivo de saída já existe; informe outro caminho para evitar sobrescrita: {target}")

    node, artifact_module = _toolchain()
    payload = build_presentation_payload(workbook, metrics)
    environment = os.environ.copy()
    environment["QA_ARTIFACT_TOOL_MODULE"] = artifact_module
    target.parent.mkdir(parents=True, exist_ok=True)
    configured_previews = os.environ.get("QA_REPORT_PREVIEW_DIR")
    preview_context = None
    if configured_previews:
        preview_dir = str(Path(configured_previews).expanduser().resolve())
        Path(preview_dir).mkdir(parents=True, exist_ok=True)
    else:
        preview_context = tempfile.TemporaryDirectory(prefix="qa-status-report-")
        preview_dir = preview_context.name
    try:
        result = subprocess.run(
            [node, str(PRESENTATION_SCRIPT), str(target), preview_dir],
            input=json.dumps(payload, ensure_ascii=False),
            text=True,
            encoding="utf-8",
            capture_output=True,
            env=environment,
            check=False,
        )
    finally:
        if preview_context is not None:
            preview_context.cleanup()
    if result.returncode != 0:
        target.unlink(missing_ok=True)
        output = result.stderr.strip() or result.stdout.strip()
        detail = output.splitlines()[0] if output else f"código {result.returncode}"
        raise RuntimeError(f"Falha ao montar o PowerPoint: {detail}")
    try:
        if workbook.scenarios:
            attach_editable_pie_data(target, metrics.status_distribution)
    except Exception as exc:
        target.unlink(missing_ok=True)
        raise RuntimeError(f"Não foi possível anexar os dados editáveis ao gráfico: {exc}") from exc
    if original_hash is not None and _sha256(source) != original_hash:
        target.unlink(missing_ok=True)
        raise RuntimeError("O hash do arquivo Excel mudou durante o processamento; o relatório foi descartado.")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qa-status-report", description="Gera um Status Report de QA a partir do workbook fixo do projeto.")
    parser.add_argument("workbook", help="Caminho para um arquivo .xlsx ou .xlsm preenchido conforme o template fixo.")
    parser.add_argument("--output", help="Caminho .pptx de saída. Padrão: outputs/<projeto>-status-report-<período>.pptx")
    args = parser.parse_args(argv)
    try:
        output = generate_report(args.workbook, args.output)
    except (FileNotFoundError, FileExistsError, WorkbookInputError, ValueError, RuntimeError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    print(f"Status Report gerado: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

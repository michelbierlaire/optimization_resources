from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RESOURCES_DIR = PROJECT_ROOT / "data" / "resources"
TEMPLATES_DIR = PROJECT_ROOT / "exercises" / "templates"
BUILD_DIR = PROJECT_ROOT / "build" / "exercises"
PUBLISHED_DIR = PROJECT_ROOT / "docs" / "assets" / "exercises"

QUESTION_TEMPLATE = TEMPLATES_DIR / "exercise_question.tex"
SOLUTION_TEMPLATE = TEMPLATES_DIR / "exercise_solution.tex"

CONTENT_PLACEHOLDER = "<<CONTENT>>"


class ExerciseBuildError(RuntimeError):
    """Raised when an exercise cannot be built."""


def is_defined(value: Any) -> bool:
    """Return True if a metadata field is meaningfully populated."""
    return value is not None and str(value).strip() != ""


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its content as a dictionary."""
    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)
    if not isinstance(data, dict):
        raise ExerciseBuildError(f"YAML file {path} does not contain a mapping.")
    return data


def load_exercise_resources(resource_ids: set[str] | None = None) -> list[dict[str, Any]]:
    """Load all exercise resources from data/resources."""
    resources: list[dict[str, Any]] = []

    yaml_paths = sorted(DATA_RESOURCES_DIR.glob("*.yml"))
    yaml_paths += sorted(DATA_RESOURCES_DIR.glob("*.yaml"))
    for path in yaml_paths:
        resource = load_yaml_file(path)
        if resource.get("type") != "exercise":
            continue

        if resource_ids is not None and resource.get("id") not in resource_ids:
            continue

        resource["_metadata_file"] = path
        resources.append(resource)

    return resources


def validate_exercise_resource(resource: dict[str, Any]) -> None:
    """Validate the fields required to build an exercise."""
    required_fields = ["id", "title", "question_source", "answer_source"]
    for field in required_fields:
        if not is_defined(resource.get(field)):
            raise ExerciseBuildError(
                f"Resource {resource.get('id', '<unknown>')} is missing required field '{field}'."
            )

    for field in ["question_source", "answer_source"]:
        source_path = PROJECT_ROOT / str(resource[field])
        if not source_path.exists():
            raise ExerciseBuildError(
                f"Resource '{resource['id']}' references missing file: {source_path}"
            )

    if not QUESTION_TEMPLATE.exists():
        raise ExerciseBuildError(f"Missing template: {QUESTION_TEMPLATE}")

    if not SOLUTION_TEMPLATE.exists():
        raise ExerciseBuildError(f"Missing template: {SOLUTION_TEMPLATE}")

    if CONTENT_PLACEHOLDER not in QUESTION_TEMPLATE.read_text(encoding="utf-8"):
        raise ExerciseBuildError(
            f"Template {QUESTION_TEMPLATE} does not contain placeholder {CONTENT_PLACEHOLDER!r}."
        )

    if CONTENT_PLACEHOLDER not in SOLUTION_TEMPLATE.read_text(encoding="utf-8"):
        raise ExerciseBuildError(
            f"Template {SOLUTION_TEMPLATE} does not contain placeholder {CONTENT_PLACEHOLDER!r}."
        )


def sanitize_fragment_path_for_latex(path: Path) -> str:
    """Return a LaTeX-friendly path."""
    return path.as_posix()


def topic_directory_name(resource: dict[str, Any]) -> str:
    """Choose the publication subdirectory from the first topic, or 'misc'."""
    topics = resource.get("topics") or []
    if topics:
        return str(topics[0])
    return "misc"


def published_pdf_paths(resource: dict[str, Any]) -> tuple[Path, Path]:
    """Return the output PDF paths for question and solution."""
    topic_dir = PUBLISHED_DIR / topic_directory_name(resource)
    question_pdf = topic_dir / f"{resource['id']}-question.pdf"
    solution_pdf = topic_dir / f"{resource['id']}-solution.pdf"
    return question_pdf, solution_pdf


def published_pdf_status(resource: dict[str, Any]) -> tuple[Path, bool, Path, bool]:
    """Return published PDF paths together with their existence status."""
    question_pdf, solution_pdf = published_pdf_paths(resource)
    return question_pdf, question_pdf.is_file(), solution_pdf, solution_pdf.is_file()


def render_template(
    template_path: Path,
    content_source: Path,
    output_tex_path: Path,
) -> None:
    """Render a standalone LaTeX file from a template and a content fragment."""
    template = template_path.read_text(encoding="utf-8")

    relative_content = Path(
        os.path.relpath(content_source, start=output_tex_path.parent)
    )
    rendered = template.replace(
        CONTENT_PLACEHOLDER,
        sanitize_fragment_path_for_latex(relative_content),
    )

    output_tex_path.parent.mkdir(parents=True, exist_ok=True)
    output_tex_path.write_text(rendered, encoding="utf-8")


def run_command(command: list[str], cwd: Path) -> None:
    """Run a subprocess and raise a helpful error if it fails."""
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ExerciseBuildError(
            f"Command failed in {cwd}:\n"
            f"{' '.join(command)}\n\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )


def compile_pdf(tex_path: Path) -> Path:
    """Compile a standalone LaTeX file to PDF using pdflatex."""
    if shutil.which("pdflatex") is None:
        raise ExerciseBuildError(
            "pdflatex was not found on PATH. Install a LaTeX distribution first."
        )

    cwd = tex_path.parent
    filename = tex_path.name

    # Two passes for stability.
    for _ in range(2):
        run_command(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                filename,
            ],
            cwd=cwd,
        )

    pdf_path = tex_path.with_suffix(".pdf")
    if not pdf_path.exists():
        raise ExerciseBuildError(f"Expected PDF was not generated: {pdf_path}")

    return pdf_path


def copy_pdf(source: Path, target: Path) -> None:
    """Copy a generated PDF into the published docs/assets tree."""
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def build_one_exercise(
    resource: dict[str, Any],
    build_question: bool = True,
    build_solution: bool = True,
) -> tuple[Path, Path]:
    """Build the missing question and/or solution PDFs for a single exercise."""
    validate_exercise_resource(resource)

    resource_build_dir = BUILD_DIR / resource["id"]
    resource_build_dir.mkdir(parents=True, exist_ok=True)

    question_source = PROJECT_ROOT / str(resource["question_source"])
    answer_source = PROJECT_ROOT / str(resource["answer_source"])

    question_pdf_published, solution_pdf_published = published_pdf_paths(resource)

    if build_question:
        question_tex = resource_build_dir / "question.tex"
        render_template(QUESTION_TEMPLATE, question_source, question_tex)
        question_pdf_built = compile_pdf(question_tex)
        copy_pdf(question_pdf_built, question_pdf_published)

    if build_solution:
        solution_tex = resource_build_dir / "solution.tex"
        render_template(SOLUTION_TEMPLATE, answer_source, solution_tex)
        solution_pdf_built = compile_pdf(solution_tex)
        copy_pdf(solution_pdf_built, solution_pdf_published)

    return question_pdf_published, solution_pdf_published


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build PDFs for exercise resources.")
    parser.add_argument(
        "--resource-id",
        action="append",
        dest="resource_ids",
        help="Build only the specified exercise resource ID. Can be repeated.",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = parse_args()
    selected_ids = set(args.resource_ids) if args.resource_ids else None

    resources = load_exercise_resources(selected_ids)
    if not resources:
        if selected_ids:
            requested = ", ".join(sorted(selected_ids))
            raise ExerciseBuildError(f"No exercise resources found for: {requested}")
        raise ExerciseBuildError("No exercise resources found in data/resources.")

    built_count = 0
    skipped_count = 0
    for resource in resources:
        question_pdf, has_question_pdf, solution_pdf, has_solution_pdf = published_pdf_status(resource)

        if has_question_pdf and has_solution_pdf:
            print(f"Skipped exercise '{resource['id']}' (already built)")
            print(f"  question: {question_pdf.relative_to(PROJECT_ROOT)}")
            print(f"  solution: {solution_pdf.relative_to(PROJECT_ROOT)}")
            skipped_count += 1
            continue

        question_pdf, solution_pdf = build_one_exercise(
            resource,
            build_question=not has_question_pdf,
            build_solution=not has_solution_pdf,
        )
        print(f"Built exercise '{resource['id']}'")
        print(
            f"  question: {question_pdf.relative_to(PROJECT_ROOT)}"
            f" ({'kept' if has_question_pdf else 'built'})"
        )
        print(
            f"  solution: {solution_pdf.relative_to(PROJECT_ROOT)}"
            f" ({'kept' if has_solution_pdf else 'built'})"
        )
        built_count += 1

    print(f"\nBuilt {built_count} exercise(s).")
    print(f"Skipped {skipped_count} exercise(s).")


if __name__ == "__main__":
    main()
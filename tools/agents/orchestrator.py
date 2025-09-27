import json
import os
import re
import subprocess
import sys
from pathlib import Path


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return re.sub(r"-+", "-", s)


def run(cmd, cwd=None):
    subprocess.check_call(cmd, cwd=cwd)


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def create_branch(branch: str):
    run(["git", "fetch", "origin", "main"])
    run(["git", "checkout", "-B", branch, "origin/main"])


def git_commit_push(branch: str, message: str, repo: str, token: str, actor: str):
    run(["git", "add", "-A"])
    run(
        [
            "git",
            "-c",
            f"user.name={actor}",
            "-c",
            f"user.email={actor}@users.noreply.github.com",
            "commit",
            "-m",
            message,
        ]
    )
    run(
        [
            "git",
            "remote",
            "set-url",
            "origin",
            f"https://x-access-token:{token}@github.com/{repo}.git",
        ]
    )
    run(["git", "push", "-u", "origin", branch])


def scaffold_skip_test(path: Path, reason: str):
    write(
        path,
        """
import pytest
pytest.skip(%r, allow_module_level=True)
""".lstrip()
        % reason,
    )


def scaffold_for_issue(title: str, labels: list[str]):
    lowered = title.lower()

    if any(l.startswith("area:cad_core") for l in labels):
        # cad_core primitives + transforms
        write(Path("cad_core/geom/__init__.py"), "\n")
        write(Path("cad_core/geom/primitives.py"), '"""Geometry primitives scaffold (agent)."""\n')
        write(Path("cad_core/geom/transform.py"), '"""Transform functions scaffold (agent)."""\n')
        scaffold_skip_test(
            Path("tests/cad_core/test_primitives.py"), "scaffold: cad_core primitives"
        )
        return {
            "branch": f"feat/agent-{slugify(title)}",
            "message": "chore(agent): scaffold cad_core primitives + transforms",
        }

    if any(l.startswith("area:backend") for l in labels):
        if "settings" in lowered:
            write(Path("backend/settings/__init__.py"), "\n")
            write(Path("backend/settings/service.py"), '"""Settings service scaffold (agent)."""\n')
            scaffold_skip_test(
                Path("tests/backend/test_settings_service.py"), "scaffold: backend settings service"
            )
            return {
                "branch": f"feat/agent-{slugify(title)}",
                "message": "chore(agent): scaffold backend settings service",
            }
        # default to catalog store
        write(Path("backend/store/__init__.py"), "\n")
        write(Path("backend/store/catalog.py"), '"""Catalog store scaffold (agent)."""\n')
        scaffold_skip_test(
            Path("tests/backend/test_catalog_store.py"), "scaffold: backend catalog store"
        )
        return {
            "branch": f"feat/agent-{slugify(title)}",
            "message": "chore(agent): scaffold backend catalog store",
        }

    if any(l.startswith("area:frontend") for l in labels):
        if "input" in lowered:
            write(Path("frontend/input/__init__.py"), "\n")
            write(Path("frontend/input/handler.py"), '"""Input handler scaffold (agent)."""\n')
            scaffold_skip_test(
                Path("tests/frontend/test_input_handler.py"), "scaffold: frontend input handler"
            )
            return {
                "branch": f"feat/agent-{slugify(title)}",
                "message": "chore(agent): scaffold frontend input handler",
            }
        # default to model space shell
        write(Path("frontend/widgets/__init__.py"), "\n")
        write(
            Path("frontend/widgets/model_space.py"), '"""Model Space widget scaffold (agent)."""\n'
        )
        write(Path("frontend/widgets/command_bar.py"), '"""Command bar scaffold (agent)."""\n')
        scaffold_skip_test(
            Path("tests/frontend/test_model_space.py"), "scaffold: frontend model space shell"
        )
        return {
            "branch": f"feat/agent-{slugify(title)}",
            "message": "chore(agent): scaffold frontend model space shell",
        }

    # Unknown area: no-op
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: orchestrator.py <event_json_path>")
        return 1
    event_path = sys.argv[1]
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    issue = event.get("issue", {})
    title = issue.get("title", "")
    labels = [l["name"] for l in issue.get("labels", [])]

    plan = scaffold_for_issue(title, labels)
    if not plan:
        print("No scaffold rule matched; exiting.")
        return 0

    branch = plan["branch"]
    message = plan["message"]

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    actor = os.environ.get("GITHUB_ACTOR", "agent-bot")
    if not token or not repo:
        print("Missing GITHUB_TOKEN or GITHUB_REPOSITORY")
        return 2

    create_branch(branch)
    git_commit_push(branch, message, repo, token, actor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

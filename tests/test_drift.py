"""Projects learn when a newer standards release exists (STD-2)."""

from pathlib import Path

from conftest import Repo, make_repo
from project_standards.drift import check, repo_url


def test_repo_url_expands_github_shorthand() -> None:
    assert repo_url("gh:wghami/x") == "https://github.com/wghami/x.git"
    assert repo_url("/local/path") == "/local/path"


def _template(tmp_path: Path, *tags: str) -> Repo:
    template = make_repo(tmp_path / "template")
    template.commit("feat(core): x")
    for tag in tags:
        template.git.run("tag", tag)
    return template


def _answers(tmp_path: Path, commit: str, src: Path) -> Path:
    answers = tmp_path / ".copier-answers.yml"
    answers.write_text(f"_commit: {commit}\n_src_path: {src}\n")
    return answers


def test_up_to_date_project_passes(tmp_path: Path, repo: Repo) -> None:
    template = _template(tmp_path, "v0.1.0", "latest")
    assert check(_answers(tmp_path, "v0.1.0", template.path), repo.git) == []


def test_outdated_project_is_told_to_update(tmp_path: Path, repo: Repo) -> None:
    template = _template(tmp_path, "v0.1.0", "v0.10.0", "v0.2.0")
    errors = check(_answers(tmp_path, "v0.2.0-3-gabc", template.path), repo.git)
    assert errors == [
        (
            "standards template v0.10.0 is available (this project uses v0.2.0-3-gabc); "
            "run `copier update`"
        )
    ]


def test_untagged_render_is_reported(tmp_path: Path, repo: Repo) -> None:
    template = _template(tmp_path)
    assert "not a release tag" in check(_answers(tmp_path, "abc123", template.path), repo.git)[0]

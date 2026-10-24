"""Version comes from tags; tags are published; nothing releasable is left untagged."""

from pathlib import Path

from conftest import Repo
from project_standards.config import Config
from project_standards.versioning import (
    check_published,
    check_pyproject,
    check_released,
    latest_tag,
)


def test_dynamic_version_passes(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\ndynamic = ["version"]\n')
    assert check_pyproject(tmp_path) == []


def test_static_version_is_refused(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "1.0.0"\n')
    errors = check_pyproject(tmp_path)
    assert len(errors) == 2


def test_latest_tag_ignores_non_release_tags(repo: Repo) -> None:
    repo.commit("feat(core): x")
    assert latest_tag(repo.git) is None
    repo.git.run("tag", "v1-beta")
    assert latest_tag(repo.git) is None
    repo.git.run("tag", "v0.1.0")
    assert latest_tag(repo.git) == "v0.1.0"


def test_nothing_to_publish_before_the_first_release(repo: Repo) -> None:
    repo.commit("feat(core): x")
    assert check_published(repo.git, "origin") == []


def test_unreachable_tags_are_reported(repo: Repo) -> None:
    repo.commit("feat(core): x")
    repo.git.run("checkout", "-q", "-b", "feat/other")
    repo.commit("feat(core): y")
    repo.git.run("tag", "v0.1.0")
    repo.git.run("checkout", "-q", "main")
    assert "none is reachable" in check_published(repo.git, "origin")[0]


def test_unpushed_tag_is_reported(repo: Repo) -> None:
    repo.add_remote()
    repo.commit("feat(core): x")
    repo.git.run("push", "-q", "origin", "main")
    repo.git.run("tag", "v0.1.0")
    assert "is not on 'origin'" in check_published(repo.git, "origin")[0]


def test_pushed_lightweight_and_annotated_tags_pass(repo: Repo) -> None:
    repo.add_remote()
    repo.commit("feat(core): x")
    repo.git.run("tag", "v0.1.0")
    repo.commit("fix(core): y")
    repo.git.run("tag", "-a", "v0.1.1", "-m", "release")
    repo.git.run("push", "-q", "origin", "main", "--tags")
    assert check_published(repo.git, "origin") == []


def test_moved_tag_is_reported(repo: Repo) -> None:
    repo.add_remote()
    repo.commit("feat(core): x")
    repo.git.run("tag", "v0.1.0")
    repo.git.run("push", "-q", "origin", "main", "--tags")
    repo.commit("fix(core): y")
    repo.git.run("tag", "-f", "v0.1.0")
    assert "points to" in check_published(repo.git, "origin")[0]


def test_untagged_releasable_commits_are_reported(repo: Repo) -> None:
    repo.commit("feat(core): x")
    assert "not tagged" in check_released(repo.git, Config())[0]
    repo.git.run("tag", "v0.1.0")
    repo.commit("docs: explain")
    assert check_released(repo.git, Config()) == []
    repo.commit("fix(core): y\n\nbody")
    assert "not tagged" in check_released(repo.git, Config())[0]

"""Every finding has an exact, actionable message (the messages are the user interface).

Fragment assertions let a mangled message pass; these tests pin each message completely, so
mutation testing (TST-12) can tell a correct message from a broken one.
"""

import json
from pathlib import Path

import pytest

from conftest import Repo, make_repo
from project_standards import (
    branches,
    commits,
    doc_impact,
    drift,
    hooks,
    mutation,
    parity,
    standards_docs,
    suppressions,
    versioning,
)
from project_standards.config import Config, DocRule

CONFIG = Config(types=("feat", "fix", "docs"), scopes=("core", "docs"))


# --- commits ----------------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("message", "errors"),
    [
        ("", ["the commit message is empty"]),
        ("fixup! feat(core): x", ["fixup!/squash! commits must be squashed before merge"]),
        ("Add things", ["'Add things' is not '<type>(<scope>): <summary>' (Conventional Commits)"]),
        ("feet(core): x", ["type 'feet' is not one of: feat, fix, docs"]),
        ("feat: x", ["type 'feat' requires a scope: core, docs"]),
        ("docs(web): x", ["scope 'web' is not one of: core, docs"]),
        ("docs: x.", ["the summary must not end with a period"]),
        (
            "docs: Add x",
            ["the summary starts with a lower-case imperative verb ('add', not 'Add')"],
        ),
        ("docs: x\nbody", ["separate the header from the body with one blank line"]),
        ("feat(core)!: x", ["'!' needs a 'BREAKING CHANGE: <what breaks>' footer (COM-2)"]),
        ("docs: " + "x" * 67, ["the header is 73 characters; the limit is 72"]),
        ("docs: " + "x" * 66, []),
    ],
)
def test_commit_messages(message: str, errors: list[str]) -> None:
    assert commits.check_message(message, CONFIG) == errors


def test_breaking_and_releasing_read_the_first_line() -> None:
    assert commits.is_breaking("feat(core)!: x\n\nbody")
    assert commits.is_releasing("feat(core): x\n\nmore body", CONFIG)
    assert not commits.is_releasing("docs: x\n\nfeat(core): not a header", CONFIG)


# --- branches ---------------------------------------------------------------------------------
def test_branch_message() -> None:
    assert branches.check_branch("wip", CONFIG) == [
        (
            "branch 'wip' must be '<type>/<topic>' with type in feat, fix, docs and a lower-case "
            "topic (e.g. feat/rule-compiler)"
        )
    ]


@pytest.mark.parametrize("name", ["feat/a/b", "feat/x!", "featx/y", "xfeat/y"])
def test_branch_names_need_exactly_one_known_type_and_a_simple_topic(name: str) -> None:
    assert branches.check_branch(name, CONFIG) != []


# --- suppressions -----------------------------------------------------------------------------
def test_suppression_message_names_the_file(tmp_path: Path) -> None:
    path = tmp_path / "m.py"
    path.write_text("x = 1  " + "#" + " noqa\n", encoding="utf-8")
    assert suppressions.check_files([path]) == [f"{path}:1: noqa must name its rule codes (LNT-4)"]


# --- versioning -------------------------------------------------------------------------------
def test_pyproject_messages(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text('[project]\nversion = "1"\n')
    assert versioning.check_pyproject(tmp_path) == [
        "pyproject.toml sets [project].version; it must come from git tags (VER-1)",
        'pyproject.toml must declare dynamic = ["version"] (VER-1)',
    ]


def test_pyproject_without_a_project_table(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[tool.x]\n")
    assert versioning.check_pyproject(tmp_path) == [
        'pyproject.toml must declare dynamic = ["version"] (VER-1)'
    ]


def test_a_non_release_tag_does_not_end_the_bootstrap(repo: Repo) -> None:
    repo.commit("feat(core): x")
    repo.git.run("checkout", "-q", "-b", "feat/other")
    repo.commit("feat(core): y")
    repo.git.run("tag", "latest")
    repo.git.run("checkout", "-q", "main")
    assert versioning.check_published(repo.git, "origin") == []


def test_unreachable_tag_message(repo: Repo) -> None:
    repo.commit("feat(core): x")
    repo.git.run("checkout", "-q", "-b", "feat/other")
    repo.commit("feat(core): y")
    repo.git.run("tag", "v0.1.0")
    repo.git.run("checkout", "-q", "main")
    assert versioning.check_published(repo.git, "origin") == [
        "tags exist but none is reachable from HEAD; rebase on the default branch"
    ]


def test_moved_tag_message(repo: Repo) -> None:
    remote = repo.add_remote()
    first = repo.commit("feat(core): x")
    repo.git.run("tag", "v0.1.0")
    repo.git.run("push", "-q", "origin", "main", "--tags")
    second = repo.commit("fix(core): y")
    repo.git.run("tag", "-f", "v0.1.0")
    assert versioning.check_published(repo.git, str(remote)) == [
        f"tag v0.1.0 points to {first[:10]} on '{remote}' but {second[:10]} locally"
    ]


def test_released_message_lists_every_pending_commit(repo: Repo) -> None:
    first = repo.commit("feat(core): x")
    second = repo.commit("fix(core): y\n\nbody")
    assert versioning.check_released(repo.git, CONFIG) == [
        (
            f"releasable commits are not tagged ({second[:10]}, {first[:10]}); the release job "
            "must run `cz bump` and push the tag (VER-2)"
        )
    ]


# --- doc impact -------------------------------------------------------------------------------
IMPACT = Config(
    watched=("src/**", "pyproject.toml"),
    doc_rules=(DocRule(paths=("src/**",), docs=("docs/a.md", "docs/b.md")),),
)


def test_doc_impact_messages_and_order() -> None:
    change = doc_impact.Change(
        files=("README.md", "pyproject.toml", "src/x.py", "src/y.py"), messages=("docs: x",)
    )
    assert doc_impact.check(change, IMPACT) == [
        (
            "pyproject.toml: watched but not mapped in [[doc_impact.rules]] of standards.toml; map "
            "it to the docs that describe it"
        ),
        (
            "src/x.py changed, but none of docs/a.md, docs/b.md did. Update them, or add a "
            "'Docs-Reviewed: <why>' commit footer"
        ),
        (
            "src/y.py changed, but none of docs/a.md, docs/b.md did. Update them, or add a "
            "'Docs-Reviewed: <why>' commit footer"
        ),
    ]


def test_doc_impact_compares_commits_not_the_working_tree(repo: Repo) -> None:
    base = repo.commit("chore: start", {"a.txt": "a"})
    repo.commit("docs: change", {"b.txt": "b"})
    repo.write("c.txt", "uncommitted")
    change = doc_impact.collect(repo.git, base)
    assert change is not None
    assert change.files == ("b.txt",)


def test_doc_impact_reads_every_message(repo: Repo) -> None:
    base = repo.commit("chore: start")
    repo.commit("docs: one")
    repo.commit("docs: two")
    change = doc_impact.collect(repo.git, base)
    assert change is not None
    assert change.messages == ("docs: two", "docs: one")


# --- parity -----------------------------------------------------------------------------------
def test_parity_messages(tmp_path: Path) -> None:
    config = tmp_path / "hooks.yaml"
    config.write_text(
        "repos:\n  - repo: local\n    hooks:\n"
        "      - {id: b, stages: [pre-push]}\n      - {id: a, stages: [pre-push]}\n"
        "      - {id: m, stages: [commit-msg]}\n"
    )
    workflow = tmp_path / "ci.yml"
    workflow.write_text("jobs: {}\n")
    assert parity.check(config, workflow) == [
        f"{workflow}: commit-msg hooks run locally but CI never runs `standards check-commits`",
        (
            f"{workflow}: no `pre-commit run --all-files --hook-stage pre-push` step, "
            "so a, b would only run locally"
        ),
    ]


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ("[1]", "pre-commit config must be a mapping"),
        ("default_stages: pre-push", "default_stages must be a list"),
        ("repos: {}", "repos must be a list"),
        ("repos: [1]", "repo must be a mapping"),
        ("repos: [{hooks: 1}]", "hooks must be a list"),
        ("repos: [{hooks: [1]}]", "hook must be a mapping"),
        ("repos: [{hooks: [{id: 1}]}]", "hook id must be a string"),
        ("repos: [{hooks: [{id: a, stages: x}]}]", "stages of a must be a list"),
    ],
)
def test_malformed_hook_configs_are_refused(config: str, message: str) -> None:
    with pytest.raises(TypeError) as error:
        parity.hook_stages(config)
    assert str(error.value) == message


def test_repos_without_hooks_and_default_stages() -> None:
    text = "default_stages: [pre-push]\nrepos:\n  - repo: x\n  - repo: y\n    hooks: [{id: a}]\n"
    assert parity.hook_stages(text) == {"pre-push": {"a"}}


# --- standards documents ----------------------------------------------------------------------
def test_standards_document_messages(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    first = docs / "a.md"
    first.write_text("intro\n| X-1 | rule | enforcer |   \n| X-2 | rule |  |\n")
    second = docs / "b.md"
    second.write_text("| X-1 | again | `standards check-a` |\n")
    hooks_file = tmp_path / "hooks.yaml"
    hooks_file.write_text(
        "repos:\n  - hooks:\n      - {id: one}\n      - {id: two, stages: [pre-push]}\n"
    )
    assert standards_docs.check(docs, hooks_file, ["check-a"]) == [
        f"{first}:3: rule X-2 has an empty cell (every rule names its enforcer)",
        f"{second}:1: rule X-1 is already defined at {first}:2",
        f"hook `one` ({hooks_file}) is not documented in {docs}",
        f"hook `two` ({hooks_file}) is not documented in {docs}",
    ]


# --- mutation ---------------------------------------------------------------------------------
def test_mutation_message_defaults_missing_counts_to_zero(tmp_path: Path) -> None:
    stats = tmp_path / "s.json"
    stats.write_text(json.dumps({"killed": 1, "no_tests": 1, "note": "ignored"}))
    assert mutation.check(stats, 90) == [
        "mutation score 50.0 % is below 90 % (0 survived, 1 untested)"
    ]
    stats.write_text(json.dumps({"killed": 1, "survived": 1}))
    assert mutation.check(stats, 90) == [
        "mutation score 50.0 % is below 90 % (1 survived, 0 untested)"
    ]


# --- drift ------------------------------------------------------------------------------------
def test_drift_messages(tmp_path: Path, repo: Repo) -> None:
    answers = tmp_path / "answers.yml"
    answers.write_text("_src_path: x\n")
    assert drift.check(answers, repo.git) == [
        f"{answers}: _commit '' is not a release tag; update from a tagged template release"
    ]


def test_drift_ignores_tags_in_other_namespaces(tmp_path: Path, repo: Repo) -> None:
    template = make_repo(tmp_path / "template")
    template.commit("feat(core): x")
    template.git.run("tag", "v0.1.0")
    template.git.run("tag", "release/v9.0.0")
    answers = tmp_path / "answers.yml"
    answers.write_text(f"_commit: v0.1.0\n_src_path: {template.path}\n")
    assert drift.check(answers, repo.git) == []


def test_drift_without_any_release_is_up_to_date(tmp_path: Path, repo: Repo) -> None:
    template = make_repo(tmp_path / "template")
    template.commit("feat(core): x")
    answers = tmp_path / "answers.yml"
    answers.write_text(f"_commit: v0.1.0\n_src_path: {template.path}\n")
    assert drift.check(answers, repo.git) == []


# --- hooks ------------------------------------------------------------------------------------
def test_binary_hooks_are_read_without_crashing(repo: Repo) -> None:
    hooks_dir = repo.path / ".git" / "hooks"
    for stage in hooks.STAGES:
        (hooks_dir / stage).write_bytes(b"\xff\xfe pre-commit")
    assert hooks.check(repo.git) == []


def test_mutants_that_were_never_evaluated_fail_the_gate(tmp_path: Path) -> None:
    stats = tmp_path / "s.json"
    stats.write_text(json.dumps({"killed": 0, "survived": 0, "total": 1474}))
    assert mutation.check(stats, 90) == [
        (
            "mutmut evaluated none of the 1474 mutants: the baseline test run failed "
            "(see the `mutmut run` output)"
        )
    ]
    stats.write_text(json.dumps({"killed": 0, "survived": 0, "total": 0}))
    assert mutation.check(stats, 90) == []


def test_header_only_skips_the_footer_rule_only() -> None:
    assert commits.check_message("feat(core)!: x", CONFIG, header_only=True) == []
    assert commits.check_message("feat(core)!: X.", CONFIG, header_only=True) == [
        "the summary must not end with a period",
        "the summary starts with a lower-case imperative verb ('add', not 'Add')",
    ]

# 09 — Mutation testing

Rule: TST-12.

100 % coverage proves that every line ran, not that a test would notice a bug in it. Mutation
testing ([mutmut](https://github.com/boxed/mutmut)) makes small deliberate changes ("mutants")
to the code, and checks that some test fails for each.

- **When:** nightly, and on PRs labelled `mutation` (`nightly.yml`).
- **Gate:** `standards check-mutation-score mutants/mutmut-cicd-stats.json --min N`, with N chosen
  at render time (default 90). Killed and timed-out mutants count as caught; survivors, untested
  and suspicious mutants count against the score. No mutants at all is not a failure, but mutants
  that were **never evaluated** are: it means the baseline test run failed under mutmut (often a
  file the tests read that `also_copy` does not list), and the badge then shows "not measured".
  A project with no function yet (only module-level code) has nothing to mutate: mutmut stops
  early, and the workflow records zero mutants instead of failing.
- **On failure:** a scheduled failure opens a `release-blocker` issue, and releases stop until it
  is closed (CI-7).
- **Badge:** the measured score is published every night, pass or fail ([08](08-badges-and-gates.md)).

## What usually survives, and what to do

| Survivor | Fix |
|---|---|
| A changed error message | assert the **whole** message, not a fragment |
| A changed CLI help text, default or `required=` | snapshot the `--help` output; test missing arguments |
| A changed boundary (`>` → `>=`) | test the exact boundary value |
| An equivalent mutant (e.g. `"\x1e"` → `"\x1E"`, the same character) | accept it: no test can tell them apart, which is why the threshold is below 100 % |

The CLI of this repository is held to the same gate.

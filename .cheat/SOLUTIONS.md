# Maintainer notes: exercise sequence

These notes give teachers and TAs an overview of the student's progression, the planted faults and their fixes.
Detailed student instructions, including how to inspect logs, belong in the practical and lecture.

## 1. Lint findings

### What a student should observe

On the first CI run, lint fails before the tests run:

- `src/ci_course/cli.py`: unused `import sys` (F401).
- `src/ci_course/io.py`: mutable default `errors=[]` (B006).
- `src/ci_course/io.py`: bare `except` (E722).

The shared default list accumulates errors across calls, but the sample data contains no unparseable rows, so the tests miss this bug.

### What a student needs to do to fix it

Remove the unused import and catch parsing errors with `except ValueError:`.
Give each call its own default error list:

```python
def load_measurements(path=None, errors=None):
    if errors is None:
        errors = []
```

## 2. Sample data missing from the installed package

### What a student should observe

Once lint passes, five tests fail with `FileNotFoundError` for the sample CSV inside `site-packages`.
The editable local install passes because it exposes the source data; CI's non-editable install omits it.
The `src` layout ensures the tests exercise the installed package.

### What a student needs to do to fix it

Include the CSV in the package by adding this to `pyproject.toml`:

```toml
[tool.setuptools.package-data]
ci_course = ["data/*.csv"]
```

## 3. Reports cannot be overwritten on Windows

### What a student should observe

When the OS matrix is introduced, `test_replaces_an_existing_report` fails with `FileExistsError` on Windows but passes on Ubuntu and macOS.
Native Windows users may already have seen this locally.
`os.rename` replaces an existing destination on POSIX but fails on Windows.

### What a student needs to do to fix it

In `write_report` in `src/ci_course/report.py`, replace `os.rename(tmp, path)` with:

```python
os.replace(tmp, path)
```

Keep this fault tied to the OS so changes to the Python matrix cannot make it disappear.

## 4. Missing values reported as a mean of zero

### What a student should observe

Coverage reveals an untested branch in `summarise` in `src/ci_course/stats.py`.
A test for entirely missing values exposes summary statistics of zero, incorrectly implying measured values exist.

### What a student needs to do to fix it

Add a test for the missing-values case and make the empty-data branch return `nan` for the statistics or raise an appropriate exception.
Keep `n` as zero if returning a summary.

## 5. A public function with no docstring

### What a student should observe

During the documentation section, `ruff check --select D src/` reports D103 for `count_missing` in `src/ci_course/stats.py`.
The function is exported and tested but absent from Sphinx's generated API reference.

### What a student needs to do to fix it

Add a docstring in the package's numpydoc style and rebuild the documentation to see the function appear.
Like code coverage, this check establishes completeness without judging quality.

## 6. Publishing the documentation

### What a student should observe

The documentation only exists on their own machine.
Building it proves it compiles, but nobody else can read it.

### What a student needs to do to fix it

Enable Pages in the repository settings, with the source set to GitHub Actions rather than a branch.
Pages on a free account needs a public repository.

Write a single job workflow that checks out the code, installs `.[docs]`, runs `sphinx-build`, then uses `configure-pages`, `upload-pages-artifact` and `deploy-pages`.
It needs `pages: write` and `id-token: write`, which is a short lived token for the deployment rather than a secret anyone has to store.

Read the Docs is the more common choice in scientific Python and is worth a mention, but the build happens somewhere the student cannot watch, which is the wrong lesson in a course about seeing your pipeline run.

At this stage the workflow is a single ungated job.
Section 10 splits it apart.

## 7. Documentation previews

### What a student should observe

A successful documentation build does not establish that the rendered text, formatting and links are correct.
Published Pages documentation reflects `main`, so it does not show proposed PR changes.

### What a student needs to do to fix it

Use `docs_preview.yml` to upload the PR's rendered Sphinx HTML as `documentation-preview` for review before merging.
The Pages workflow publishes after merging.
The later gated deployment exercise reuses built HTML in a separate job after approval.

## 8. Caching and concurrency

### What a student should observe

Repeated runs download the same dependencies, and successive commits can leave obsolete CI runs active.
Timing differences will be small here; the practical and lecture should explain that larger downloads or expensive builds can make savings significant.

### What a student needs to do to fix it

Enable pip caching in the `setup-python` step:

```yaml
cache: pip
cache-dependency-path: pyproject.toml
```

Cancel superseded runs with workflow-level concurrency:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

The Python versions, Operating systems, Coverage and Docstrings workflows provide the reference examples.

## 9. Pre-commit

### What a student should observe

Every check so far has only spoken up after a push, so a trivial lint error costs a full round trip through CI.
Hooks move that feedback to commit time, where it costs seconds.

By this point in the course the three planted lint findings have already been fixed, back in the first exercise.
A clean tree catches nothing, so the student has to reintroduce a fault to see the hooks work.
Adding an unused import is enough.

### What a student needs to do to fix it

Create `.pre-commit-config.yaml`, then install the hooks into the local clone:

```bash
pre-commit install
```

Reintroduce a lint fault, try to commit it, and watch the commit be refused.
Fix it and commit again.

Run every hook against the whole repository, which is what CI does:

```bash
pre-commit run --all-files
```

The reference configuration pins four whitespace hooks and `ruff-check`.
`ruff-check` deliberately does not pass `--fix`, so it reports the same findings as the lint job rather than rewriting the code underneath the student.

The reference workflow is `pre_commit.yml`.

Be straight with students that this workflow is close to redundant here, because the Python versions and Operating systems workflows already run `ruff check`.
It earns its place as a backstop rather than as new coverage: hooks are installed per clone, so anyone who skips `pre-commit install` is unprotected, `git commit --no-verify` bypasses them, and a commit hook only sees the files in that commit while `--all-files` catches drift after a config or hook version change.
The wider point is the same one branch protection makes: a local convention is not enforcement until something outside the developer's machine checks it.
The extra practice at reading and writing workflow YAML is itself worth the ten seconds of duplicated linting.

## 10. Gated deployment

### What a student should observe

The Pages workflow from section 6 publishes whatever lands on `main`.
It runs no tests, and it builds and publishes in one job, so the thing that goes live was never a reviewable artifact.
Nobody is asked whether publishing is a good idea.

This is the distinction the lecture draws between Continuous Delivery and Deployment, made concrete.
Up to now the course has only shown Deployment.

### What a student needs to do to fix it

Split the workflow into three jobs joined by `needs:`: `tests`, then `build-docs`, then `deploy`.
Deployment now requires both passing tests and a documentation build that survives `-W`.

Build the HTML once in `build-docs` and upload it with `upload-pages-artifact`.
The `deploy` job has no checkout, no install and no build: it runs `deploy-pages` and nothing else, so what is published is exactly the artifact that was built and reviewed.
Rebuilding in the deploy job would quietly reintroduce the possibility of publishing something different from what passed.

Add a required reviewer to the `github-pages` environment, under Settings, then Environments.
This is the part students most often miss: the gate is a repository setting, not a line of YAML.
The workflow only names the environment, and naming it is what makes the setting apply.
With a reviewer configured the deploy job sits waiting for approval, and the run shows who approved it.

Keep `permissions: contents: read` at workflow level and widen only inside `deploy`, so nothing before the gate holds a token that can publish.

The concurrency group is worth contrasting with section 8.
The test workflows cancel superseded runs, because an obsolete test result is worthless.
A deployment is cancelled part way through at your peril, so this one queues instead, with `cancel-in-progress: false`.

A tag triggered GitHub Release with generated notes is a reasonable optional extra here.
It is not in the reference files.

## 11. Supply chain

### What a student should observe

Every workflow they have written pulls in somebody else's code with `uses:`, identified by a tag.
A tag belongs to the action's author and can be moved to different code at any time, so `@v7` is a promise rather than a fact.
The Codecov step is the sharp end: it is third-party, and it is the one step that is handed a secret.

Nothing in the course so far has checked any of this, and none of it is visible by reading a green tick.

### What a student needs to do to fix it

Run the auditor and read what it says:

```bash
pipx run zizmor .github/workflows/
```

On unconfigured workflows it finds three things, and all three are worth fixing:

- `unpinned-uses`: pin third-party actions to a commit hash, with the tag kept in a trailing comment so it is still readable.
- `excessive-permissions`: add `permissions: contents: read` to each workflow and widen only where a job needs it, as the deployment workflow does.
- `artipacked`: add `persist-credentials: false` to `actions/checkout`, which otherwise leaves a usable token in `.git/config` for every later step.

The pin policy lives in `zizmor.yml`: GitHub's own actions may be used by tag, everything else must be hashed.
That is a deliberate position rather than the strictest one, and it is worth asking students whether they agree with it.
Applied here it flags exactly one action, `codecov/codecov-action`, which is the right answer.

Add Dependabot for GitHub Actions with a cooldown.
The cooldown is the interesting part: taking an update the day it ships is its own risk, and a fortnight's delay means somebody else finds the bad release first.

All seven reference workflows have these fixes applied, so `zizmor` reports nothing against `.cheat/`.
A student's own workflows will not, which is the exercise.

### Notes for maintainers

Dependabot watches GitHub Actions only.
The Python dependencies are declared without version bounds and there is no lockfile, so Dependabot has nothing to raise for pip.
If bounds or a lockfile are ever added, revisit that.

The reference `dependabot.yml` says `directory: "/"`, which is correct for a student whose workflows are at `.github/workflows`.
It is not correct for this repository, where the reference workflows live under `.cheat/`.
Enabling Dependabot on these files would need `directory: "/.cheat/.github/workflows"`, because the Actions file fetcher scans YAML directly in the configured directory rather than walking down from it.

The audit workflow uses `zizmorcore/zizmor-action`, pinned to a commit like any other third-party action.
An earlier draft installed `zizmor` from pip in a `run:` step instead, which was a mistake worth not repeating: hash-pinning the actions on one line and then fetching an unpinned package from an index on the next is the hole this whole section is about.
Using an action also means Dependabot maintains it, which the pip step would not have been, because Dependabot here watches GitHub Actions only.

Both pins matter.
The action is pinned by commit, and its `version` input pins the auditor the action installs.
Without `version` the action takes the latest zizmor release, so the workflow would still be running unreviewed code.

The pinned versions are deliberately not the newest.
zizmor 1.31.0 and zizmor-action v0.7.0 were both released on 2026-10-15; the pins here are the previous pair, v0.6.4 and 1.30.1, which is what the fortnight cooldown recommended two paragraphs earlier actually looks like when you follow it.
`training-slides-core` pins the same action commit.

`advanced-security: false` with `annotations: true` makes the action annotate the diff and fail, which needs only `contents: read`.
Set `advanced-security: true` instead to upload results to code scanning, which needs `security-events: write` and `actions: read`.

## Maintaining the reference files

The workflows and documentation in `.cheat/` are maintained by hand, with no automated check against the practical.
When commands, job names, dependencies or faults change, update the matching practical examples and notes here.
Keep solutions out of the student README.

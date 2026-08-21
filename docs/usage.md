# Using it in a repository

Three small files opt a repository in.

## 1. `docs/conf.py`

```python
project = 'BlueRobotics Models'
copyright = 'Honu Robotics'
author = 'Honu Robotics'

extensions = ['sphinx_honu']
honu_github = ('HonuRobotics', 'bluerobotics_models')
```

The extension applies the theme, its docs.ros.org configuration, the brand
skin, the version flyout and the GitHub edit link, and enables MyST so all
pages are Markdown. Anything set explicitly in `conf.py` wins over the
extension defaults.

## 2. `docs/requirements.txt`

```text
sphinx-honu @ git+https://github.com/HonuRobotics/honu-docs@v0.2.0
```

Pin a release tag. Rebuilding an old distribution branch keeps the exact
look it shipped with; bumping the pin per branch is a deliberate change.

## 3. `.github/workflows/docs.yml`

```yaml
name: Documentation

on:
  push:
    branches: [lyrical]
  pull_request:

jobs:
  docs:
    uses: HonuRobotics/honu-docs/.github/workflows/docs.yml@v0.2.0
    permissions:
      contents: write
    with:
      default_version: lyrical
```

Add each new distribution branch to `push.branches` as it is created.
`default_version` chooses which branch owns the site root redirect; leave
it out to use the repository default branch.

## One time repository setup

1. Push once so the workflow creates the `gh-pages` branch.
2. In the repository settings, enable GitHub Pages from the `gh-pages`
   branch, root folder.
3. Point the repository About URL and a short README at the site.

The site appears at `https://honurobotics.github.io/<repository>/`.

## Writing pages

Pages are MyST Markdown. Hidden `toctree` blocks in section index pages
build the sidebar; the `colon_fence` extension is enabled so admonitions
can be written with `:::` fences, and diagrams are text in
```` ```{mermaid} ```` blocks (rendered in the browser). Build locally with:

```bash
pip install -r docs/requirements.txt
sphinx-build -W docs _build/html
python3 -m http.server -d _build/html
```

# honu-docs

Shared documentation tooling for Honu Robotics repositories: the `mkdocs-honu`
branding package (MkDocs Material theme defaults, palette, logo, template
overrides) and the reusable GitHub Actions workflow that builds and deploys
versioned documentation to GitHub Pages with `mike`.

## Consumer setup

`docs/requirements.txt`:

```
git+https://github.com/HonuRobotics/honu-docs
```

`mkdocs.yml`:

```yaml
site_name: BlueRobotics Models
repo_url: https://github.com/HonuRobotics/bluerobotics_models
theme:
  name: material
plugins:
  - search
  - honu
nav:
  - Home: index.md
  # ...
```

`.github/workflows/docs.yml`:

```yaml
jobs:
  docs:
    uses: HonuRobotics/honu-docs/.github/workflows/docs.yml@main
```

Local preview:

```bash
pip install -r docs/requirements.txt
mkdocs serve
```

Versioning: the branch name is the docs version (ROS distro convention). The
reusable workflow runs `mike deploy <branch> latest` on pushes to distro
branches and a strict build check on pull requests.

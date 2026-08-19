# honu-docs

Shared documentation tooling for Honu Robotics repositories:

- **`sphinx-honu`**, a pip installable Sphinx extension giving every site
  the docs.ros.org look and behavior under Honu branding, MyST Markdown
  sources, a per distribution version flyout and GitHub edit links.
- **A reusable GitHub Actions workflow** that builds a repository's
  `docs/` strictly on pull requests and deploys one version per branch to
  GitHub Pages on push.

See the [documentation](https://honurobotics.github.io/honu-docs/) for
setup and the versioning model, or build it locally:

```bash
pip install . && sphinx-build -W docs _build/html
```

## Attribution

The theme configuration and the version flyout structure derive from
[ros2/ros2_documentation](https://github.com/ros2/ros2_documentation)
(CC BY 4.0), the source of docs.ros.org. Brand assets are Honu Robotics
originals, vendored from honurobotics.com.

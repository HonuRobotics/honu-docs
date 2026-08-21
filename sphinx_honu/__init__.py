"""Sphinx extension carrying the Honu Robotics documentation house style.

Consumers enable everything with ``extensions = ['sphinx_honu']``. The
extension applies the stock sphinx_rtd_theme configured exactly as
docs.ros.org (ros2/ros2_documentation) runs it, adds the Honu brand skin,
the version flyout and the GitHub edit link, and wires MyST so pages are
written in Markdown, with mermaid for diagrams.

Only settings the consumer left untouched are filled in, so any value set
explicitly in a consumer conf.py wins.

Environment contract (set by the reusable deploy workflow):
  DOCS_VERSION   name of the version being built (the branch name)
  DOCS_BASEURL   site root path prefix, e.g. /bluerobotics_models/
  DOCS_VERSIONS  optional space or comma separated build time version list;
                 the deployed site refines the flyout at runtime from
                 <site root>/versions.json
"""

import os
from pathlib import Path

__version__ = '0.2.0'

_HERE = Path(__file__).resolve().parent

# Copied verbatim from ros2/ros2_documentation (docs.ros.org), CC BY 4.0.
_THEME_OPTIONS = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': -1,
}


def _versions_from_env(current, base):
    """Build time flyout entries; the deployed site refines the list at
    runtime from <site root>/versions.json."""
    raw = os.environ.get('DOCS_VERSIONS', '')
    names = [name for name in raw.replace(',', ' ').split() if name]
    if current not in names:
        names.append(current)
    names.sort()
    return [(name, f'{base}{name}/') for name in names]


def _config_inited(app, config):
    if config.html_theme in ('default', 'alabaster'):
        config.html_theme = 'sphinx_rtd_theme'

    for key, value in _THEME_OPTIONS.items():
        config.html_theme_options.setdefault(key, value)

    config.html_static_path.append(str(_HERE / 'static'))
    config.templates_path.append(str(_HERE / 'templates'))
    if 'honu.css' not in config.html_css_files:
        config.html_css_files.append('honu.css')

    if not config.html_logo:
        config.html_logo = str(_HERE / 'static' / 'honu-robotics-white-logo.svg')
    if not config.html_favicon:
        config.html_favicon = str(_HERE / 'static' / 'honu-robotics-favicon.svg')

    if 'colon_fence' not in config.myst_enable_extensions:
        config.myst_enable_extensions = (
            list(config.myst_enable_extensions) + ['colon_fence'])

    current = os.environ.get('DOCS_VERSION') or 'local'
    base = os.environ.get('DOCS_BASEURL') or '/'
    if not config.version:
        config.version = current
        config.release = current

    context = config.html_context
    context.setdefault('current_version', current)
    context.setdefault('base_url', base)
    context.setdefault('versions', _versions_from_env(current, base))

    if config.honu_github and 'github_user' not in context:
        user, repo = config.honu_github
        context['display_github'] = True
        context['github_user'] = user
        context['github_repo'] = repo
        context['github_version'] = current
        context['conf_py_path'] = f'/{config.honu_docs_dir}/'


def setup(app):
    app.setup_extension('myst_parser')
    # Diagrams as text: ```{mermaid} blocks render client side, so pages
    # stay editable and the build needs no graphviz.
    app.setup_extension('sphinxcontrib.mermaid')
    app.add_config_value('honu_github', None, 'html')
    app.add_config_value('honu_docs_dir', 'docs', 'html')
    app.connect('config-inited', _config_inited)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

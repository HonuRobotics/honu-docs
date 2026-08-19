"""Honu Robotics branding plugin for MkDocs Material.

Consumer sites enable it with:

    theme:
      name: material
    plugins:
      - search
      - honu

The plugin injects the shared branding (logo, palette, fonts, CSS, template
overrides) and sane Material defaults, so per-repo mkdocs.yml files carry only
site identity and navigation. Anything a site sets explicitly wins over the
defaults injected here.
"""

from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import File, Files

_PKG = Path(__file__).parent

_THEME_DEFAULTS = {
    'palette': [
        {
            'media': '(prefers-color-scheme: light)',
            'scheme': 'default',
            'primary': 'custom',
            'accent': 'custom',
            'toggle': {'icon': 'material/weather-night',
                       'name': 'Switch to dark mode'},
        },
        {
            'media': '(prefers-color-scheme: dark)',
            'scheme': 'slate',
            'primary': 'custom',
            'accent': 'custom',
            'toggle': {'icon': 'material/weather-sunny',
                       'name': 'Switch to light mode'},
        },
    ],
    'features': [
        'navigation.sections',
        'navigation.top',
        'navigation.footer',
        'search.suggest',
        'search.highlight',
        'content.code.copy',
        'content.tabs.link',
    ],
    'icon': {'repo': 'fontawesome/brands/github'},
}

_MARKDOWN_DEFAULTS = [
    'admonition',
    'attr_list',
    'md_in_html',
    'tables',
    {'pymdownx.highlight': {'anchor_linenums': True}},
    'pymdownx.superfences',
    'pymdownx.tabbed',
    'pymdownx.details',
]


class HonuPlugin(BasePlugin):
    """Inject Honu branding and defaults into a Material site."""

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        theme = config.theme
        if theme.name != 'material':
            raise ValueError('the honu plugin requires theme.name: material')

        # Shared template overrides (version selector placement, footer).
        overrides = str(_PKG / 'overrides')
        if overrides not in theme.dirs:
            theme.dirs.insert(0, overrides)

        # Branding: only fill what the site did not set itself.
        for key, value in _THEME_DEFAULTS.items():
            if not theme.get(key):
                theme[key] = value
        if not theme.get('logo'):
            theme['logo'] = 'assets/honu-logo.svg'
        if not theme.get('favicon'):
            theme['favicon'] = 'assets/honu-logo.svg'

        config.extra_css = ['assets/honu.css'] + list(config.extra_css or [])
        if not config.copyright:
            config.copyright = 'Copyright © Honu Robotics'

        for ext in _MARKDOWN_DEFAULTS:
            name = ext if isinstance(ext, str) else next(iter(ext))
            if name not in config.markdown_extensions:
                if isinstance(ext, str):
                    config.markdown_extensions.append(ext)
                else:
                    config.markdown_extensions.append(name)
                    config.mdx_configs.update(ext)
        return config

    def on_files(self, files: Files, *, config: MkDocsConfig) -> Files:
        """Serve the packaged brand assets as site files under assets/."""
        for asset in sorted((_PKG / 'assets').iterdir()):
            uri = f'assets/{asset.name}'
            if not files.get_file_from_path(uri):
                files.append(File.generated(config, uri,
                                            abs_src_path=str(asset)))
        return files

"""Build the fixture consumer end to end and assert on the output.

These assertions pin the behaviors that broke during prototyping: the brand
CSS shipping inside the wheel, the hover deviation, the flyout with absolute
URLs and the runtime versions.json hook, and the GitHub edit link wiring.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / 'fixture' / 'docs'


def build(tmp_path, env_extra=None):
    env = os.environ.copy()
    env.update(env_extra or {})
    out = tmp_path / 'html'
    subprocess.run(
        [sys.executable, '-m', 'sphinx', '-W', '-b', 'html',
         str(FIXTURE), str(out)],
        check=True, env=env, capture_output=True, text=True)
    return out


@pytest.fixture(scope='module')
def site(tmp_path_factory):
    return build(tmp_path_factory.mktemp('site'),
                 {'DOCS_VERSION': 'lyrical', 'DOCS_BASEURL': '/fixture/',
                  'DOCS_VERSIONS': 'lyrical m-distro'})


def test_theme_and_brand_assets(site):
    index = (site / 'index.html').read_text()
    assert '_static/css/theme.css' in index, 'sphinx_rtd_theme not applied'
    assert 'honu.css' in index
    assert (site / '_static' / 'honu-robotics-white-logo.svg').exists()
    assert (site / '_static' / 'honu-robotics-favicon.svg').exists()
    css = (site / '_static' / 'honu.css').read_text()
    assert '#082133' in css, 'brand palette missing'
    assert '!important' in css, 'the one hover deviation went missing'


def test_version_flyout(site):
    index = (site / 'index.html').read_text()
    assert 'rst-versions' in index
    assert 'v: lyrical' in index
    assert 'data-version="lyrical"' in index
    assert 'data-version="m-distro"' in index
    assert 'href="/fixture/m-distro/"' in index, 'flyout URLs must be absolute'
    assert 'versions.json' in index, 'runtime version refresh missing'


def test_github_edit_link(site):
    usage = (site / 'usage.html').read_text()
    assert 'HonuRobotics' in usage and 'fixture' in usage
    assert 'lyrical/docs/usage.md' in usage, 'edit link must target the branch'


def test_myst_note_rendered(site):
    index = (site / 'index.html').read_text()
    assert 'admonition note' in index, 'colon fence admonition not rendered'


def test_mermaid_diagrams_render(site):
    usage = (site / 'usage.html').read_text()
    assert 'mermaid' in usage, 'mermaid block did not reach the page'
    assert 'graph LR' in usage


def test_local_build_defaults(tmp_path):
    out = build(tmp_path, {'DOCS_VERSION': '', 'DOCS_BASEURL': '',
                           'DOCS_VERSIONS': ''})
    index = (out / 'index.html').read_text()
    assert 'v: local' in index
    assert 'href="/local/"' in index

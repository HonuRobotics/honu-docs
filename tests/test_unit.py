"""Unit tests for the pure helpers."""

import json

from sphinx_honu import _versions_from_env
from sphinx_honu.deploy import redirect_html, update_versions


def test_versions_from_env_includes_current_and_sorts(monkeypatch):
    monkeypatch.setenv('DOCS_VERSIONS', 'm-distro, lyrical')
    assert _versions_from_env('lyrical', '/repo/') == [
        ('lyrical', '/repo/lyrical/'),
        ('m-distro', '/repo/m-distro/'),
    ]
    monkeypatch.setenv('DOCS_VERSIONS', '')
    assert _versions_from_env('local', '/') == [('local', '/local/')]


def test_update_versions_upserts_and_sorts(tmp_path):
    update_versions(tmp_path, 'm-distro', '/repo/')
    update_versions(tmp_path, 'lyrical', '/repo/')
    update_versions(tmp_path, 'lyrical', '/repo/')
    entries = json.loads((tmp_path / 'versions.json').read_text())
    assert entries == [
        {'name': 'lyrical', 'url': '/repo/lyrical/'},
        {'name': 'm-distro', 'url': '/repo/m-distro/'},
    ]


def test_redirect_html_targets_version():
    html = redirect_html('lyrical')
    assert 'url=lyrical/' in html
    assert "location.replace('lyrical/'" in html

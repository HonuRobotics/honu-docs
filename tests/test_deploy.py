"""Exercise the deploy tool against a local bare origin: first deploy
bootstraps gh-pages, later deploys add versions, the default version owns
the root redirect, and .nojekyll plus versions.json stay maintained."""

import json
import subprocess
from pathlib import Path

import pytest

from sphinx_honu import deploy


def git(*cmd, cwd):
    return subprocess.run(['git', *cmd], cwd=cwd, check=True,
                          capture_output=True, text=True).stdout


@pytest.fixture()
def repos(tmp_path):
    origin = tmp_path / 'origin.git'
    origin.mkdir()
    git('init', '--bare', '--quiet', cwd=origin)
    repo = tmp_path / 'repo'
    repo.mkdir()
    git('init', '--quiet', '-b', 'main', cwd=repo)
    git('config', 'user.name', 'Test', cwd=repo)
    git('config', 'user.email', 'test@example.com', cwd=repo)
    (repo / 'README.md').write_text('fixture\n')
    git('add', '.', cwd=repo)
    git('commit', '--quiet', '-m', 'init', cwd=repo)
    git('remote', 'add', 'origin', str(origin), cwd=repo)
    git('push', '--quiet', '-u', 'origin', 'main', cwd=repo)
    return repo, origin


def html_site(tmp_path, name, marker):
    site = tmp_path / name
    (site / '_static').mkdir(parents=True)
    (site / 'index.html').write_text(f'<html>{marker}</html>\n')
    (site / '_static' / 'style.css').write_text('body {}\n')
    (site / '.buildinfo').write_text('build info\n')
    return site


def run_deploy(repo, html, version, make_default=False):
    argv = ['--repo', str(repo), '--html', str(html), '--version', version,
            '--base-url', '/fixture/']
    if make_default:
        argv.append('--make-default')
    deploy.main(argv)


def pages_clone(origin, tmp_path):
    clone = tmp_path / 'pages-clone'
    subprocess.run(['git', 'clone', '--quiet', '--branch', 'gh-pages',
                    str(origin), str(clone)],
                   check=True, capture_output=True, text=True)
    return clone


def test_full_deploy_lifecycle(tmp_path, repos):
    repo, origin = repos

    run_deploy(repo, html_site(tmp_path, 'a', 'lyrical-v1'), 'lyrical',
               make_default=True)
    run_deploy(repo, html_site(tmp_path, 'b', 'm-distro-v1'), 'm-distro')
    run_deploy(repo, html_site(tmp_path, 'c', 'lyrical-v2'), 'lyrical',
               make_default=True)

    pages = pages_clone(origin, tmp_path)

    assert (pages / '.nojekyll').exists(), \
        'without .nojekyll GitHub Pages drops _static'
    assert (pages / 'lyrical' / '_static' / 'style.css').exists()
    assert 'lyrical-v2' in (pages / 'lyrical' / 'index.html').read_text(), \
        'redeploy must replace the old build'
    assert 'm-distro-v1' in (pages / 'm-distro' / 'index.html').read_text()
    assert not (pages / 'lyrical' / '.buildinfo').exists(), \
        'build byproducts must not deploy'

    versions = json.loads((pages / 'versions.json').read_text())
    assert versions == [
        {'name': 'lyrical', 'url': '/fixture/lyrical/'},
        {'name': 'm-distro', 'url': '/fixture/m-distro/'},
    ]

    root = (pages / 'index.html').read_text()
    assert 'url=lyrical/' in root, 'root must redirect to the default version'

    assert not git('worktree', 'list', '--porcelain', cwd=repo).count('gh-pages') > 1, \
        'worktrees must be cleaned up'


def test_nondefault_deploy_leaves_redirect_alone(tmp_path, repos):
    repo, origin = repos
    run_deploy(repo, html_site(tmp_path, 'a', 'lyrical'), 'lyrical',
               make_default=True)
    run_deploy(repo, html_site(tmp_path, 'b', 'm-distro'), 'm-distro')
    pages = pages_clone(origin, tmp_path)
    assert 'url=lyrical/' in (pages / 'index.html').read_text(), \
        'a non default deploy must not steal the root redirect'


def test_unchanged_deploy_is_noop(tmp_path, repos, capsys):
    repo, _ = repos
    site = html_site(tmp_path, 'a', 'same')
    run_deploy(repo, site, 'lyrical', make_default=True)
    run_deploy(repo, site, 'lyrical', make_default=True)
    assert 'nothing to deploy' in capsys.readouterr().out

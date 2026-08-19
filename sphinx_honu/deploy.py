"""Publish a built Sphinx site to the gh-pages branch.

Layout maintained on gh-pages:

  .nojekyll       keeps GitHub Pages from running Jekyll, which would drop
                  the underscore directories Sphinx relies on (_static, ...)
  versions.json   the version flyout refreshes from this at runtime
  index.html      redirect to the default version, written only when the
                  default version deploys
  <version>/      one built site per deployed branch

The tool operates on a normal clone (the Actions checkout), publishing
through a temporary git worktree and retrying the push a few times so two
branches deploying at once do not clobber each other.
"""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

PAGES_BRANCH = 'gh-pages'
PUSH_ATTEMPTS = 3


def run(*cmd, cwd=None, check=True):
    return subprocess.run(list(cmd), cwd=cwd, check=check,
                          capture_output=True, text=True)


def redirect_html(version):
    return f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="0; url={version}/">
    <link rel="canonical" href="{version}/">
    <script>window.location.replace('{version}/' + window.location.hash);</script>
  </head>
  <body>
    <a href="{version}/">Redirecting to the {version} documentation.</a>
  </body>
</html>
"""


def update_versions(pages_dir, name, base_url):
    """Insert or refresh one entry in versions.json, keeping the list
    sorted by name. Removing a version (end of life) is a deliberate manual
    operation: delete its directory and its entry here."""
    path = Path(pages_dir) / 'versions.json'
    entries = json.loads(path.read_text()) if path.exists() else []
    entries = [entry for entry in entries if entry['name'] != name]
    entries.append({'name': name, 'url': f'{base_url}{name}/'})
    entries.sort(key=lambda entry: entry['name'])
    path.write_text(json.dumps(entries, indent=2) + '\n')
    return entries


def checkout_pages(repo_dir, worktree):
    """Attach a worktree on gh-pages, creating the branch as an orphan on
    the first ever deploy."""
    fetched = run('git', 'fetch', 'origin', PAGES_BRANCH,
                  cwd=repo_dir, check=False).returncode == 0
    if fetched:
        run('git', 'worktree', 'add', '--force', '-B', PAGES_BRANCH,
            str(worktree), f'origin/{PAGES_BRANCH}', cwd=repo_dir)
    else:
        run('git', 'worktree', 'add', '--force', '--detach', str(worktree),
            cwd=repo_dir)
        run('git', 'checkout', '--orphan', PAGES_BRANCH, cwd=worktree)
        run('git', 'rm', '-rfq', '--ignore-unmatch', '.', cwd=worktree)


def publish(worktree, message):
    run('git', 'add', '--all', cwd=worktree)
    if not run('git', 'status', '--porcelain', cwd=worktree).stdout.strip():
        return 'nothing to deploy'
    run('git', 'commit', '--quiet', '--message', message, cwd=worktree)
    last = None
    for _ in range(PUSH_ATTEMPTS):
        last = run('git', 'push', 'origin', PAGES_BRANCH,
                   cwd=worktree, check=False)
        if last.returncode == 0:
            return 'deployed'
        run('git', 'pull', '--rebase', 'origin', PAGES_BRANCH,
            cwd=worktree, check=False)
    raise SystemExit(f'push to {PAGES_BRANCH} failed after '
                     f'{PUSH_ATTEMPTS} attempts:\n{last.stderr}')


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Publish a built Sphinx site to the gh-pages branch.')
    parser.add_argument('--html', required=True,
                        help='directory holding the built HTML site')
    parser.add_argument('--version', required=True,
                        help='version name to publish under (the branch name)')
    parser.add_argument('--base-url', default='/',
                        help='site root path prefix, e.g. /bluerobotics_models/')
    parser.add_argument('--make-default', action='store_true',
                        help='also point the site root redirect at this version')
    parser.add_argument('--repo', default='.',
                        help='repository clone to publish from')
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    html = Path(args.html).resolve()

    with tempfile.TemporaryDirectory() as tmp:
        worktree = Path(tmp) / PAGES_BRANCH
        checkout_pages(repo, worktree)
        try:
            target = worktree / args.version
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(
                html, target,
                ignore=shutil.ignore_patterns('.doctrees', '.buildinfo'))
            (worktree / '.nojekyll').touch()
            update_versions(worktree, args.version, args.base_url)
            if args.make_default:
                (worktree / 'index.html').write_text(
                    redirect_html(args.version))
            print(publish(worktree, f'Deploy {args.version} documentation'))
        finally:
            run('git', 'worktree', 'remove', '--force', str(worktree),
                cwd=repo, check=False)


if __name__ == '__main__':
    main()

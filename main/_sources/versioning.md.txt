# Versioning model

One branch is one documentation version, named after the ROS distribution
(`lyrical`, `m-distro`, ...). Each push builds only that branch with plain
`sphinx-build` and deploys it to `gh-pages/<branch>/`. There is no
multiversion machinery; docs.ros.org needs a vendored sphinx-multiversion
because it rebuilds every ref in one job, and this model does not.

## The flyout

The lower left flyout lists all deployed versions and keeps the reader on
the same page when switching. Each deploy refreshes `versions.json` at the
site root, and every page reads it at runtime, so a site built before a
new distribution existed still offers it in the flyout without a rebuild.
When the file is unreachable (local preview, offline) the flyout falls
back to the list known at build time.

## The root redirect

The bare site URL redirects to the default version. Only a deploy of the
branch named by the `default_version` workflow input rewrites the
redirect, so deploying an older distribution never steals the root. Each
repository chooses its own default.

## End of life

Removing a distribution is a deliberate manual operation, not something
the automation does:

1. On `gh-pages`, delete the version directory.
2. Remove its entry from `versions.json`.
3. If it was the default, point `index.html` and the `default_version`
   input at the new default.

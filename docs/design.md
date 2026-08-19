# Design notes

## Stock functionality, painted

The stack is Sphinx, sphinx_rtd_theme and MyST, configured exactly as
docs.ros.org runs it: the theme options are copied verbatim from
`ros2/ros2_documentation` and the CSS starts from their single content
width rule. Everything Honu adds is paint (brand colors, logo, favicon)
with one documented behavioral deviation: the theme's expanded sidebar
items rest on a grey that outranks its own hover rule, so hover is
invisible there (docs.ros.org shows the same dead hover); `honu.css`
restores a visible hover with one `!important` rule.

The flyout template structure also derives from `ros2/ros2_documentation`
(CC BY 4.0), extended with same page switching and the runtime
`versions.json` refresh.

## Why a shared repository

Every problem found while prototyping (a Pages Jekyll pitfall, flyout URL
resolution from subpages, CSS specificity clashes) lived in the shared
machinery, not in any repository's content. Fixing such problems here
fixes them for every consumer on its next pin bump.

## What runs in CI

- Unit tests for the pure helpers.
- A fixture consumer built end to end, asserting on the produced HTML:
  theme applied, brand assets shipped in the wheel, flyout URLs absolute,
  GitHub edit links targeting the branch. The package installs non
  editable so missing wheel data fails loudly.
- Deploy lifecycle tests against a local bare origin: `gh-pages`
  bootstrap, `.nojekyll`, `versions.json` upserts, root redirect
  ownership, redeploy replacement.
- This site itself deploys through the reusable workflow (dogfood).
- A weekly scheduled run repeats the tests against freshly resolved
  dependencies to catch new Sphinx, theme or MyST releases early.

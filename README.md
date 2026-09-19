# AI/ML/Data Science Workbook

Macbook Stash backup. All projects are light-weighted and pulled or dependent on VMs.

# Workspace Directory Overview

```.
├── _kit
├── _utils
├── blog-mimi
│   └── docs
│       ├── blog
│       │   ├── 2026
│       │   └── posts
│       └── stylesheets
├── projects
│   ├── 2025-adaptive-immune-profiling
│   ├── 2025-brain-to-text
│   │   ├── notebooks
│   │   └── src
│   ├── 2025-chart-students-map
│   ├── 2025-hedge-fund-forecasting
│   ├── 2025-helios-commodity
│   │   └── notebooks
│   ├── 2025-rsna-competition
│   ├── 2026-aimo3
│   ├── 2026-customer-analytics-with-dl
│   └── 2026-march-madness-ncaa
│       └── references
├── scripts
├── textbook
│   └── chapters
└── workspace
    ├── demo
    ├── notebooks
    └── src
```

## Git Tracking Brief 

This workspace is a monorepo with nested repos. Git submodules

| Path | Remote | Purpose |
|---|---|---|
| `~/Projects` (parent) | [`whoamimi/workspace`](https://github.com/whoamimi/workspace) | Main workspace, branch `main` |
| `blog-mimi/` | [`whoamimi/whoamimi.github.io`](https://github.com/whoamimi/whoamimi.github.io) | MkDocs blog in subdirectory path: [/blog](./blog-mimi), live at https://whoamimi.github.io |
| `plug-mimi/` | [`whoamimi/plugin-mimi`](https://github.com/whoamimi/plugin-mimi)| Submodule git init subdirectory path: [/plugin-mimi](./plug-mimi) |

### How submodules work

- A submodule is its own repo. The parent stores only a pointer to one commit.
- Commit and push inside the submodule first. Then run `git add <submodule>` and commit in the parent to update the pointer.
- Loose edits inside a submodule show as `modified content` in the parent. That is normal.
- Clone everything with `git clone --recurse-submodules https://github.com/whoamimi/workspace.git`.
- Pull submodule updates with `git submodule update --init --recursive`.

### Blog deployment

- Source lives in `blog-mimi/` (`mkdocs.yml` and `docs/`).
- A GitHub Actions workflow at `blog-mimi/.github/workflows/deploy.yml` runs on every push to `main`.
- It runs `mkdocs gh-deploy --force --remote-branch gh-pages`.
- GitHub Pages serves the `gh-pages` branch (`/ (root)`).
- To deploy manually, run `mkdocs gh-deploy --force --remote-branch gh-pages` from `blog-mimi/`.
- Never push built HTML to `main`. Keep `main` for source only.

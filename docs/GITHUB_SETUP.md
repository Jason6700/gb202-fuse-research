# Publishing this repository on GitHub

## Recommended settings

- Repository name: `gb202-fuse-research`
- Description: `Software-only feasibility research into NVIDIA GB202 SM and L2 cache floorsweeping, fuse masks and firmware overrides.`
- Visibility: **Public**, once you have reviewed the files and redacted any local device data.
- License: **MIT**, already included.
- Default branch: `main`.
- Issues: enabled.
- Discussions: optional.

## From PowerShell using GitHub CLI

Prerequisites: [Git](https://git-scm.com/downloads/win) and [GitHub CLI](https://cli.github.com/); a GitHub account.

1. Extract the ZIP. Open PowerShell **inside** the `gb202-fuse-research` folder.
2. Run:

```powershell
git init -b main
git add .
git commit -m "Initialize GB202 software-only research"
gh auth login
gh repo create gb202-fuse-research --public --source . --remote origin --push
```

If Git asks for an author identity, configure your desired public attribution using `git config user.name "..."` and `git config user.email "..."` before committing. Do not publish your personal email unless you wish to; GitHub supports a no-reply commit address.

## Without GitHub CLI

1. Create an empty **public** repository at https://github.com/new named `gb202-fuse-research` (do not auto-create README, license or .gitignore since those exist in this starter).
2. From the extracted project folder, run:

```powershell
git init -b main
git add .
git commit -m "Initialize GB202 software-only research"
git remote add origin https://github.com/YOUR_USERNAME/gb202-fuse-research.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub handle. Authentication will be handled by your configured Git credential manager or GitHub authentication method.

## Suggested first tasks

Create GitHub Issues using the checklist in [RESEARCH_PLAN.md](RESEARCH_PLAN.md). Start with a read-only baseline capture before architecture-specific investigation. Do not commit full driver logs or private device identifiers.

## First local verification

```powershell
python -m unittest discover -s tests -v
python tools/collect_baseline.py --output reports/my-5090-baseline.json
```

The optional `cuda_probe.cu` needs `nvcc` and a compatible CUDA toolkit; the baseline Python tool does not. This starter package's CUDA probe has not been executed against your GPU yet.

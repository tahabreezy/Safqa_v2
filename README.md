# Safqa_v2

This repository contains the SAFQA V2 application.

## Project structure

- `safqa/` — main application source tree, including backend, frontend, scraper, and infrastructure config
- `README.md` — repository overview and branch workflow guidance
- `.gitignore` — root Git ignore rules
- `.github/workflows/ci-staging.yml` — staging CI workflow (moved to repository root on `dev` branch)

## Branch strategy

- `main` is the primary branch for production-ready code.
- `dev` is the staging branch used for development and CI validation.
- Push to `dev` to trigger the CI workflow at `.github/workflows/ci-staging.yml`.

## GitHub Actions

The staging workflow runs on `push` to `dev` and includes:

- backend tests and linting
- Docker image builds for API, frontend, and scraper
- image push to GitHub Container Registry
- deployment via SSH to a staging VPS

## How to use

1. Clone the repository.
2. Work in the `safqa/` subfolder for the application code.
3. Create feature branches off `dev`.
4. Push your branch to GitHub and open a pull request into `main`.

## Release tagging

A release tag is created for the current version and pushed to GitHub. The tag format is `v<major>.<minor>.<patch>`.

## Notes

- This repository was initialized locally and pushed to `https://github.com/tahabreezy/Safqa_v2`.
- The staging CI workflow requires a `dev` branch on GitHub, so `dev` is created and pushed in this repo.

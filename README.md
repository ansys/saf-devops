# SAF DevOps

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

This repository contains reusable GitHub Actions and workflows for automating the release, build, and deployment processes for Ansys SAF projects.

## Features
- Automated release note generation
- Version bumping and tagging
- Building and publishing Python packages
- Documentation build and deployment
- SBOM (Software Bill of Materials) generation and upload
- Artifact management and release asset uploads
- Compatibility and dependency checks

## Structure
- Each subfolder contains a custom GitHub Action or workflow component.
- Workflows are defined in `.github/workflows/` and can be called or reused by other repositories.

## Usage
You can use these actions in your own workflows by referencing them, for example:

```yaml
jobs:
  generate-release-notes:
    uses: ansys/saf-devops/generate-release-notes@v1
    with:
      tag-name: ${{ github.ref }}
```

Or call the reusable workflows:

```yaml
jobs:
  release:
    uses: ansys/saf-devops/.github/workflows/_release.yml@v1
    with:
      python-version: '3.12'
      poetry-version: '2.3.2'
      release-name: 'v1.0.0'
      release-branch: 'main'
```

## Permissions
Some actions require specific permissions. For example, to generate release notes or upload assets to a release, ensure your workflow grants the following permissions:

```yaml
permissions:
  contents: write
  pull-requests: read
```

## Contributing
Contributions are welcome! Please open issues or pull requests for improvements or bug fixes.

## License
This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

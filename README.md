# 📄 Wara<u>9</u>a - Intelligent Automated IT Documentation

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/elhajjaji/wara9a/workflows/tests/badge.svg)](https://github.com/elhajjaji/wara9a/actions)

> Open-source Python framework for intelligent automated documentation

**Wara<u>9</u>a** (وَرَقَة - "sheet" in Arabic) automatically transforms your IT projects into clear and professional documentation. Configure once, document forever.

## 🚀 Installation

```bash
# Basic installation (recommended)
pip install wara9a

# Connector dependencies are automatically installed
# based on your wara9a.yml configuration

# Or full installation if you prefer
pip install wara9a[all]
```

## ⚡ Quick Start

```bash
# 1. Initialize a new project
wara9a init

# 2. Configure your sources (edit wara9a.yml)

# 3. Generate documentation
wara9a generate
```

## 📁 Example Configuration

```yaml
# wara9a.yml
project:
  name: "My Awesome Project"
  version: "1.0.0"

sources:
  - type: github
    repo: my-org/my-repo
    token: ${GITHUB_TOKEN}
  
templates:
  - name: readme
    output: README.md
  - name: release_notes
    output: CHANGELOG.md

output:
  directory: docs/
  formats: [markdown, html]

# Dependencies are installed automatically
auto_install_deps: true
```

## 🏗️ Architecture

```
Sources → Connectors → Normalized Data → Templates → Documents
```

- **Modular connectors**: GitHub, Jira, Azure DevOps, local files...
- **Flexible templates**: Jinja2 with built-in template library
- **Multi-format**: Markdown, HTML, PDF
- **Automation**: Git hooks, CI/CD, webhooks

## 🔌 Available Connectors

- ✅ **GitHub**: Commits, issues, PRs, releases (*auto-install*)
- ✅ **Local Files**: README, CHANGELOG, docs/ (*built-in*)
- 🔜 **Jira**: Tickets, sprints, projects (*auto-install*)
- 🔜 **Azure DevOps**: Work items, builds, releases (*auto-install*)

> **Note**: Connector dependencies are automatically installed based on your configuration

## 📖 Documentation

- [User Guide](docs/user-guide.md)
- [Developing a Connector](docs/connector-dev.md)
- [API Reference](docs/api.md)
- [Examples](examples/)

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
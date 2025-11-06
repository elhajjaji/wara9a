# 📄 Wara<u>9</u>a - Intelligent Automated IT Documentation

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/elhajjaji/wara9a/workflows/tests/badge.svg)](https://github.com/elhajjaji/wara9a/actions)

> Open-source Python framework for intelligent automated documentation

**Wara<u>9</u>a** automatically transforms your IT projects into clear and professional documentation. Configure once, document forever.

## 🚀 Installation

### From PyPI (coming soon)
```bash
# Basic installation (recommended)
pip install wara9a

# Or full installation with all connectors
pip install wara9a[all]
```

### From Source
```bash
# Clone the repository
git clone https://github.com/elhajjaji/wara9a.git
cd wara9a

# Basic installation
pip install -r requirements.txt

# Development installation
pip install -r requirements-dev.txt

# Full installation (all connectors and generators)
pip install -r requirements-full.txt
```

## ⚡ Quick Start

```bash
# 1. Initialize a new project
wara9a init

# 2. Configure your sources (edit wara9a.yml)

# 3. Generate documentation
wara9a generate
```

## 🛠️ Development

### Cross-platform development commands:

```bash
# Windows
scripts\dev.bat [command]

# Unix/Linux/macOS  
./scripts/dev.sh [command]

# Or use Python directly (works everywhere)
python scripts/dev.py [command]
```

### Available commands:
- `install` - Install basic dependencies
- `install-dev` - Setup development environment
- `test` - Run tests
- `format` - Format code (black + isort)
- `lint` - Run linting (flake8 + mypy)
- `demo` - Run demo script
- `clean` - Clean build artifacts
- `check` - Run all quality checks

## 📁 Example Configuration

```yaml
# wara9a.yml
project:
  name: "My Awesome Project"
  version: "1.0.0"

sources:
  # Functional documentation from ticketing
  - type: jira
    project: MYPROJ
    token: ${JIRA_TOKEN}
    # Extracts: epics, features, user stories
  
  # Technical documentation from Git
  - type: github
    repo: my-org/my-repo
    token: ${GITHUB_TOKEN}
    # Extracts: commits, PRs, code structure
  
templates:
  - name: functional_spec  # Uses Jira data
    output: docs/functional-spec.md
  - name: technical_doc    # Uses GitHub data
    output: docs/technical.md
  - name: release_notes    # Combines both sources
    output: CHANGELOG.md

output:
  directory: docs/
  formats: [markdown, html]

# Dependencies are installed automatically
auto_install_deps: true
```

## 🏗️ Architecture

```
📋 Ticketing (Jira/Azure)  → Functional docs (epics, features) → ┐
                                                                  ├→ Templates → Documents
🔧 Git (GitHub/GitLab)     → Technical docs (commits, code)    → ┘
```

**Dual-source documentation strategy:**
- **Functional documentation** extracted from ticketing systems (epics, features, user stories)
- **Technical documentation** extracted from Git repositories and code (commits, PRs, architecture)

**Key features:**
- **Modular connectors**: Separate connectors for ticketing vs. Git sources
- **Flexible templates**: Jinja2 templates can combine both data sources
- **Multi-format**: Markdown, HTML, PDF
- **Automation**: Git hooks, CI/CD, webhooks

## 🔌 Available Connectors

### 📋 Functional Documentation (Ticketing Systems)
- 🔜 **Jira**: Epics, features, user stories, sprints (*auto-install*)
- 🔜 **Azure DevOps**: Work items, features, requirements (*auto-install*)

### 🔧 Technical Documentation (Git & Code)
- ✅ **GitHub**: Commits, PRs, releases, code structure (*auto-install*)
- 🔜 **GitLab**: Commits, merge requests, pipelines (*auto-install*)
- ✅ **Local Files**: README, CHANGELOG, docs/ (*built-in*)

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

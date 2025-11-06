# 🚀 Quick Start Guide - Wara<u>9</u>a

This guide will help you create your first automated documentation project with Wara<u>9</u>a.

## 📋 Prerequisites

- Python 3.9 or higher
- Git (optional, for repositories)
- GitHub token (optional, for private repositories)

## ⚡ Installation

```bash
# Basic installation (recommended)
cd wara9a/
pip install -e .

# Connector dependencies will be installed automatically
# based on your wara9a.yml configuration

# Optional: full installation
pip install -e .[all]
```

## 🏁 First Project

### 1. Initialize a Project

```bash
# Create a new project
wara9a init --name "My First Project"

# With a GitHub repository
wara9a init --name "My Project" --github-repo "my-org/my-repo"
```

This command creates:
- `wara9a.yml`: Project configuration
- `output/`: Folder for generated documentation

### 2. Configure Sources

Edit the generated `wara9a.yml` file:

```yaml
project:
  name: "My First Project"
  version: "1.0.0"
  description: "Automated documentation with Wara<u>9</u>a"

sources:
  # Local files (always available)
  - type: local_files
    name: "Local Documentation"
    path: "."
    patterns:
      - "README.md"
      - "CHANGELOG.md"
    enabled: true

  # GitHub (if you have a repository)
  - type: github
    name: "My GitHub Repository"
    repo: "my-org/my-repo"
    token: "${GITHUB_TOKEN}"  # Environment variable
    max_commits: 50
    enabled: true

templates:
  - name: readme
    output: "README_auto.md"
    enabled: true
    
  - name: changelog
    output: "CHANGELOG_auto.md"
    enabled: true

output:
  directory: "docs_generated"
  formats:
    - markdown
    - html
```

### 3. Configure GitHub Token (Optional)

```bash
# Set environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# Or in your shell profile (~/.zshrc, ~/.bashrc)
echo 'export GITHUB_TOKEN="ghp_your_token_here"' >> ~/.zshrc
```

### 4. Generate Documentation

```bash
# Full generation (automatically installs dependencies)
wara9a generate

# Preview before generation
wara9a generate --preview

# Generate a single template
wara9a generate --template readme

# Force fresh data collection
wara9a generate --force-refresh
```

> **Note**: During the first generation, Wara<u>9</u>a will automatically install the necessary dependencies based on your configured connectors.

## 📖 Useful Commands

### Configuration

```bash
# Show current configuration
wara9a config show

# Validate configuration
wara9a config validate
```

### Exploration

```bash
# List available connectors
wara9a connectors

# List built-in templates
wara9a templates
```

### Dependencies

```bash
# Check required dependencies
wara9a deps check

# Install missing dependencies
wara9a deps install

# List all connectors and their dependencies
wara9a deps list

# Installation simulation (dry-run mode)
wara9a deps install --dry-run
```

### Help

```bash
# General help
wara9a --help

# Help for specific command
wara9a generate --help
```

## 📁 File Structure

After initialization, your project looks like:

```
my-project/
├── wara9a.yml              # Main configuration
├── docs_generated/         # Generated documentation
│   ├── README_auto.md      # Generated README
│   ├── CHANGELOG_auto.md   # Generated changelog
│   └── *.html              # HTML versions
├── README.md               # Your original README
└── CHANGELOG.md            # Your original changelog
```

## 🎯 Common Examples

### GitHub-only Project

```yaml
project:
  name: "My Web App"
  
sources:
  - type: github
    repo: "my-org/my-app"
    token: "${GITHUB_TOKEN}"
    
templates:
  - name: readme
    output: "README_generated.md"
  - name: release_notes
    output: "RELEASE_NOTES.md"

output:
  formats: [markdown, html]
```

### Local-only Project

```yaml
project:
  name: "My Local Project"
  
sources:
  - type: local_files
    path: "."
    patterns: ["README.md", "docs/**/*.md"]
    
templates:
  - name: readme
    output: "documentation.md"

output:
  directory: "generated"
  formats: [markdown]
```

### Multi-source Project

```yaml
project:
  name: "Complex Project"
  
sources:
  - type: github
    repo: "org/backend"
    name: "Backend API"
  - type: github  
    repo: "org/frontend"
    name: "Frontend App"
  - type: local_files
    path: "docs"
    name: "Local Documentation"
    
templates:
  - name: readme
    output: "README_complete.md"
  - name: changelog
    output: "HISTORY.md"

output:
  formats: [markdown, html]
```

## 🔧 Troubleshooting

### GitHub Token

If you have authentication errors:

1. Create a token on GitHub: Settings > Developer settings > Personal access tokens
2. Required permissions: `repo` (for private repos) or `public_repo`
3. Set the variable: `export GITHUB_TOKEN="ghp_..."`

### Connector Errors

```bash
# Test connection
wara9a connectors

# Validate config
wara9a config validate
```

### Detailed Logs

```bash
# Verbose mode
wara9a generate --verbose
```

## 📚 Next Steps

1. **Customize templates**: Create your own Jinja2 templates
2. **Automate**: Integrate into your CI/CD
3. **Extend**: Develop custom connectors
4. **Share**: Contribute to the Wara9a community

## 🆘 Need Help?

- 📖 Documentation: [docs/](../docs/)
- 💡 Examples: [examples/](../examples/)
- 🐛 Issues: [GitHub Issues](https://github.com/elhajjaji/wara9a/issues)
- 💬 Community: [Discussions](https://github.com/elhajjaji/wara9a/discussions)

---

**Wara<u>9</u>a**: Because good documentation should never be a manual effort! ✨
# 📄 Wara<u>9</u>a - Documentation IT Automatique et Intelligente

**Wara<u>9</u>a** is an open-source Python framework that automatically transforms your IT projects into clear and professional documentation. Configure once, document forever.

## 🎯 Philosophy

Wara<u>9</u>a starts from a simple principle: **your project already contains all its documentation**, it's just scattered across different sources. Wara<u>9</u>a gathers this information and transforms it into professional documents, automatically.

### 📊 Dual Data Sources Strategy

**Wara<u>9</u>a** intelligently combines two complementary documentation sources:

1. **📋 Functional Documentation** → Extracted from **ticketing systems**
   - Epics, features, user stories (Jira, Azure DevOps)
   - Business requirements and specifications
   - Sprint planning and project roadmap
   - User-facing features and capabilities

2. **🔧 Technical Documentation** → Extracted from **Git repositories & code**
   - Commits history and code changes (GitHub, GitLab)
   - Pull requests and code reviews
   - Technical architecture from code structure
   - API documentation from source code

---

## ✨ Main Features

### 🔌 Plug & Play Connectors
- **Ticketing connectors**: Jira, Azure DevOps for functional documentation (epics, features, stories)
- **Git connectors**: GitHub, GitLab for technical documentation (commits, PRs, code)
- **Universal format**: All connectors speak the same language (JSON/YAML)
- **Extensible**: Create your own connectors in just a few lines of Python
- **Community marketplace**: Share and reuse connectors created by the community

### ⚙️ Ultra-Simple Configuration
```yaml
# wara9a.yml - That's all you need!
project:
  name: "My Awesome Project"
  
sources:
  # Functional documentation from ticketing
  - type: jira
    project: PROJ
    # Extracts: epics, features, user stories
  
  - type: azure_devops
    project: MyProject
    # Extracts: work items, features, requirements
    
  # Technical documentation from Git/code
  - type: github
    repo: my-org/my-repo
    # Extracts: commits, PRs, code structure
    
  - type: gitlab
    project: my-project
    # Extracts: commits, merge requests, pipelines
    
templates:
  - functional_spec    # Uses ticketing data
  - technical_doc      # Uses Git/code data
  - release_notes      # Combines both sources
  
output:
  formats: [pdf, html, markdown]
```

### 🤖 Intelligent Automation
- **Flexible triggers**: On commit, PR, release, or custom event
- **CI/CD integration**: GitHub Actions, GitLab CI, Azure Pipelines, Jenkins...
- **Manual mode**: Simple `wara9a generate` command for testing
- **Webhooks**: Generation triggered by any external event

### 🎨 Powerful and Flexible Templates
- **Template library**: Technical documentation, release notes, user guides, sprint reports...
- **Multi-templates**: Generate multiple document types in a single pass
- **Customizable**: Jinja2 engine to adapt each template to your needs
- **Themes**: Apply your brand guidelines with just a few clicks

### 📤 Professional Exports
- **PDF**: Print-ready documents with professional layout
- **HTML**: Interactive and responsive documentation sites
- **Markdown**: Documentation versioned with your code
- **Guaranteed quality**: Automatic layout, table of contents, index, cross-references

---

## 🏗️ Architecture

### Modular Principle
```
Ticketing Systems (Jira/Azure DevOps) → Functional Data → ┐
                                                           ├→ Templates → Documents
Git Repositories (GitHub/GitLab)      → Technical Data  → ┘
```

Inspired by dbt and the best Python frameworks, Wara<u>9</u>a adopts a clear architecture:

1. **Connectors**: 
   - Ticketing connectors extract functional documentation (epics, features, stories)
   - Git connectors extract technical documentation (commits, PRs, code)
2. **Normalizer**: Transforms all data into unified format
3. **Template engine**: Jinja2 combines both data sources for maximum flexibility
4. **Generators**: PDF (ReportLab), HTML, Markdown exports

### Extensibility
Each component can be replaced or extended:
- Add a connector for your proprietary API
- Create custom templates for your specific needs
- Develop post-processors to enrich data
- Integrate your own output generators

---

## 🚀 Quick Start

```bash
# Installation
pip install wara9a

# Initialization
wara9a init

# Configuration (edit wara9a.yml)
# ... add your sources ...

# Generation
wara9a generate

# Automation
wara9a setup-hooks  # Configure Git hooks automatically
```

---

## 💎 Strengths

### ✅ **Simplicity**
- Configuration in a single readable YAML file
- Intuitive CLI with explicit commands
- Abundant documentation and examples

### ✅ **Flexibility**
- Connectors for all popular sources
- Templates adaptable to all use cases
- Configurable triggers according to your workflows

### ✅ **Quality**
- Professional ready-to-use documents
- Automatic and consistent layout
- Multi-language support and internationalization

### ✅ **Open Source**
- Permissive license (MIT)
- Contributions welcome
- Active and welcoming community

---

## 🌟 Use Cases

- **Functional Specifications**: Generated from Jira epics and features for product documentation
- **Technical Documentation**: Extracted from Git commits and code structure for developer guides
- **Release Notes**: Combines ticketing stories and Git commits for complete changelog
- **Project Reports**: Sprint reports from Jira/Azure DevOps for stakeholders
- **Audit Documentation**: Complete traceability from requirements (tickets) to implementation (code)
- **Onboarding Guides**: Up-to-date documentation combining business context and technical details

---

## 🛣️ Roadmap

**v1.0** (Current version)
- ✅ Base connectors (GitHub, Jira, Azure DevOps)
- ✅ Essential templates
- ✅ PDF, HTML, Markdown exports
- ✅ Git hooks and CI/CD automation

**v2.0** (Future)
- 🔜 Access and permissions management
- 🔜 Advanced documentation versioning
- 🔜 Web interface for configuration
- 🔜 Connector and template marketplace
- 🔜 Documentation collaboration and review

---

## 🤝 Contributing

Wara<u>9</u>a is a community project. Whether you want to:
- Create a new connector
- Develop a template
- Fix a bug
- Improve documentation

**All contributions are welcome!**

---

**Wara<u>9</u>a**: Because good documentation should never be a manual effort.

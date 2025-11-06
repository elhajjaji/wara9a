# 📄 Wara<u>9</u>a - Documentation IT Automatique et Intelligente

**Wara<u>9</u>a** is an open-source Python framework that automatically transforms your IT projects into clear and professional documentation. Configure once, document forever.

## 🎯 Philosophy

Wara<u>9</u>a starts from a simple principle: **your project already contains all its documentation**, it's just scattered between your commits, tickets, APIs and code. Wara<u>9</u>a gathers this information and transforms it into professional documents, automatically.

---

## ✨ Main Features

### 🔌 Plug & Play Connectors
- **Connect your sources**: Azure DevOps, Jira, GitHub, GitLab, or any API
- **Universal format**: All connectors speak the same language (JSON/YAML)
- **Extensible**: Create your own connectors in just a few lines of Python
- **Community marketplace**: Share and reuse connectors created by the community

### ⚙️ Ultra-Simple Configuration
```yaml
# wara9a.yml - That's all you need!
project:
  name: "My Awesome Project"
  
sources:
  - type: github
    repo: my-org/my-repo
  - type: jira
    project: PROJ
    
templates:
  - technical_doc
  - release_notes
  
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
Sources → Connectors → Normalized Data → Templates → Documents
```

Inspired by dbt and the best Python frameworks, Wara<u>9</u>a adopts a clear architecture:

1. **Connectors**: Independent Python modules that extract data
2. **Normalizer**: Transforms all data into unified format
3. **Template engine**: Jinja2 for maximum flexibility
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

- **Releases**: Release notes automatically generated at each deployment
- **Audits**: Complete technical documentation for compliance
- **Onboarding**: Up-to-date guides for new developers
- **Reporting**: Sprint/project reports for stakeholders
- **Knowledge Base**: Technical wiki synchronized with code

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

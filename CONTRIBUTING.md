# 🤝 Contributing to Wara<u>9</u>a

Thank you for your interest in contributing to Wara<u>9</u>a! This guide will help you get started.

## 🎯 Types of Contributions

We accept several types of contributions:

### 🐛 Bug Reports
- Use GitHub Issues with the `bug` label
- Describe the problem with reproduction steps
- Include your environment (OS, Python, versions)

### ✨ New Features
- Open an issue first to discuss the idea
- Describe the use case and benefits
- Propose an implementation if possible

### 🔌 New Connectors
- Connectors for new APIs (Jira, Azure DevOps, etc.)
- Follow the `ConnectorBase` interface
- Include tests and documentation

### 📝 New Templates
- Templates for specific use cases
- Use Jinja2 with standardized variables
- Document the variables used

### 📚 Documentation
- README improvements
- Usage guides
- Practical examples
- Translations

## 🛠️ Development Setup

### Prerequisites
- Python 3.9+
- Git
- pip or poetry

### Installation
```bash
# Clone the repository
git clone https://github.com/elhajjaji/wara9a.git
cd wara9a

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install in development mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Project Structure
```
wara9a/
├── wara9a/
│   ├── core/           # Core engine
│   ├── connectors/     # Connectors
│   ├── generators/     # Output generators
│   ├── templates/      # Built-in templates
│   └── cli/           # CLI interface
├── tests/             # Unit tests
├── docs/              # Documentation
├── examples/          # Usage examples
└── demo.py           # Demo script
```

## 🧪 Tests

### Running Tests
```bash
# Full test suite
python -m pytest

# Tests with coverage
python -m pytest --cov=wara9a

# Specific tests
python -m pytest tests/test_connectors.py

# Verbose tests
python -m pytest -v
```

### Writing Tests
- One test per main feature
- Use fixtures for test data
- Mock external APIs
- Test error cases

### Test Example
```python
def test_new_connector():
    connector = MyConnector()
    config = SourceConfig(type="my_type", param="value")
    
    # Test validation
    errors = connector.validate_config(config)
    assert len(errors) == 0
    
    # Test collection (with mock if needed)
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {"data": "test"}
        
        result = connector.collect(config)
        assert isinstance(result, ProjectData)
```

## 📋 Contribution Process

### 1. Fork and Branch
```bash
# Fork on GitHub, then clone
git clone https://github.com/YOUR-USERNAME/wara9a.git

# Create a feature branch
git checkout -b feature/my-new-feature
```

### 2. Development
- Write clean, documented code
- Follow Python conventions (PEP 8)
- Add tests for your changes
- Update documentation if needed

### 3. Local Validation
```bash
# Linting and formatting
black wara9a/
isort wara9a/
flake8 wara9a/

# Tests
python -m pytest

# Demo
python demo.py
```

### 4. Pull Request
- Create a descriptive Pull Request
- Link related issues
- Wait for review and CI tests
- Address review comments

## 🔌 Developing a Connector

### Basic Structure
```python
class MyConnector(ConnectorBase):
    @property
    def connector_type(self) -> str:
        return "my_type"
    
    @property
    def display_name(self) -> str:
        return "My Service"
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Collection implementation
        pass
```

### Steps
1. Inherit from `ConnectorBase`
2. Implement abstract methods
3. Handle authentication if needed
4. Normalize to Wara<u>9</u>a models
5. Add comprehensive tests
6. Document usage

### Complete Example
See `wara9a/connectors/github.py` as reference.

## 📝 Developing a Template

### Jinja2 Template
```markdown
# {{ project.name }}

{{ project.description }}

## Statistics
- Commits: {{ data.commits | length }}
- Open Issues: {{ open_issues | length }}

{% for commit in recent_commits[:5] %}
- {{ commit.message | truncate(50) }} ({{ commit.date | format_date }})
{% endfor %}
```

### Available Variables
- `project.*`: Project metadata
- `data.*`: Collected data (commits, issues, etc.)
- `open_issues`: Open issues
- `recent_commits`: Recent commits
- `latest_release`: Latest release

### Custom Filters
- `format_date`: Format dates
- `truncate`: Truncate text
- `clean_commit_message`: Clean commit messages

## 📖 Conventions

### Code
- **Names**: snake_case for functions/variables, PascalCase for classes
- **Docstrings**: Google style format
- **Type hints**: Use type annotations
- **Imports**: Sorted with isort

### Git
- **Commits**: Descriptive messages in English
- **Branches**: `feature/`, `fix/`, `docs/`
- **Tags**: Semantic versioning (v1.0.0)

### Documentation
- Keep README updated with new features
- Docstrings for all public classes
- Usage examples in `examples/`
- User guide if needed

## 🚀 Roadmap and Priorities

### Current Version (1.0)
- ✅ Base architecture
- ✅ GitHub and local file connectors
- ✅ Essential templates
- ✅ Functional CLI

### Upcoming Versions
- 🔜 Jira connector
- 🔜 Azure DevOps connector
- 🔜 PDF generator
- 🔜 Advanced templates
- 🔜 Web interface
- 🔜 Cache system
- 🔜 Webhooks

### Wanted Contributions
- **Connectors**: Jira, Azure DevOps, GitLab
- **Templates**: Sprint reports, API guides
- **Generators**: PDF, LaTeX, Word
- **Integrations**: CI/CD, Git hooks
- **Documentation**: Tutorials, use cases

## 🆘 Support

### Questions
- GitHub Discussions for general questions
- Issues for specific bugs
- Discord/Slack (links coming soon)

### Resources
- [API Documentation](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Practical Examples](examples/)

## 📄 License

By contributing to Wara<u>9</u>a, you agree that your contributions will be licensed under MIT License.

## 🙏 Recognition

All contributors are listed in the AUTHORS.md file and recognized in release notes.

---

**Thank you for helping make automated documentation accessible to everyone! 🌟**
# Dual-Source Architecture

Wara9a implements a **dual-source documentation strategy** that separates functional and technical documentation.

## 📊 Documentation Categories

### 1. 📋 Functional Documentation (Ticketing Systems)

**Sources:** Jira, Azure DevOps, Linear, Asana

**Data Extracted:**
- Epics: High-level business initiatives
- Features: Major product capabilities  
- User Stories: Specific user requirements
- Sprint planning and roadmap
- Business requirements and specifications

**Use Cases:**
- Product specifications
- Business requirements documents
- Sprint reports for stakeholders
- Roadmap documentation
- Feature tracking

**Connector Base Class:** `TicketingConnector`

### 2. 🔧 Technical Documentation (Git Repositories)

**Sources:** GitHub, GitLab, Bitbucket

**Data Extracted:**
- Commits history and code changes
- Pull/Merge requests and code reviews
- Repository structure and architecture
- API documentation from code
- Technical architecture from code structure

**Use Cases:**
- Technical documentation for developers
- Code change history
- API documentation
- Architecture documentation
- Developer onboarding guides

**Connector Base Class:** `GitConnector`

### 3. 📁 File-Based Documentation

**Sources:** Local file system, cloud storage

**Data Extracted:**
- README, CHANGELOG
- Documentation directories
- Configuration files
- Existing documentation files

**Connector Base Class:** `FilesConnector`

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Data Sources                          │
├──────────────────────────┬──────────────────────────────────┤
│   📋 Ticketing Systems   │      🔧 Git Repositories         │
│   (Functional Docs)      │      (Technical Docs)            │
│                          │                                  │
│   • Jira                 │      • GitHub                    │
│   • Azure DevOps         │      • GitLab                    │
│   • Linear               │      • Bitbucket                 │
└──────────┬───────────────┴────────────┬─────────────────────┘
           │                            │
           ▼                            ▼
    TicketingConnector            GitConnector
           │                            │
           └────────────┬───────────────┘
                        ▼
                ConnectorBase (Normalization)
                        │
                        ▼
                  ProjectData (Unified Model)
                        │
                        ▼
                Template Engine (Jinja2)
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
      Functional   Technical    Combined
         Docs        Docs         Docs
```

## 💻 Implementation Guide

### Creating a Ticketing Connector

```python
from wara9a.core.connector_base import TicketingConnector
from wara9a.core.models import ProjectData, Issue, IssueType

class MyTicketingConnector(TicketingConnector):
    """
    Connector for functional documentation from MyTicketingSystem.
    
    Extracts: Epics, features, user stories
    Category: TICKETING
    """
    
    @property
    def connector_type(self) -> str:
        return "my_ticketing"
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Extract epics, features, stories
        issues = self._fetch_issues(config)
        
        return ProjectData(
            repository=self._create_repo_info(config),
            issues=issues,  # Functional items
            commits=[],     # No commits from ticketing
            pull_requests=[],
            releases=[],
            source_type=SourceType.CUSTOM,
            source_config={"type": "functional"}
        )
```

### Creating a Git Connector

```python
from wara9a.core.connector_base import GitConnector
from wara9a.core.models import ProjectData, Commit, PullRequest

class MyGitConnector(GitConnector):
    """
    Connector for technical documentation from MyGitSystem.
    
    Extracts: Commits, PRs, code structure
    Category: GIT
    """
    
    @property
    def connector_type(self) -> str:
        return "my_git"
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Extract commits, PRs, technical info
        commits = self._fetch_commits(config)
        prs = self._fetch_pull_requests(config)
        
        return ProjectData(
            repository=self._get_repo_info(config),
            commits=commits,        # Technical changes
            pull_requests=prs,      # Code reviews
            issues=[],              # No functional issues from Git
            releases=self._fetch_releases(config),
            source_type=SourceType.CUSTOM,
            source_config={"type": "technical"}
        )
```

## 📝 Template Usage

### Functional Documentation Template

```jinja2
{# Uses data from ticketing connectors #}
# Product Requirements

{% for issue in data.issues if issue.type == 'EPIC' %}
## Epic: {{ issue.title }}

**Status:** {{ issue.status }}
**Created:** {{ issue.created_at }}

{{ issue.description }}

### Features
{% for feature in data.issues if feature.type == 'FEATURE' %}
- {{ feature.title }}
{% endfor %}
{% endfor %}
```

### Technical Documentation Template

```jinja2
{# Uses data from Git connectors #}
# Technical Changes

## Recent Commits

{% for commit in data.commits[:50] %}
### {{ commit.date.strftime('%Y-%m-%d') }} - {{ commit.author.name }}

**{{ commit.message }}**

Files changed: {{ commit.files_changed|length }}
+{{ commit.additions }} -{{ commit.deletions }}
{% endfor %}
```

### Combined Documentation Template

```jinja2
{# Combines both data sources #}
# Release Notes

## Version {{ version }}

### Features Delivered
{% for issue in data.issues if issue.type == 'STORY' and issue.status == 'CLOSED' %}
- {{ issue.title }} ({{ issue.id }})
{% endfor %}

### Technical Changes
{% for commit in data.commits %}
- {{ commit.message }} ({{ commit.sha[:7] }})
{% endfor %}
```

## 🔧 Configuration

### Example: Combining Both Sources

```yaml
project:
  name: "My Project"
  version: "2.0.0"

sources:
  # Functional documentation from Jira
  - type: jira
    name: product-requirements
    project: MYPROJ
    token: ${JIRA_TOKEN}
    include_epics: true
    include_stories: true
    
  # Technical documentation from GitHub
  - type: github
    name: technical-changes
    repo: org/repo
    token: ${GITHUB_TOKEN}
    max_commits: 100

templates:
  # Uses Jira data only
  - name: functional_spec
    output: docs/requirements.md
    
  # Uses GitHub data only
  - name: technical_doc
    output: docs/technical.md
    
  # Combines both sources
  - name: release_notes
    output: CHANGELOG.md
```

## 🎯 Benefits

1. **Clear Separation of Concerns**
   - Functional docs from business tools (Jira)
   - Technical docs from dev tools (GitHub)

2. **Complete Documentation**
   - Requirements → Implementation traceability
   - Business context + Technical details

3. **Flexible Templates**
   - Use one source or combine both
   - Tailored to audience (stakeholders vs. developers)

4. **Extensible Architecture**
   - Easy to add new ticketing systems
   - Easy to add new Git platforms

## 📚 Further Reading

- [Creating Custom Connectors](connector-dev.md)
- [Template Development Guide](template-dev.md)
- [API Reference](api.md)

# Migration Guide: Legacy to Standardized Models

This guide helps you migrate from the old models (`Commit`, `Issue`, `PullRequest`) to the new standardized models (`TechnicalCommit`, `Epic`, `Feature`, `UserStory`, `TechnicalPullRequest`).

## 🎯 Why Migrate?

The new standardized models provide:
- ✅ **Clear separation**: Functional vs. Technical documentation
- ✅ **Richer data**: More fields and better structure
- ✅ **Consistency**: All connectors of the same type return identical structures
- ✅ **Type safety**: Better validation and IDE support
- ✅ **Template reusability**: Write once, use with any connector

## 📊 Migration Mapping

### Functional Documentation (Ticketing Connectors)

| Old Model | New Model | When to Use |
|-----------|-----------|-------------|
| `Issue` (type=EPIC) | `Epic` | High-level business initiatives |
| `Issue` (type=FEATURE) | `Feature` | Product features |
| `Issue` (type=STORY) | `UserStory` | User stories |
| `Issue` (other types) | `Requirement` | Formal requirements |

### Technical Documentation (Git Connectors)

| Old Model | New Model | Enhancement |
|-----------|-----------|-------------|
| `Commit` | `TechnicalCommit` | + detailed file changes, links to issues/PRs |
| `PullRequest` | `TechnicalPullRequest` | + reviewers, approval status, detailed metrics |

## 🔧 Migrating a Ticketing Connector

### Before (Old Code)

```python
from wara9a.core.connector_base import ConnectorBase
from wara9a.core.models import ProjectData, Issue, IssueStatus, IssueType, Author

class OldJiraConnector(ConnectorBase):
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Fetch issues from Jira
        raw_issues = self._fetch_jira_issues(config)
        
        # Convert to generic Issue objects
        issues = []
        for raw in raw_issues:
            issue = Issue(
                id=raw["key"],
                title=raw["fields"]["summary"],
                description=raw["fields"]["description"],
                status=IssueStatus.OPEN,
                type=IssueType.STORY,  # All treated the same
                author=Author(name=raw["fields"]["creator"]["displayName"]),
                created_at=datetime.fromisoformat(raw["fields"]["created"]),
                url=f"https://mycompany.atlassian.net/browse/{raw['key']}"
            )
            issues.append(issue)
        
        # Return with legacy structure
        return ProjectData(
            repository=Repository(name="project", full_name="project"),
            issues=issues,  # All mixed together
            commits=[],
            pull_requests=[],
            source_type=SourceType.JIRA
        )
```

### After (New Code)

```python
from wara9a.core.connector_base import TicketingConnector  # ← Specific base class
from wara9a.core.models import (
    ProjectData, FunctionalData,  # ← New structure
    Epic, Feature, UserStory,     # ← Specific models
    IssueStatus, Priority, Author
)

class NewJiraConnector(TicketingConnector):  # ← Inherit from TicketingConnector
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Fetch issues from Jira
        raw_issues = self._fetch_jira_issues(config)
        
        # Separate by type
        epics = []
        features = []
        user_stories = []
        
        for raw in raw_issues:
            issue_type = raw["fields"]["issuetype"]["name"].lower()
            
            if issue_type == "epic":
                epic = Epic(
                    id=raw["key"],
                    key=raw["key"],
                    title=raw["fields"]["summary"],
                    description=raw["fields"]["description"],
                    status=self._normalize_status(raw["fields"]["status"]),
                    priority=self._normalize_priority(raw["fields"]["priority"]),
                    author=Author(name=raw["fields"]["creator"]["displayName"]),
                    created_at=datetime.fromisoformat(raw["fields"]["created"]),
                    business_value=raw["fields"].get("customfield_10001"),  # ← Rich data
                    url=f"https://mycompany.atlassian.net/browse/{raw['key']}"
                )
                epics.append(epic)
                
            elif issue_type == "feature":
                feature = Feature(
                    id=raw["key"],
                    key=raw["key"],
                    title=raw["fields"]["summary"],
                    description=raw["fields"]["description"],
                    status=self._normalize_status(raw["fields"]["status"]),
                    priority=self._normalize_priority(raw["fields"]["priority"]),
                    epic_id=raw["fields"].get("epic", {}).get("key"),  # ← Link to epic
                    author=Author(name=raw["fields"]["creator"]["displayName"]),
                    created_at=datetime.fromisoformat(raw["fields"]["created"]),
                    url=f"https://mycompany.atlassian.net/browse/{raw['key']}"
                )
                features.append(feature)
                
            elif issue_type == "story":
                story = UserStory(
                    id=raw["key"],
                    key=raw["key"],
                    title=raw["fields"]["summary"],
                    description=raw["fields"]["description"],
                    status=self._normalize_status(raw["fields"]["status"]),
                    priority=self._normalize_priority(raw["fields"]["priority"]),
                    story_points=raw["fields"].get("customfield_10016"),  # ← Story points
                    epic_id=raw["fields"].get("epic", {}).get("key"),
                    sprint=raw["fields"].get("customfield_10020", {}).get("name"),  # ← Sprint
                    author=Author(name=raw["fields"]["creator"]["displayName"]),
                    created_at=datetime.fromisoformat(raw["fields"]["created"]),
                    url=f"https://mycompany.atlassian.net/browse/{raw['key']}"
                )
                user_stories.append(story)
        
        # Create FunctionalData structure
        functional_data = FunctionalData(
            epics=epics,
            features=features,
            user_stories=user_stories,
            requirements=[],
            source_type=SourceType.JIRA,
            project_name=config.config["project"],
            project_key=config.config["project"]
        )
        
        # Return with new structure
        return ProjectData(
            functional_data=functional_data,  # ← Standardized!
            technical_data=None,              # Not applicable for Jira
            repository=Repository(name=config.config["project"], full_name=config.config["project"]),
            source_type=SourceType.JIRA
        )
```

### Key Changes

1. ✅ **Inherit from `TicketingConnector`** instead of `ConnectorBase`
2. ✅ **Separate issues by type** (Epic, Feature, UserStory)
3. ✅ **Use specific models** with richer fields
4. ✅ **Populate `functional_data`** in ProjectData
5. ✅ **Link related items** (epic_id, feature_id, sprint)

## 🔧 Migrating a Git Connector

### Before (Old Code)

```python
from wara9a.core.connector_base import ConnectorBase
from wara9a.core.models import ProjectData, Commit, PullRequest, Author

class OldGitHubConnector(ConnectorBase):
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Fetch commits
        raw_commits = self._fetch_github_commits(config)
        
        commits = []
        for raw in raw_commits:
            commit = Commit(
                sha=raw["sha"],
                message=raw["commit"]["message"],
                author=Author(
                    name=raw["commit"]["author"]["name"],
                    email=raw["commit"]["author"]["email"]
                ),
                date=datetime.fromisoformat(raw["commit"]["author"]["date"]),
                files_changed=[f["filename"] for f in raw["files"]],  # Just file names
                additions=raw["stats"]["additions"],
                deletions=raw["stats"]["deletions"]
            )
            commits.append(commit)
        
        return ProjectData(
            repository=self._get_repo_info(config),
            commits=commits,  # Simple commit list
            issues=[],
            pull_requests=[],
            source_type=SourceType.GITHUB
        )
```

### After (New Code)

```python
from wara9a.core.connector_base import GitConnector  # ← Specific base class
from wara9a.core.models import (
    ProjectData, TechnicalData,       # ← New structure
    TechnicalCommit, TechnicalPullRequest,  # ← Specific models
    CodeChange, CodeMetrics, Author
)
import re

class NewGitHubConnector(GitConnector):  # ← Inherit from GitConnector
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # Fetch commits with detailed info
        raw_commits = self._fetch_github_commits(config)
        
        technical_commits = []
        for raw in raw_commits:
            # Parse commit message for links
            message = raw["commit"]["message"]
            subject = message.split('\n')[0]
            body = '\n'.join(message.split('\n')[1:]).strip() if '\n' in message else None
            
            # Extract linked issues (#123) and PRs
            linked_issues = re.findall(r'#(\d+)', message)
            
            # Detailed file changes
            files_changed = []
            for f in raw["files"]:
                change = CodeChange(
                    file_path=f["filename"],
                    change_type=f["status"],  # added, modified, deleted
                    additions=f["additions"],
                    deletions=f["deletions"],
                    changes=f["changes"],
                    language=self._detect_language(f["filename"])  # ← Language detection
                )
                files_changed.append(change)
            
            commit = TechnicalCommit(
                sha=raw["sha"],
                short_sha=raw["sha"][:7],
                message=message,
                message_subject=subject,
                message_body=body,
                author=Author(
                    name=raw["commit"]["author"]["name"],
                    email=raw["commit"]["author"]["email"]
                ),
                date=datetime.fromisoformat(raw["commit"]["author"]["date"]),
                files_changed=files_changed,  # ← Rich file change data
                total_additions=raw["stats"]["additions"],
                total_deletions=raw["stats"]["deletions"],
                linked_issues=linked_issues,  # ← Links to functional items
                url=raw["html_url"]
            )
            technical_commits.append(commit)
        
        # Fetch PRs with review data
        raw_prs = self._fetch_github_prs(config)
        technical_prs = [self._normalize_pr(pr) for pr in raw_prs]
        
        # Calculate code metrics
        metrics = self._calculate_metrics(config)
        
        # Create TechnicalData structure
        technical_data = TechnicalData(
            commits=technical_commits,
            pull_requests=technical_prs,
            code_metrics=metrics,  # ← Code statistics
            technical_debt=[],
            repository_name=config.config["repo"],
            source_type=SourceType.GITHUB
        )
        
        # Return with new structure
        return ProjectData(
            functional_data=None,              # Not applicable for Git
            technical_data=technical_data,     # ← Standardized!
            repository=self._get_repo_info(config),
            source_type=SourceType.GITHUB
        )
```

### Key Changes

1. ✅ **Inherit from `GitConnector`** instead of `ConnectorBase`
2. ✅ **Use `TechnicalCommit`** with detailed file changes
3. ✅ **Parse commit messages** for links to issues/PRs
4. ✅ **Add code metrics** (languages, LOC, etc.)
5. ✅ **Populate `technical_data`** in ProjectData
6. ✅ **Link to functional items** via commit messages

## 📝 Migrating Templates

### Before (Old Template)

```jinja2
{# Old template using mixed issues #}
<h1>Release Notes</h1>

<h2>Completed Issues</h2>
<ul>
{% for issue in data.issues %}
  {% if issue.status == 'CLOSED' %}
    <li>{{ issue.title }} ({{ issue.type }})</li>
  {% endif %}
{% endfor %}
</ul>

<h2>Recent Commits</h2>
<ul>
{% for commit in data.commits %}
  <li>{{ commit.sha[:7] }}: {{ commit.message }}</li>
{% endfor %}
</ul>
```

### After (New Template)

```jinja2
{# New template using standardized models #}
<h1>Release Notes</h1>

{% if data.has_functional_data() %}
  <h2>Features Delivered</h2>
  
  {% for epic in data.functional_data.epics %}
    {% if epic.status == 'CLOSED' %}
      <div class="epic">
        <h3>{{ epic.key }}: {{ epic.title }}</h3>
        <p><strong>Business Value:</strong> {{ epic.business_value }}</p>
        
        {# Get features for this epic #}
        {% set epic_features = data.functional_data.get_features_by_epic(epic.id) %}
        {% if epic_features %}
          <h4>Features</h4>
          <ul>
          {% for feature in epic_features %}
            <li>{{ feature.key }}: {{ feature.title }}</li>
          {% endfor %}
          </ul>
        {% endif %}
        
        {# Get user stories #}
        {% set epic_stories = data.functional_data.get_stories_by_epic(epic.id) %}
        {% if epic_stories %}
          <h4>User Stories ({{ epic_stories|length }})</h4>
          <ul>
          {% for story in epic_stories %}
            <li>{{ story.key }}: {{ story.title }} ({{ story.story_points }} pts)</li>
          {% endfor %}
          </ul>
        {% endif %}
      </div>
    {% endif %}
  {% endfor %}
{% endif %}

{% if data.has_technical_data() %}
  <h2>Technical Implementation</h2>
  
  <p><strong>Commits:</strong> {{ data.technical_data.commits|length }}</p>
  <p><strong>Changes:</strong> +{{ data.technical_data.get_total_additions() }} 
                              -{{ data.technical_data.get_total_deletions() }} lines</p>
  
  <h3>Recent Commits</h3>
  <ul>
  {% for commit in data.technical_data.commits[:20] %}
    <li>
      <code>{{ commit.short_sha }}</code> {{ commit.message_subject }}
      <br><small>{{ commit.author.name }} - {{ commit.date.strftime('%Y-%m-%d') }}</small>
      {% if commit.linked_issues %}
        <br><em>Implements: {{ commit.linked_issues|join(', ') }}</em>
      {% endif %}
    </li>
  {% endfor %}
  </ul>
  
  <h3>Pull Requests</h3>
  {% for pr in data.technical_data.get_merged_prs() %}
    <div class="pr">
      <h4>#{{ pr.number }}: {{ pr.title }}</h4>
      <p>{{ pr.files_changed }} files, +{{ pr.additions }} -{{ pr.deletions }}</p>
      <p>Reviewed by: {{ pr.approved_by|map(attribute='name')|join(', ') }}</p>
    </div>
  {% endfor %}
{% endif %}
```

## 🔄 Using Migration Helpers (Temporary)

If you need to migrate gradually, use the migration utilities:

```python
from wara9a.core.migration import (
    migrate_issues_to_functional_data,
    migrate_commits_to_technical_data
)

# Convert legacy data
functional_data = migrate_issues_to_functional_data(
    issues=legacy_issues,
    project_name="MyProject"
)

technical_data = migrate_commits_to_technical_data(
    commits=legacy_commits,
    pull_requests=legacy_prs,
    repository_name="my-repo"
)

# Use in ProjectData
return ProjectData(
    functional_data=functional_data,
    technical_data=technical_data,
    repository=repo,
    source_type=SourceType.CUSTOM
)
```

⚠️ **Note**: Migration helpers are temporary and will be removed in v2.0. Migrate to direct model usage.

## ✅ Migration Checklist

### For Connector Developers

- [ ] Change base class to `TicketingConnector` or `GitConnector`
- [ ] Use specific models (`Epic`, `Feature`, `UserStory`, `TechnicalCommit`, `TechnicalPullRequest`)
- [ ] Populate `functional_data` or `technical_data` in ProjectData
- [ ] Add rich fields (business_value, story_points, reviewers, etc.)
- [ ] Link related items (epic_id, feature_id, linked_issues)
- [ ] Remove usage of legacy `issues`, `commits`, `pull_requests` fields
- [ ] Update tests to use new models
- [ ] Update documentation

### For Template Developers

- [ ] Check `data.has_functional_data()` and `data.has_technical_data()`
- [ ] Access `data.functional_data.epics/features/user_stories`
- [ ] Access `data.technical_data.commits/pull_requests`
- [ ] Use new helper methods (`get_features_by_epic()`, `get_merged_prs()`, etc.)
- [ ] Update variable names for clarity
- [ ] Test with both connector types

## 📚 See Also

- [Standard Output Formats](standard-outputs.md)
- [Dual-Source Architecture](dual-source-architecture.md)
- [Connector Development Guide](connector-dev.md)

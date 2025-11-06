# Standard Output Formats

Wara9a defines **standard output formats** for each documentation type to ensure consistency across all connectors.

## 📋 Functional Documentation Standard

All **ticketing connectors** (Jira, Azure DevOps, Linear, etc.) must return data in this standardized format:

### Data Structure

```python
ProjectData(
    functional_data=FunctionalData(
        epics=[Epic(...)],           # Business epics
        features=[Feature(...)],     # Product features
        user_stories=[UserStory(...)],  # User stories
        requirements=[Requirement(...)]  # Formal requirements
    )
)
```

### Standard Fields

#### Epic
```python
Epic(
    id="unique-id",
    key="PROJ-123",                  # Epic key
    title="Customer Portal",
    description="Build customer self-service portal",
    status=IssueStatus.IN_PROGRESS,
    priority=Priority.HIGH,
    author=Author(name="Product Owner"),
    created_at=datetime(...),
    business_value="Reduce support tickets by 30%",
    acceptance_criteria=[...]
)
```

#### Feature
```python
Feature(
    id="unique-id",
    key="PROJ-456",
    title="User Authentication",
    description="Implement OAuth2 authentication",
    status=IssueStatus.OPEN,
    priority=Priority.HIGH,
    epic_id="epic-id",               # Link to parent epic
    epic_key="PROJ-123",
    author=Author(name="Product Manager"),
    acceptance_criteria=[...]
)
```

#### UserStory
```python
UserStory(
    id="unique-id",
    key="PROJ-789",
    title="Login with Google",
    user_persona="Customer",         # As a...
    user_goal="login with my Google account",  # I want...
    user_benefit="avoid creating another password",  # So that...
    status=IssueStatus.CLOSED,
    priority=Priority.MEDIUM,
    story_points=5,
    epic_id="epic-id",
    feature_id="feature-id",
    sprint="Sprint 23",
    acceptance_criteria=[
        "User can click 'Sign in with Google'",
        "OAuth flow completes successfully",
        "User profile is created/updated"
    ]
)
```

### Template Usage

```jinja2
{# Accessing functional data in templates #}

{% if data.has_functional_data() %}
  <h1>Product Requirements</h1>
  
  {% for epic in data.functional_data.epics %}
    <h2>{{ epic.key }}: {{ epic.title }}</h2>
    <p><strong>Business Value:</strong> {{ epic.business_value }}</p>
    <p><strong>Status:</strong> {{ epic.status }}</p>
    
    {# Get features for this epic #}
    {% set epic_features = data.functional_data.get_features_by_epic(epic.id) %}
    {% if epic_features %}
      <h3>Features</h3>
      <ul>
      {% for feature in epic_features %}
        <li>{{ feature.key }}: {{ feature.title }}</li>
      {% endfor %}
      </ul>
    {% endif %}
    
    {# Get user stories for this epic #}
    {% set epic_stories = data.functional_data.get_stories_by_epic(epic.id) %}
    {% if epic_stories %}
      <h3>User Stories</h3>
      <ul>
      {% for story in epic_stories %}
        <li>{{ story.key }}: {{ story.title }} ({{ story.story_points }} points)</li>
      {% endfor %}
      </ul>
    {% endif %}
  {% endfor %}
{% endif %}
```

---

## 🔧 Technical Documentation Standard

All **Git connectors** (GitHub, GitLab, Bitbucket, etc.) must return data in this standardized format:

### Data Structure

```python
ProjectData(
    technical_data=TechnicalData(
        commits=[TechnicalCommit(...)],     # Code commits
        pull_requests=[TechnicalPullRequest(...)],  # PRs/MRs
        code_metrics={                       # Metrics by language
            "python": CodeMetrics(...),
            "typescript": CodeMetrics(...)
        },
        technical_debt=[TechnicalDebt(...)]  # Debt items
    )
)
```

### Standard Fields

#### TechnicalCommit
```python
TechnicalCommit(
    sha="abc123...",
    short_sha="abc123",
    message="feat: Add user authentication",
    message_subject="feat: Add user authentication",
    message_body="Implements OAuth2 flow...",
    author=Author(name="John Doe", email="john@example.com"),
    date=datetime(...),
    
    # Detailed code changes
    files_changed=[
        CodeChange(
            file_path="src/auth/oauth.py",
            change_type="added",
            additions=150,
            deletions=0,
            language="python"
        )
    ],
    total_additions=150,
    total_deletions=0,
    
    # Links to functional items
    linked_issues=["PROJ-789"],      # References user story
    linked_prs=["#42"]
)
```

#### TechnicalPullRequest
```python
TechnicalPullRequest(
    id="pr-123",
    number=42,
    title="feat: Add user authentication",
    description="Implements OAuth2...",
    author=Author(name="John Doe"),
    status="merged",
    
    source_branch="feature/oauth",
    target_branch="main",
    
    created_at=datetime(...),
    merged_at=datetime(...),
    
    # Code review
    reviewers=[Author(name="Jane Smith")],
    approved_by=[Author(name="Jane Smith")],
    review_comments_count=5,
    
    # Changes
    commits=[...],                   # TechnicalCommit objects
    files_changed=10,
    additions=500,
    deletions=50,
    
    linked_issues=["PROJ-789"]       # Links to user story
)
```

#### CodeMetrics
```python
CodeMetrics(
    language="python",
    files_count=125,
    lines_of_code=15420,
    lines_blank=2100,
    lines_comment=3200,
    complexity=2.8
)
```

#### TechnicalDebt
```python
TechnicalDebt(
    id="debt-1",
    title="Refactor authentication module",
    description="Current implementation has high complexity",
    severity="medium",
    type="code_smell",
    file_path="src/auth/oauth.py",
    line_number=42,
    estimated_effort="4 hours"
)
```

### Template Usage

```jinja2
{# Accessing technical data in templates #}

{% if data.has_technical_data() %}
  <h1>Technical Changes</h1>
  
  <h2>Recent Commits</h2>
  {% for commit in data.technical_data.commits[:20] %}
    <div class="commit">
      <code>{{ commit.short_sha }}</code>
      <strong>{{ commit.message_subject }}</strong>
      <p>{{ commit.author.name }} - {{ commit.date.strftime('%Y-%m-%d') }}</p>
      <p>+{{ commit.total_additions }} -{{ commit.total_deletions }}</p>
      
      {% if commit.linked_issues %}
        <p>Implements: {{ commit.linked_issues|join(', ') }}</p>
      {% endif %}
    </div>
  {% endfor %}
  
  <h2>Pull Requests</h2>
  {% for pr in data.technical_data.get_merged_prs() %}
    <div class="pr">
      <h3>#{{ pr.number }}: {{ pr.title }}</h3>
      <p>{{ pr.author.name }} - Merged {{ pr.merged_at.strftime('%Y-%m-%d') }}</p>
      <p>{{ pr.files_changed }} files, +{{ pr.additions }} -{{ pr.deletions }}</p>
      <p>Reviewed by: {{ pr.approved_by|map(attribute='name')|join(', ') }}</p>
    </div>
  {% endfor %}
  
  <h2>Code Statistics</h2>
  <table>
    <tr><th>Language</th><th>Files</th><th>Lines of Code</th></tr>
    {% for lang, metrics in data.technical_data.code_metrics.items() %}
    <tr>
      <td>{{ lang }}</td>
      <td>{{ metrics.files_count }}</td>
      <td>{{ metrics.lines_of_code }}</td>
    </tr>
    {% endfor %}
  </table>
{% endif %}
```

---

## 🔗 Combined Documentation (Traceability)

Templates can access **both** functional and technical data to create complete documentation:

```jinja2
<h1>Release Notes - v{{ version }}</h1>

<h2>Features Delivered</h2>
{% if data.has_functional_data() %}
  {% for story in data.functional_data.user_stories %}
    {% if story.status == 'CLOSED' %}
      <div class="feature">
        <h3>{{ story.key }}: {{ story.title }}</h3>
        <p>{{ story.description }}</p>
        
        {# Link to technical implementation #}
        {% if data.has_technical_data() %}
          {% set related_commits = [] %}
          {% for commit in data.technical_data.commits %}
            {% if story.key in commit.linked_issues %}
              {% set _ = related_commits.append(commit) %}
            {% endif %}
          {% endfor %}
          
          {% if related_commits %}
            <h4>Technical Implementation</h4>
            <ul>
            {% for commit in related_commits %}
              <li><code>{{ commit.short_sha }}</code> {{ commit.message_subject }}</li>
            {% endfor %}
            </ul>
          {% endif %}
        {% endif %}
      </div>
    {% endif %}
  {% endfor %}
{% endif %}

<h2>Technical Changes</h2>
{% if data.has_technical_data() %}
  <p>Total commits: {{ data.technical_data.commits|length }}</p>
  <p>Total additions: {{ data.technical_data.get_total_additions() }}</p>
  <p>Total deletions: {{ data.technical_data.get_total_deletions() }}</p>
{% endif %}
```

---

## 🛠️ Connector Implementation Guide

### Implementing a Ticketing Connector

```python
from wara9a.core.connector_base import TicketingConnector
from wara9a.core.models import (
    ProjectData, FunctionalData, Epic, Feature, UserStory,
    IssueStatus, Priority, Author
)

class MyTicketingConnector(TicketingConnector):
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # 1. Fetch raw data from API
        raw_epics = self._fetch_epics(config)
        raw_features = self._fetch_features(config)
        raw_stories = self._fetch_stories(config)
        
        # 2. Normalize to standard format
        epics = [self._normalize_epic(e) for e in raw_epics]
        features = [self._normalize_feature(f) for f in raw_features]
        stories = [self._normalize_story(s) for s in raw_stories]
        
        # 3. Create FunctionalData
        functional_data = FunctionalData(
            epics=epics,
            features=features,
            user_stories=stories,
            requirements=[],
            source_type=SourceType.JIRA,
            project_name=config.config["project"],
            project_key=config.config["project"]
        )
        
        # 4. Return ProjectData with functional_data populated
        return ProjectData(
            functional_data=functional_data,  # Standard output!
            technical_data=None,              # Not applicable for ticketing
            repository=self._create_repo_placeholder(config),
            source_type=SourceType.JIRA
        )
    
    def _normalize_epic(self, raw: dict) -> Epic:
        """Convert raw API response to standard Epic format."""
        return Epic(
            id=raw["id"],
            key=raw["key"],
            title=raw["fields"]["summary"],
            description=raw["fields"]["description"],
            status=self._normalize_status(raw["fields"]["status"]),
            priority=self._normalize_priority(raw["fields"]["priority"]),
            author=Author(name=raw["fields"]["creator"]["displayName"]),
            created_at=datetime.fromisoformat(raw["fields"]["created"])
        )
```

### Implementing a Git Connector

```python
from wara9a.core.connector_base import GitConnector
from wara9a.core.models import (
    ProjectData, TechnicalData, TechnicalCommit, TechnicalPullRequest,
    CodeChange, CodeMetrics, Author
)

class MyGitConnector(GitConnector):
    
    def collect(self, config: SourceConfig) -> ProjectData:
        # 1. Fetch raw data from API
        raw_commits = self._fetch_commits(config)
        raw_prs = self._fetch_pull_requests(config)
        
        # 2. Normalize to standard format
        commits = [self._normalize_commit(c) for c in raw_commits]
        prs = [self._normalize_pr(pr) for pr in raw_prs]
        
        # 3. Calculate metrics
        metrics = self._calculate_code_metrics(config)
        
        # 4. Create TechnicalData
        technical_data = TechnicalData(
            commits=commits,
            pull_requests=prs,
            code_metrics=metrics,
            technical_debt=[],
            repository_name=config.config["repo"],
            source_type=SourceType.GITHUB
        )
        
        # 5. Return ProjectData with technical_data populated
        return ProjectData(
            functional_data=None,              # Not applicable for Git
            technical_data=technical_data,     # Standard output!
            repository=self._get_repo_info(config),
            source_type=SourceType.GITHUB
        )
    
    def _normalize_commit(self, raw: dict) -> TechnicalCommit:
        """Convert raw API response to standard TechnicalCommit format."""
        return TechnicalCommit(
            sha=raw["sha"],
            short_sha=raw["sha"][:7],
            message=raw["commit"]["message"],
            message_subject=raw["commit"]["message"].split('\n')[0],
            author=Author(
                name=raw["commit"]["author"]["name"],
                email=raw["commit"]["author"]["email"]
            ),
            date=datetime.fromisoformat(raw["commit"]["author"]["date"]),
            files_changed=[
                CodeChange(
                    file_path=f["filename"],
                    change_type=f["status"],
                    additions=f["additions"],
                    deletions=f["deletions"]
                )
                for f in raw["files"]
            ],
            total_additions=raw["stats"]["additions"],
            total_deletions=raw["stats"]["deletions"]
        )
```

---

## ✅ Benefits of Standard Outputs

1. **Consistency**: All connectors of the same type return identical structures
2. **Interoperability**: Templates work with any connector of that type
3. **Type Safety**: Pydantic models ensure data validation
4. **Documentation**: Clear contract for connector developers
5. **Template Reusability**: Write once, use with multiple connectors
6. **Traceability**: Easy to link functional items to technical implementation

---

## 📚 See Also

- [Dual-Source Architecture](dual-source-architecture.md)
- [Connector Development Guide](connector-dev.md)
- [Template Development Guide](template-dev.md)

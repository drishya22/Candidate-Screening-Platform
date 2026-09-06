import re

from github import Github
from github.GithubException import GithubException

from app.core.config import settings


def parse_github_profile(url: str) -> str:
    match = re.search(
        r"github\.com/([^/]+)/?$",
        url.strip(),
    )

    if not match:
        raise ValueError(f"Invalid GitHub profile URL: {url}")

    return match.group(1)


def analyze_github_profile(url: str) -> dict:
    username = parse_github_profile(url)

    github = Github(settings.github_token)

    try:
        user = github.get_user(username)
        repositories = list(user.get_repos(type="owner", sort="updated"))

        repo_results = []

        # Analyze a small number of repositories to control
        # latency and API usage.
        for repo in repositories[:5]:
            languages = dict(repo.get_languages())

            readme = ""
            try:
                readme_file = repo.get_readme()
                readme = readme_file.decoded_content.decode(
                    "utf-8",
                    errors="ignore",
                )
            except GithubException:
                pass

            repo_results.append(
                {
                    "name": repo.full_name,
                    "description": repo.description or "",
                    "url": repo.html_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "languages": languages,
                    "commit_count": repo.get_commits().totalCount,
                    "readme": readme[:4000],
                }
            )

        return {
            "username": user.login,
            "public_repositories": user.public_repos,
            "repositories_analyzed": len(repo_results),
            "repositories": repo_results,
        }

    except GithubException as exc:
        raise ValueError(
            f"GitHub API error for {username}: {exc}"
        )

def calculate_github_score(profile_data: dict) -> dict:
    repositories = profile_data.get("repositories", [])

    if not repositories:
        return {
            "score": 0.0,
            "repository_relevance": 0.0,
            "engineering_signals": 0.0,
            "activity": 0.0,
            "documentation": 0.0,
            "evidence": ["No public repositories available for analysis."],
        }

    analyzed = len(repositories)

    # 1. Activity: normalize average commits across analyzed repos.
    avg_commits = sum(
        repo.get("commit_count", 0)
        for repo in repositories
    ) / analyzed

    activity = min(avg_commits / 20 * 100, 100)

    # 2. Engineering signals:
    # Prefer code-heavy repositories over empty/basic repositories.
    code_repos = 0

    for repo in repositories:
        languages = repo.get("languages", {})

        if languages:
            code_repos += 1

    engineering_signals = (code_repos / analyzed) * 100

    # 3. Documentation based on README presence.
    documented = sum(
        1
        for repo in repositories
        if repo.get("readme", "").strip()
    )

    documentation = (documented / analyzed) * 100

    # 4. Repository relevance:
    # We initially use repository metadata as a proxy.
    # JD-aware semantic scoring can be added later.
    relevant_keywords = {
        "ai",
        "ml",
        "machine",
        "deep",
        "learning",
        "llm",
        "nlp",
        "computer",
        "vision",
        "python",
        "model",
    }

    relevant_repos = 0

    for repo in repositories:
        text = (
            f"{repo.get('name', '')} "
            f"{repo.get('description', '')} "
            f"{repo.get('readme', '')}"
        ).lower()

        if any(keyword in text for keyword in relevant_keywords):
            relevant_repos += 1

    repository_relevance = (
        relevant_repos / analyzed
    ) * 100

    final_score = (
        repository_relevance * 0.40
        + engineering_signals * 0.25
        + activity * 0.20
        + documentation * 0.15
    )

    evidence = [
        f"Analyzed {analyzed} repositories.",
        f"{relevant_repos} repositories showed AI/ML/software engineering relevance.",
        f"{code_repos} repositories contained detectable source code.",
        f"{documented} repositories contained README documentation.",
        f"Average commits across analyzed repositories: {avg_commits:.1f}.",
    ]

    return {
        "score": round(final_score, 2),
        "repository_relevance": round(repository_relevance, 2),
        "engineering_signals": round(engineering_signals, 2),
        "activity": round(activity, 2),
        "documentation": round(documentation, 2),
        "evidence": evidence,
    }        
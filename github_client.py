import os
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("GH_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def _get(self, path: str, params: Dict = None) -> Optional[dict]:
        url = f"{GITHUB_API}{path}"
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=10)
            if r.status_code == 401:
                logger.error("GitHub API: невірний токен (401)")
                return None
            if r.status_code == 403:
                logger.error("GitHub API: доступ заборонено (403) — перевір права токена")
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"GitHub API error: {e}")
            return None

    def get_user(self) -> Optional[Dict]:
        return self._get("/user")

    def list_repos(self) -> List[Dict]:
        data = self._get("/user/repos", params={"sort": "pushed", "per_page": 20})
        if not data:
            return []
        return [{"name": r["name"], "private": r["private"], "language": r.get("language"), "pushed_at": r["pushed_at"]} for r in data]

    def list_branches(self, owner: str, repo: str) -> List[str]:
        data = self._get(f"/repos/{owner}/{repo}/branches")
        if not data:
            return []
        return [b["name"] for b in data]

    def list_commits(self, owner: str, repo: str, branch: str = "main", limit: int = 5) -> List[Dict]:
        data = self._get(f"/repos/{owner}/{repo}/commits", params={"sha": branch, "per_page": limit})
        if not data:
            return []
        return [{"sha": c["sha"][:7], "message": c["commit"]["message"].split("\n")[0], "author": c["commit"]["author"]["name"], "date": c["commit"]["author"]["date"][:10]} for c in data]

    def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        data = self._get(f"/repos/{owner}/{repo}/pulls", params={"state": state, "per_page": 10})
        if not data:
            return []
        return [{"number": p["number"], "title": p["title"], "author": p["user"]["login"], "branch": p["head"]["ref"]} for p in data]

    def list_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        data = self._get(f"/repos/{owner}/{repo}/issues", params={"state": state, "per_page": 10})
        if not data:
            return []
        return [{"number": i["number"], "title": i["title"], "author": i["user"]["login"]} for i in data if "pull_request" not in i]

    def get_repo_summary(self, owner: str, repo: str) -> str:
        branches = self.list_branches(owner, repo)
        commits = self.list_commits(owner, repo, limit=3)
        prs = self.list_pull_requests(owner, repo)
        issues = self.list_issues(owner, repo)

        lines = [
            f"Репо: {owner}/{repo}",
            f"Гілки ({len(branches)}): {', '.join(branches)}",
            f"\nОстанні коміти:",
        ]
        for c in commits:
            lines.append(f"  [{c['sha']}] {c['message']} — {c['author']} ({c['date']})")
        lines.append(f"\nВідкриті PR: {len(prs)}")
        for p in prs:
            lines.append(f"  #{p['number']} {p['title']} (@{p['author']})")
        lines.append(f"\nВідкриті Issues: {len(issues)}")
        for i in issues:
            lines.append(f"  #{i['number']} {i['title']} (@{i['author']})")

        return "\n".join(lines)

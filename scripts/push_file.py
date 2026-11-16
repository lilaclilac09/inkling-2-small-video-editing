"""Push one local file into a GitHub repo via the contents API.

The PAT lives in the registered connection custom.github-pat, never in a
file. Creates the file on the repo default branch (one commit). If the
file already exists, pass its current blob sha to update it instead.

Usage:
  python3 push_file.py <owner>/<repo> <local_path> <repo_path> <message> [sha]
"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://api.github.com"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def main():
    repo, local_path, repo_path, message = sys.argv[1:5]
    sha = sys.argv[5] if len(sys.argv) > 5 else None
    with open(os.path.expanduser(local_path), "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    body = {"message": message, "content": content}
    if sha:
        body["sha"] = sha
    data = json.dumps(body).encode("utf-8")
    url = f"{BASE}/repos/{repo}/contents/{repo_path}"
    request = urllib.request.Request(url, data=data, method="PUT")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "muse-sandbox")
    request.add_header("Content-Type", "application/json")
    add_surrogate_to_request(
        request, "custom.github-pat",
        allowed_hosts=["api.github.com", "github.com"],
    )
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
        out = read_json_response(response)
        print(f"HTTP {response.status} {repo}/{repo_path} sha={out.get('content', {}).get('sha', '')[:7]}")
        print(out.get("content", {}).get("html_url", ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

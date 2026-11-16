"""Push local files into lilaclilac09/ripple via the GitHub contents API.

Each file becomes one commit. The PAT lives in the registered connection
custom.github-pat, never in a file. Run from the repo root of the push list.

Usage:
  python3 push_to_ripple.py
"""
import base64
import json
import os
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://api.github.com"
OWNER = "lilaclilac09"
REPO = "ripple"

FILES = [
    ("~/workspace/inkling-recap/README.md", "README.md"),
    ("~/workspace/your_files/inkling-video-pipeline.py", "inkling-video-pipeline.py"),
    ("~/workspace/your_files/inkling-video-combine.py", "inkling-video-combine.py"),
    ("~/workspace/your_files/inkling-video-cut.py", "inkling-video-cut.py"),
    ("~/workspace/your_files/inkling-video-recap.py", "inkling-video-recap.py"),
    ("~/workspace/your_files/inkling-video-sft.py", "inkling-video-sft.py"),
    ("~/workspace/your_files/inkling-video-editor-mcp.py", "inkling-video-editor-mcp.py"),
    ("~/workspace/your_files/inkling-demo-master-prompt.txt", "inkling-demo-master-prompt.txt"),
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def put_file(local_path, repo_path):
    local_path = os.path.expanduser(local_path)
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("ascii")
    body = json.dumps({
        "message": f"Add {repo_path}",
        "content": content,
    }).encode("utf-8")
    url = f"{BASE}/repos/{OWNER}/{REPO}/contents/{repo_path}"
    request = urllib.request.Request(url, data=body, method="PUT")
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    request.add_header("User-Agent", "muse-sandbox")
    request.add_header("Content-Type", "application/json")
    add_surrogate_to_request(
        request, "custom.github-pat",
        allowed_hosts=["api.github.com", "github.com"],
    )
    with urllib.request.build_opener(NoRedirect()).open(request, timeout=60) as response:
        data = read_json_response(response)
        print(f"{repo_path}: HTTP {response.status} sha={data.get('content', {}).get('sha', '')[:7]}")
        return response.status


def main():
    ok = 0
    for local_path, repo_path in FILES:
        if not os.path.exists(os.path.expanduser(local_path)):
            print(f"{repo_path}: SKIP (missing locally: {local_path})")
            continue
        try:
            status = put_file(local_path, repo_path)
            if status in (200, 201):
                ok += 1
        except Exception as e:
            print(f"{repo_path}: FAILED {e}")
    print(f"Done: {ok}/{len(FILES)} files pushed")
    return 0 if ok == len(FILES) else 1


if __name__ == "__main__":
    sys.exit(main())

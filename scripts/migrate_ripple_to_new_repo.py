"""Copy all files from lilaclilac09/ripple to lilaclilac09/inkling-2-small-video-editing.

Uses the stored fine-grained PAT (custom.github-pat) via the dynamic
credentials surrogate, same as github_pat.py. Reads each file's base64
content from ripple and PUTs it to the new repo.
"""
import base64
import json
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE = "https://api.github.com"
SRC = "lilaclilac09/ripple"
DST = "lilaclilac09/inkling-2-small-video-editing"

FILES = [
    "README.md",
    "how-inkling-2-small-cut-this-video.md",
    "inkling-demo-master-prompt.txt",
    "inkling-video-combine.py",
    "inkling-video-cut.py",
    "inkling-video-editor-mcp.py",
    "inkling-video-pipeline.py",
    "inkling-video-recap.py",
    "inkling-video-sft.py",
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def call(method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "muse-sandbox")
    if data:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(
        req, "custom.github-pat",
        allowed_hosts=["api.github.com", "github.com"],
    )
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
        return read_json_response(resp), resp.status


def main():
    for path in FILES:
        content, status = call("GET", f"/repos/{SRC}/contents/{path}")
        if status != 200:
            print(f"SKIP {path}: GET returned {status}")
            continue
        b64 = content["content"].replace("\n", "")
        body = {
            "message": f"Migrate {path} from ripple",
            "content": b64,
        }
        result, status = call("PUT", f"/repos/{DST}/contents/{path}", body)
        if status in (200, 201):
            print(f"OK {path} -> {result['content']['html_url']}")
        else:
            print(f"FAIL {path}: PUT returned {status}: {result}")


if __name__ == "__main__":
    main()

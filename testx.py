
from typing import Union, Optional
from urllib.parse import urlparse
import re
from dataclasses import dataclass


@dataclass
class GithubUrl:
    host: str
    path: str
    explicit_branch: Union[str, None]
    filepath: Optional[str]
    blob: Optional[str]
    owner: Optional[str]
    name: Optional[str]
    repository: Optional[str]


def is_checksum(s: str) -> bool:
    return bool(re.match(r"^[a-f0-9]{40}$", s, re.IGNORECASE))


def trim_slash(path: str):
    return path[1:] if path.startswith("/") else path


def owner(s: str):
    if not s:
        return None
    idx = s.find(":")
    return s[idx + 1 :] if idx > -1 else s


def name(s: str):
    return re.sub(r"^\W+|\.git$", "", s) if s else None


# None here means default branch (master/main)
def get_branch(s: str, fragment: Union[str, None]) -> Union[str, None]:
    segs = s.split("#")
    branch = segs[-1] if len(segs) > 1 else None

    if not branch and fragment is not None and fragment.startswith("#"):
        branch = fragment[1:]

    return branch


def parse_github_url(url: str) -> GithubUrl:
    if not isinstance(url, str) or len(url) == 0:
        raise Exception("Invalid url")

    if "git@gist" in url or "//gist" in url:
        raise Exception("Cannot parse gists")

    url_obj = urlparse(url)
    full_path = url_obj.path + "?" + url_obj.query if url_obj.query else url_obj.path
    hostname = url_obj.hostname
    if not hostname and re.match(r"^git@", url):
        hostname = urlparse("http://" + url).hostname
    if hostname is None:
        raise Exception("Invalid hostname")

    full_path = (
        full_path[6:]
        if "repos" in full_path and full_path.index("repos")
        else full_path
    )

    seg = [s for s in full_path.split("/") if s]
    branch = (
        seg[3]
        if len(seg) >= 3 and seg[2] == "blob" and not is_checksum(seg[3])
        else None
    )
    filepath = (
        "/".join(seg[4:])
        if len(seg) >= 3
        and seg[2] == "blob"
        and not is_checksum(seg[3])
        and len(seg) > 4
        else None
    )

    blob = url[url.index("blob") + 5 :] if "blob" in url else None

    tree_index = url.find("tree")
    if tree_index != -1:
        idx = tree_index + 5
        _branch = url[idx:]
        slash_index = _branch.find("/")
        if slash_index != -1:
            _branch = _branch[:slash_index]
        branch = _branch

    repo_owner = owner(seg[0])
    repo_name = name(seg[1])
    repo = None

    if len(seg) > 1 and repo_owner and repo_name:
        repo = f"{repo_owner}/{repo_name}"
    else:
        href = url.split(":")

        if len(href) == 2 and "//" not in url:
            repo = repo if repo is not None else href[-1]
            repo_segments = repo.split("/")
            repo_owner, repo_name = (
                repo_segments if len(repo_segments) == 2 else (None, None)
            )
        else:
            match = re.search(r"/([^/]*)$", url)
            repo_owner = match.group(1) if match else None
            repo = None

        if repo and (not repo_owner or not repo_name):
            segs = repo.split("/")
            repo_owner, repo_name = segs if len(segs) == 2 else (None, None)

    if not branch:
        branch = seg[2] if len(seg) > 2 else get_branch(full_path, url_obj.fragment)
        if len(seg) > 3:
            filepath = "/".join(seg[3:])

    return GithubUrl(
        host=hostname or "github.com",
        owner=repo_owner,
        name=repo_name,
        path=trim_slash(url_obj.path),
        explicit_branch=branch,
        filepath=filepath,
        blob=blob,
        repository=repo,
    )


if __name__ == "__main__":
    print(parse_github_url("https://github.com/iirvanard/nafan"))
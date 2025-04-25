#!/usr/bin/env python3

import os
import random
import time
from pathlib import Path

from git import Repo

FORTUNES_PATH = Path("fortune cookie/fortunes.cookie")
README_PATH = Path("README.md")


def pick_fortune() -> str:
    with FORTUNES_PATH.open(encoding="utf-8") as fh:
        lines = fh.readlines()
    
    return lines[random.randint(2, len(lines) - 1)].rstrip("\n")


def update_readme(fortune: str) -> None:
    with README_PATH.open(encoding="utf-8") as fh:
        lines = fh.readlines()

    for i, line in enumerate(lines):
        if line.startswith("> "):
            lines[i] = f"> 🥠 {fortune}\n"
        elif line.startswith("Last update:"):
            lines[i] = f"Last update: {time.ctime()}\n"

    with README_PATH.open("w", encoding="utf-8") as fh:
        fh.writelines(lines)


def get_remote_url() -> str | None:
    """Return a URL that contains credentials, or None."""
    env_url = os.getenv("REMOTE_URL")
    if env_url:
        return env_url

    token = os.getenv("GITHUB_TOKEN")
    repo_full = os.getenv("GITHUB_REPOSITORY")
    if token and repo_full:
        return f"https://x-access-token:{token}@github.com/{repo_full}.git"

    
    return None


def main() -> None:
    fortune = pick_fortune()
    print(f"Today’s fortune is: {fortune}")
    update_readme(fortune)

    repo = Repo(".")
    repo.git.add(update=True)
    
    if not repo.is_dirty(index=True, working_tree=False, untracked_files=False):
        print("Nothing changed – skipping commit and push.")
        return

    repo.index.commit("Update fortune cookie message")
    origin = repo.remote(name="origin")

    if (url := get_remote_url()) is not None:
        print(f"Setting origin URL to {url!r}")
        origin.set_url(url)
    else:
        print("Using existing origin URL")

    print("Pushing to origin…")
    origin.push("HEAD:main")


if __name__ == "__main__":
    main()

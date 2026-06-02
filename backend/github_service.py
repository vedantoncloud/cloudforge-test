import os
import subprocess


def clone_repo(repo_url):

    repo_name = repo_url.split("/")[-1]

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]

    clone_path = f"repos/{repo_name}"

    os.makedirs("repos", exist_ok=True)

    subprocess.run(
        [
            "git",
            "clone",
            repo_url,
            clone_path
        ]
    )

    return clone_path
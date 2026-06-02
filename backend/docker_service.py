import subprocess


def build_image(repo_path, image_name):

    result = subprocess.run(
        [
            "docker",
            "build",
            "-t",
            image_name,
            repo_path
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
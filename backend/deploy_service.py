import subprocess


def run_container(
    image_name,
    port
):

    result = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "-p",
            f"{port}:80",
            image_name
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
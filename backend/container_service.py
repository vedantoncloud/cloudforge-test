import subprocess


def list_containers():

    result = subprocess.run(
        [
            "docker",
            "ps",
            "-a"
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def stop_container(container_id):

    result = subprocess.run(
        [
            "docker",
            "stop",
            container_id
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }

def restart_container(container_id):

    result = subprocess.run(
        [
            "docker",
            "restart",
            container_id
        ],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
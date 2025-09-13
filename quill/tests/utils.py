import subprocess
import time
import socket
import pytest
from typing import Generator
from quill import PostgresDriverParams, MysqlDriverParams

def wait_for_port(host: str, port: int, timeout: float = 30.0):
    """Wait until a TCP port is open."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    raise TimeoutError(f"Port {host}:{port} not ready after {timeout} seconds")


def start_container(name: str, image: str, env: dict, ports: dict):
    """Start docker container with given parameters."""
    args = [
        "docker", "run", "--rm", "-d", "--name", name,
    ]
    for k, v in env.items():
        args += ["-e", f"{k}={v}"]
    for host_port, container_port in ports.items():
        args += ["-p", f"127.0.0.1:{host_port}:{container_port}"]
    args.append(image)

    try:
        subprocess.run(args, check=True, capture_output=True)
    except FileNotFoundError:
        pytest.skip("Docker is not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to start docker container: {e.stderr.decode()}")


def stop_container(name: str):
    subprocess.run(["docker", "stop", name], check=False)


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresDriverParams, None, None]:

    try:
        name = "pytest-postgres"
        image = "postgres:16"
        env = {"POSTGRES_PASSWORD": "secret"}
        ports = {25432: 5432}
        start_container(name, image, env, ports)
        wait_for_port("localhost", 25432)

        params = PostgresDriverParams(
            host="localhost",
            port=25432,
            user="postgres",
            password="secret",
            database="postgres"
        )

        yield params
    finally:
        stop_container(name)


@pytest.fixture(scope="session")
def mysql_container():
    try:
        name = "pytest-mysql"
        image = "mysql:8"
        env = {
            "MYSQL_ROOT_PASSWORD": "secret",
            "MYSQL_DATABASE": "testdb",
            "MYSQL_USER": "testuser",
            "MYSQL_PASSWORD": "testpass",
        }
        ports = {23306: 3306}

        start_container(name, image, env, ports)
        wait_for_port("localhost", 23306)
    
        yield MysqlDriverParams(
            host="localhost",
            port=23306,
            user="testuser",
            password="testpass",
            database="testdb"
        )
    finally:
        stop_container(name)



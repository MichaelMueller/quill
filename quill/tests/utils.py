import subprocess, time, socket, pytest, sys, os
from typing import Generator
# local
project_path = os.path.abspath( os.path.dirname( __file__) + "/../.." )
if not project_path in sys.path:
    sys.path.insert(0, project_path)
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
    yield from _postgres_container()
    
def _postgres_container() -> Generator[PostgresDriverParams, None, None]:
    try:
        name = "pytest-postgres"
        stop_container(name)
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
        stop_container(name)
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

async def sandbox():
    # for manual testing
    for params in _postgres_container():
        print(params)        
        import asyncpg
        pool:asyncpg.Pool = await asyncpg.create_pool(
            user=params.user,
            password=params.password,
            database=params.database,
            host=params.host,
            port=params.port,
            min_size=params.pool_min_size,
            max_size=params.pool_max_size,
        )

        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT 1;")
            data:list[dict] = [dict(row) for row in rows]
            print(list( data[0].values() ) [0])
        await pool.close()
                
if __name__ == "__main__":
    import asyncio
    asyncio.run(sandbox())
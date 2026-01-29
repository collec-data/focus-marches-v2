import os

from testcontainers.core.generic import DbContainer
from testcontainers.core.utils import raise_for_deprecated_parameter
from testcontainers.core.wait_strategies import ExecWaitStrategy

_UNSET = object()


class MariaDBContainer(DbContainer):
    def __init__(
        self,
        image: str = "mariadb:latest",
        port: int = 3306,
        username: str | None = None,
        root_password: str | None = None,
        password: str | None = None,
        dbname: str | None = None,
        driver: str | None = "mariadbconnector",
        **kwargs,
    ) -> None:
        raise_for_deprecated_parameter(kwargs, "user", "username")
        super().__init__(image=image, **kwargs)
        self.username: str = username or os.environ.get("MARIADB_USER", "test")
        self.password: str = password or os.environ.get("MARIADB_PASSWORD", "test")
        self.root_password = root_password or os.environ.get(
            "MARIADB_ROOT_PASSWORD", "test"
        )
        self.dbname: str = dbname or os.environ.get("MARIADB_DATABASE", "test")
        self.port = port
        self.driver = f"+{driver}" if driver else ""

        self.with_exposed_ports(self.port)

    def _configure(self) -> None:
        self.with_env("MARIADB_USER", self.username)
        self.with_env("MARIADB_PASSWORD", self.password)
        self.with_env("MARIADB_ROOT_PASSWORD", self.root_password)
        self.with_env("MARIADB_DATABASE", self.dbname)

    def get_connection_url(
        self, host: str | None = None, driver: str | object | None = _UNSET
    ) -> str:
        driver_str = (
            "" if driver is None else self.driver if driver is _UNSET else f"+{driver}"
        )
        return super()._create_connection_url(
            dialect=f"mariadb{driver_str}",
            username=self.username,
            password=self.password,
            dbname=self.dbname,
            host=host,
            port=self.port,
        )

    def _connect(self) -> None:
        escaped_single_password = self.password.replace("'", "'\"'\"'")
        strategy = ExecWaitStrategy(
            [
                "sh",
                "-c",
                f"mariadb -h 127.0.0.1 -u {self.username} -p{escaped_single_password} -D {self.dbname}",
            ]
        )
        strategy.wait_until_ready(self)

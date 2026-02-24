import subprocess
import gzip
import shutil
from pathlib import Path
from datetime import datetime
import getpass


class MariaDBBackupConfig:
    """
    Configuration container for MariaDB backup process.
    """

    def __init__(
        self,
        user: str,
        password: str,
        host: str = "localhost",
        backup_dir: str = "/home/sal/backups/mariadb"
    ):
        self.user = user
        self.password = password
        self.host = host
        self.backup_dir = Path(backup_dir)
        self.excluded_dbs = {
            "information_schema",
            "performance_schema",
            "mysql",
            "sys"
        }


class MariaDBBackupService:
    """
    Service responsible for dumping and compressing MariaDB databases.
    """

    def __init__(self, config: MariaDBBackupConfig):
        self.config = config
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.config.backup_dir.mkdir(parents=True, exist_ok=True)

    def _run_command(self, command: list) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def get_databases(self) -> list:
        """
        Retrieve list of databases excluding system schemas.
        """
        cmd = [
            "mysql",
            f"-u{self.config.user}",
            f"-p{self.config.password}",
            "-e",
            "SHOW DATABASES;"
        ]

        result = self._run_command(cmd)

        if result.returncode != 0:
            raise RuntimeError(f"Error listing databases: {result.stderr}")

        dbs = result.stdout.splitlines()[1:]  # Skip header
        return [
            db for db in dbs
            if db not in self.config.excluded_dbs
        ]

    def dump_database(self, database: str) -> Path:
        """
        Dump a single database to .sql file.
        """
        output_file = self.config.backup_dir / f"{database}_{self.timestamp}.sql"

        cmd = [
            "mysqldump",
            f"-u{self.config.user}",
            f"-p{self.config.password}",
            "--single-transaction",
            "--routines",
            "--triggers",
            database
        ]

        with open(output_file, "w") as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True
            )

        if result.returncode != 0:
            output_file.unlink(missing_ok=True)
            raise RuntimeError(f"Error dumping {database}: {result.stderr}")

        if output_file.stat().st_size == 0:
            output_file.unlink(missing_ok=True)
            raise RuntimeError(f"Dump file for {database} is empty.")

        return output_file

    def compress_file(self, file_path: Path) -> Path:
        """
        Compress .sql file to .gz and verify integrity.
        """
        compressed_path = Path(str(file_path) + ".gz")

        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Verify gzip integrity
        try:
            with gzip.open(compressed_path, "rb") as f:
                f.read(1024)
        except Exception as e:
            compressed_path.unlink(missing_ok=True)
            raise RuntimeError(f"Gzip integrity check failed: {e}")

        if compressed_path.stat().st_size == 0:
            compressed_path.unlink(missing_ok=True)
            raise RuntimeError("Compressed file is empty.")

        file_path.unlink()  # Remove original .sql

        return compressed_path

    def backup_all(self):
        databases = self.get_databases()

        if not databases:
            print("No databases to backup.")
            return

        for db in databases:
            print(f"Backing up: {db}")
            sql_file = self.dump_database(db)
            gz_file = self.compress_file(sql_file)
            print(f"✔ Backup created: {gz_file}")


if __name__ == "__main__":
    password = getpass.getpass("Enter MariaDB root password: ")

    config = MariaDBBackupConfig(
        user="root",
        password=password,
        backup_dir="/home/sal/backups/mariadb"
    )

    service = MariaDBBackupService(config)
    service.backup_all()

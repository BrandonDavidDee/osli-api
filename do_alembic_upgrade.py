import getopt
import os
import sys

from dotenv import load_dotenv

from alembic import command
from alembic.config import Config

load_dotenv()


def do_alembic_update(argv: list[str]) -> None:
    """
    This script is intended to be used instead of manually running "alembic upgrade head".
    With separate sets of database env variables for dev and production this can be used to easily
    run alembic upgrades on both environments.

    Requiring manual entry of the db server password (instead of grabbing it from env variable) is
    meant to SLOW YOU DOWN and think about exactly which database server you are affecting so you can
    avoid running an unintended upgrade against your production server.
    """
    server_name: str | None = None
    db_name: str | None = None
    arg_environment: str = ""
    db_username: str = ""
    db_password: str = ""
    arg_help: str = "{0} -e <environment> -p <db_password>".format(argv[0])

    try:
        opts, args = getopt.getopt(
            argv[1:],
            "he:p:",
            ["help", "environment=", "db_password="],
        )
    except getopt.GetoptError:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-e", "--environment"):
            arg_environment = arg
        elif opt in ("-p", "--db_password"):
            db_password = arg

    if arg_environment not in ["localhost", "production"]:
        print("-e options are localhost or production")
        sys.exit(2)

    if not db_password:
        print("-p is required")
        sys.exit(2)

    if arg_environment == "production":
        server_name = os.environ["PRODUCTION_DATABASE_HOST"]
        db_name = os.environ["PRODUCTION_DATABASE_NAME"]
        db_username: str = os.getenv("PRODUCTION_DATABASE_USERNAME")

    elif arg_environment == "localhost":
        server_name = os.environ["DATABASE_HOST"]
        db_name = os.environ["DATABASE_NAME"]
        db_username: str = os.getenv("DATABASE_USERNAME")

    if not server_name:
        print("Error: No Server Name")
        sys.exit(2)

    if not db_name:
        print("Error: No Database Name")
        sys.exit(2)

    conn: str = (
        f"postgresql+asyncpg://{db_username}:{db_password}@{server_name}:5432/{db_name}"
    )

    cwd: str = os.getcwd()

    alembic_ini_location: str = f"{cwd}/alembic.ini"
    alembic_cfg: Config = Config(alembic_ini_location)
    alembic_cfg.set_main_option("sqlalchemy.url", conn)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    do_alembic_update(sys.argv)

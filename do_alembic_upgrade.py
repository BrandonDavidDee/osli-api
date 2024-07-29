import getopt
import os
import sys
from alembic.config import Config
from dotenv import load_dotenv

from alembic import command

load_dotenv()


def do_alembic_update(argv):
    server_name: str | None = None
    db_name: str | None = None
    arg_environment: str = ""
    db_username: str = ""
    db_password: str = ""
    arg_help = "{0} -e <environment> -u <db_username>".format(argv[0])

    try:
        opts, args = getopt.getopt(
            argv[1:],
            "he:u:p:",
            ["help", "environment=", "db_username="],
        )
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-e", "--environment"):
            arg_environment = arg
        elif opt in ("-u", "--db_username"):
            db_username = arg

    if arg_environment not in ["localhost", "production"]:
        print("-e options are localhost or production")
        sys.exit(2)

    if not db_username:
        print("-u is required")
        sys.exit(2)

    if arg_environment == "production":
        server_name = os.environ["PRODUCTION_DATABASE_HOST"]
        db_name = os.environ["PRODUCTION_DATABASE_NAME"]
        db_password = os.environ["PRODUCTION_DATABASE_PASSWORD"]

    elif arg_environment == "localhost":
        server_name = os.environ["DATABASE_HOST"]
        db_name = os.environ["DATABASE_NAME"]
        db_password = os.environ["DATABASE_PASSWORD"]

    if not server_name:
        print("Error: No Server Name")
        sys.exit(2)

    if not db_name:
        print("Error: No DataBase Name")
        sys.exit(2)

    if not db_password:
        print("Error: No DataBase Password")
        sys.exit(2)

    conn = f"postgresql+asyncpg://{db_username}:{db_password}@{server_name}:5432/{db_name}"

    cwd = os.getcwd()

    alembic_ini_location = f"{cwd}/alembic.ini"
    alembic_cfg = Config(alembic_ini_location)
    alembic_cfg.set_main_option("sqlalchemy.url", conn)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    do_alembic_update(sys.argv)

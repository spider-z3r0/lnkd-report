#!usr/bin/env python3

import ruamel.yaml as ym
from .models import Account, ConfigFile
from pydantic import ValidationError
from pathlib import Path


def main():
    print("Hello from yaml parser")


def capture_config_file(file_path: Path) -> ConfigFile:
    """
    Validates and captures a YAML configuration file path for further parsing.

    This function first checks that the provided path has a valid YAML extension
    (.yml or .yaml) using the ConfigFile model's internal validation. It then ensures
    that the specified file actually exists on disk before proceeding.

    This two-step validation helps catch common issues early and provides
    clear guidance for correcting mistakes, making the setup process
    smoother for users.

    Parameters
    ----------
    file_path : pathlib.Path
        The path to the configuration file to validate.

    Returns
    -------
    ConfigFile
        A validated ConfigFile instance representing the provided path.

    Raises
    ------
    ValueError
        If the file path does not have a '.yml' or '.yaml' extension.
    FileNotFoundError
        If the specified YAML file does not exist at the given path.
    """
    try:
        file = ConfigFile(path=file_path)  # Validate extension first
        if not file.path.exists():
            raise FileNotFoundError(
                f"Could not find the file '{file_path.name}'. "
                "ase check that the file name and location are correct."
            )
        return file
    except ValidationError as e:
        raise ValueError(
            f"Invalid configuration file path: {e}. "
            "Please provide a file ending in '.yml' or '.yaml'."
        )


def parse_accounts(config_path: ConfigFile, dump: bool = False) -> list[Account]:
    """
    Parses and validates the 'data' section from a YAML configuration file.

    This function reads the specified configuration file, extracts the acccounts and
    and validates their structure using the Account model. It optionally allows users
    to view the parsed configuration for learning or debugging purposes.

    Parameters
    ----------
    config_path : ConfigFile
        A validated ConfigFile instance pointing to the YAML file.
    dump : bool, optional
        If True, pretty-prints the parsed DataSet for easy inspection (default is False).

    Returns
    -------
    Account
        A list of Account instances populated from the YAML configuration.

    Raises
    ------
    KeyError
        If there are problems with accounts. 
    """
    accounts = []
    yaml = ym.YAML()
    with open(config_path.path, "r") as conf:
        account_config = yaml.load(conf)["accounts"]

        for a in account_config:
            accounts.append(
                Account(
                    name=a["name"],
                    linkedin_url=a["linkedin_url"]
                    )
            )

        if len(accounts) < 1:
            raise ValueError(
                    "No accounts found"
                    )
        else:
            return accounts


if __name__ == "__main__":
    main()

#!usr/bin/python


import pathlib as pl
import src

def main():
    print("Hello from lnkd-report")
    y_path = pl.Path(__file__).parent.parent / "test_yaml.yml"
    try:
        yml = src.capture_config_file(y_path)
        print(f"{yml}")
    except Exception as e:
        print(f"Couldn't import the thing {e}")

    try:
        accounts = src.parse_accounts(yml)
    except Exception as e:
        print(f"Couldn't import the accounts {e}")

    try:
        posts = src.find_posts(accounts)
    except Exception as e:
        print(f"failed finding posts \n{e}")

    with open(y_path.parent / "posts.csv", "w") as f:
        f.writelines(
            [p.model_dump_json(indent=2) for p in posts]
            )




if __name__ == '__main__':
    main()

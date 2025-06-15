#!usr/bin/python

import pathlib as pl
import csv
from datetime import datetime
import src

def main():
    print("Hello from lnkd-report")
    resources = pl.Path(__file__).parent.parent/"resources" 
    output = resources.parent/"output"
    y_path = resources / "test_yaml.yml"
    
    try:
        yml = src.capture_config_file(y_path)
        print(f"{yml}")
    except Exception as e:
        print(f"Couldn't import the thing: {e}")
        return

    try:
        accounts = src.parse_accounts(yml)
    except Exception as e:
        print(f"Couldn't import the accounts: {e}")
        return

    try:
        
        posts = sorted([
            src.Post.from_content(**p.model_dump())
            for p in src.find_posts(accounts)
            if not p.is_repost
        ], key = lambda p: p.author)
    except Exception as e:
        print(f"Failed finding posts: {e}")
        return

    try:
        src.render_template(
            posts=posts,
            template_path=resources / "template.qmd.j2",
            output_path=output/ f"linkedin_report_{datetime.today().date()}.qmd"
        )
    except Exception as e:
        print(f"Couldn't produce report: {e}")

    try:
        csv_path = y_path.parent / f"posts_{datetime.today().date()}.csv"
        with open(csv_path, "w", encoding="utf-8", newline='') as f:
            if posts:
                fieldnames = list(posts[0].model_dump().keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for p in posts:
                    writer.writerow(p.model_dump())
        print(f"✅ CSV saved to {csv_path}")
    except Exception as e:
        print(f"Failed writing posts to CSV: {e}")

if __name__ == '__main__':
    main()


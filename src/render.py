#!usr/env/bin python3

from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from src.models import Post
import subprocess

def render_template(posts: list[Post], template_path: Path, output_path: Path):
    env = Environment(loader=FileSystemLoader(template_path.parent))
    template = env.get_template(template_path.name)

    rendered = template.render(posts=posts)
    output_path.write_text(rendered, encoding="utf-8")

    try:
        subprocess.run(["quarto", "render", str(output_path)], check=True)
        print(f"✅ Rendered Quarto document: {output_path.with_suffix('.html')}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Quarto render failed: {e}")

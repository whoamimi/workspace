import re
from pathlib import Path
import yaml


def define_env(env):
    @env.macro
    def latest_posts(limit=5):
        posts_dir = Path(env.conf["docs_dir"]) / "blog" / "posts"
        posts = []
        for f in posts_dir.glob("*.md"):
            text = f.read_text(encoding="utf-8")
            m = re.match(r"^---\n(.*?)\n---", text, re.S)
            meta = yaml.safe_load(m.group(1)) if m else {}
            if meta.get("draft"):
                continue
            date = meta.get("date")
            if isinstance(date, dict):
                date = date.get("created")
            title = re.search(r"^# (.+)$", text, re.M)
            posts.append(
                {
                    "date": date,
                    "title": title.group(1) if title else f.stem,
                    "path": f"blog/posts/{f.name}",
                }
            )
        posts.sort(key=lambda p: str(p["date"]), reverse=True)
        return "\n".join(
            f"- [{p['title']}]({p['path']}) — {p['date']}" for p in posts[:limit]
        )

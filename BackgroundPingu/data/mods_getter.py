import json, requests

ignored = []

def get_mods(start: bool=True):
    """I hate python semver. If it wasn't for that I wouldn't have to do all this..."""
    if start: print("Getting mods...")
    path = "./BackgroundPingu/data/mods.json"
    mods = []
    link = "https://raw.githubusercontent.com/tildejustin/mcsr-meta/schema-6/mods.json"
    headers = {'Cache-Control': 'no-cache'}
    res = requests.get(link, headers=headers, timeout=10)
    if res.status_code == 200:
        content = res.text
        for item in ignored: content = content.replace(item, "")
        content = json.loads(content)
        content = content["mods"]
        for item in content:
            item.pop("description", "")
            item.pop("recommended", "")
            item.pop("traits", "")
            item.pop("modid", "")
            item["files"] = item.pop("versions", [])
            item["incompatible"] = item.pop("incompatibilities", [])
            for fi in item["files"]:
                fi.pop("hash", "")
                fi["game_versions"] = [f"=={a}" for a in fi.pop("target_version")]
                fi["name"] = fi["url"].split("/")[-1]
                fi["page"] = fi.pop("url")
            mods.append(item)
        with open(path, "w") as f:
            json.dump(mods, f, indent=4)
    if start: print("  Finished getting mods.")
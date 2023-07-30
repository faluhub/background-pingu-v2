import json, requests

ignored = [
    "{\"version\":\"1.1.1\",\"game_versions\":[\"=1.16.1\"],\"name\":\"lazystronghold-1.1.1.jar\",\"url\":\"https://github.com/Gregor0410/LazyStronghold/releases/download/v1.1.1/lazystronghold-1.1.1.jar\",\"page\":\"https://github.com/Gregor0410/LazyStronghold/releases/tag/v1.1.1\",\"sha1\":\"8fe6b356e19baf39e334947acd31e8dd48b09c88\",\"size\":13744},"
]

def get_mods(start: bool=True):
    """I hate python semver. If it wasn't for that I wouldn't have to do all this..."""
    if start: print("Getting mods...")
    path = "./BackgroundPingu/data/mods.json"
    mods = []
    res = requests.get("https://raw.githubusercontent.com/RedLime/MCSRMods/v4/meta/v4/files.json", timeout=10)
    if res.status_code == 200:
        content = res.text
        for item in ignored: content = content.replace(item, "")
        content = json.loads(content)
        for item in content:
            if item["type"] != "fabric_mod":
                continue
            item.pop("type", "")
            item.pop("description", "")
            item.pop("recommended", "")
            for fi in item["files"]:
                fi.pop("url", "")
                fi.pop("sha1", "")
                fi.pop("size", "")
                vi = 0
                for vs in fi["game_versions"]:
                    parts = vs.split(" ")
                    final_parts = []
                    for v in parts:
                        if v.endswith("-"):
                            for i in range(11):
                                final_parts.append(f"{v[:-1]}.{i}")
                        else:
                            if v.count(".") == 1:
                                v += ".0"
                            try:
                                if v.startswith("<="):
                                    for i in range(int(v.split('.')[2])+1):
                                        final_parts.append(f"{v[:-1]}{i}")
                                elif v.startswith(">="):
                                    for i in range(int(v.split('.')[2]),11):
                                        final_parts.append(f"{v[:-1]}{i}")
                                else: final_parts.append(v)
                            except: final_parts.append(v)
                    pi = 0
                    for v in final_parts:
                        if v.count(".") == 1:
                            v += ".0"
                        if v.startswith("=1"):
                            v = v.replace("=1", "==1")
                        elif v.startswith("~1"):
                            v = v.replace("~1", "<=1")
                        final_parts[pi] = v
                        pi += 1
                    fi["game_versions"][vi] = " ".join(final_parts)
                    vi += 1
            mods.append(item)
        with open(path, "w") as f:
            json.dump(mods, f, indent=4)
    if start: print("  Finished getting mods.")

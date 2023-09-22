import re, requests, enum
from packaging import version
from cached_property import cached_property

class OperatingSystem(enum.IntEnum):
    WINDOWS = enum.auto()
    LINUX = enum.auto()
    MACOS = enum.auto()

class ModLoader(enum.Enum):
    FABRIC = "Fabric"
    QUILT = "Quilt"
    FORGE = "Forge"
    VANILLA = "Vanilla"

class Log:
    def __init__(self, content: str) -> None:
        self._content = content
        self._lower_content = self._content.lower()
        self.launchers = [
            "MultiMC",
            "Prism",
            "PolyMC",
            "ManyMC",
            "UltimMC"
        ]
    
    @staticmethod
    def from_link(link: str):
        paste_ee_match = re.search(r"https://paste\.ee/(?:p/|d/)([a-zA-Z0-9]+)", link)
        mclogs_match = re.search(r"https://mclo\.gs/(\w+)", link)
        if paste_ee_match: link = f"https://paste.ee/d/{paste_ee_match.group(1)}/0"
        elif mclogs_match: link = f"https://api.mclo.gs/1/raw/{mclogs_match.group(1)}"
        elif not link.endswith(".txt") and not link.endswith(".log"): return None
        res = requests.get(link, timeout=5)
        if res.status_code == 200:
            return Log(res.text.replace("\r", ""))
        return None

    @cached_property
    def mods(self) -> list[str]:
        pattern = re.compile(r"\[✔️\]\s+([^\[\]]+\.jar)")
        mods = pattern.findall(self._content)
        pattern = re.compile(r"\[✔\]\s+([^\[\]\n]+)")
        mods += [mod.rstrip("\n").replace(" ", "+") + ".jar" for mod in pattern.findall(self._content)]
        return mods
    
    @cached_property
    def java_version(self) -> str:
        match = re.compile(r"Checking Java version\.\.\.\n(.*)\n").search(self._content)
        if not match is None:
            line = match.group(1)
            version_match = re.compile(r"Java is version (\S+),").search(line)
            if not version_match is None:
                return version_match.group(1)
        version_match = re.compile(r"Java Version: (\S+),").search(self._content)
        if not version_match is None:
            return version_match.group(1)
        return None
    
    @cached_property
    def major_java_version(self) -> int:
        if not self.java_version is None:
            parts = self.java_version.split(".")
            try:
                if not parts[0] == "1": return int(parts[0])
                return int(parts[1])
            except: pass
        return None
    
    @cached_property
    def minecraft_folder(self) -> str:
        match = re.compile(r"Minecraft folder is:\n(.*)\n").search(self._content)
        return match.group(1).strip() if not match is None else None
    
    @cached_property
    def operating_system(self) -> OperatingSystem:
        if self.minecraft_folder is None:
            return OperatingSystem.WINDOWS if "-natives-windows.jar" in self._content else None
        if self.minecraft_folder.startswith("/"):
            if len(self.minecraft_folder) > 1 and self.minecraft_folder[1].isupper():
                return OperatingSystem.MACOS
            return OperatingSystem.LINUX
        return OperatingSystem.WINDOWS
    
    @cached_property
    def minecraft_version(self) -> str:
        match = re.compile(r"Params:\n(.*?)\n", re.DOTALL).search(self._content)
        if not match is None:
            line = match.group(1)
            version_match = re.compile(r"--version (\S+)\s").search(line)
            if not version_match is None:
                return version_match.group(1)
        match = re.compile(r"Loading Minecraft (\S+) with Fabric Loader").search(self._content)
        if not match is None:
            return match.group(1)
        match = re.compile(r"Minecraft Version ID: (\S+)").search(self._content)
        if not match is None:
            return match.group(1)
        return None
    
    @cached_property
    def short_version(self) -> str:
        if not self.minecraft_version is None:
            return self.minecraft_version[:4]
        return None
    
    @cached_property
    def fabric_version(self) -> version.Version:
        match = re.compile(r"Loading Minecraft \S+ with Fabric Loader (\S+)").search(self._content)
        try:
            if not match is None: return version.parse(match.group(1))
        except: pass
        match = re.compile(r"libraries/net/fabricmc/fabric-loader/\S+/fabric-loader-(\S+).jar").search(self._content)
        try:
            if not match is None: return version.parse(match.group(1))
        except: pass
        return None
    
    @cached_property
    def launcher(self) -> str:
        result = self._content.split(" ", 1)[0]
        return result if result in self.launchers else None

    @cached_property
    def is_multimc_or_fork(self) -> bool:
        return not self.launcher is None

    @cached_property
    def is_prism(self) -> bool:
        return not self.launcher is None and self.launcher.lower() == "prism"
    
    @cached_property
    def mod_loader(self) -> ModLoader:
        match = re.compile(r"Main Class:\n(.*)\n").search(self._content)
        if not match is None:
            line = match.group(1)
            for loader in ModLoader:
                if loader.value.lower() in line.lower():
                    return loader
            if "net.minecraft.launchwrapper.Launch" in line:
                return ModLoader.FORGE
            if "net.minecraft.client.main.Main" in line:
                return ModLoader.VANILLA
        match = re.search(r"Loading Minecraft \S+ with Fabric Loader",self._content)
        if not match is None:
            return ModLoader.FABRIC
        match = re.search(r"Client brand changed to '(\S+)'",self._content)
        if match:
            for loader in ModLoader:
                if loader.value.lower() in match.group(1).lower():
                    return loader
        if "client brand is untouched" in self._content:
            return ModLoader.VANILLA
        return None
    
    @cached_property
    def java_arguments(self):
        match = re.compile(r"Java Arguments:\n(.*?)\n", re.DOTALL).search(self._content)
        if not match is None:
            return match.group(1)
        match = re.compile(r"JVM Flags: \S+ total; (.*(?:\n|$))", re.DOTALL).search(self._content)
        if not match is None:
            return match.group(1)
        return None

    @cached_property
    def max_allocated(self):
        if not self.java_arguments is None:
            match = re.compile(r"-Xmx(\d+)m").search(self.java_arguments)
            try:
                if not match is None: return int(match.group(1))
            except ValueError: pass
            match = re.compile(r"-Xmx(\d+)M").search(self.java_arguments)
            try:
                if not match is None: return int(match.group(1))
            except ValueError: pass
            match = re.compile(r"-Xmx(\d+)G").search(self.java_arguments)
            try:
                if not match is None: return int(match.group(1))*1024
            except ValueError: pass
        return None
    
    def has_content(self, content: str) -> bool:
        return content.lower() in self._lower_content
    
    def has_mod(self, mod_name: str) -> bool:
        for mod in self.mods:
            if mod_name.lower() in mod.lower():
                return True
        return False
    
    def has_java_argument(self, argument: str) -> bool:
        return argument.lower() in self.java_arguments.lower()
    
    def upload(self) -> (bool, str):
        api_url = "https://api.mclo.gs/1/log"
        payload = {
            "content": self._content
        }
        response = requests.post(api_url, data=payload)
        if response.status_code == 200:
            match = re.search(r"/(Users|home)/([^/]+)/", self._content)
            return (
                match and match.group(2).lower() not in ["user", "admin", "********"],
                response.json().get("url")
            )
    
    def __str__(self) -> str:
        return f"mods={self.mods}\njava_version={self.java_version}\nmajor_java_version={self.major_java_version}\nminecraft_folder={self.minecraft_folder}\noperating_system={self.operating_system}\nminecraft_version={self.minecraft_version}\nfabric_version={self.fabric_version}\nlauncher={self.launcher}\ncustom_launcher={self.custom_launcher}\nmod_loader={self.mod_loader}\njava_arguments={self.java_arguments}\nmax_allocated={self.max_allocated}"

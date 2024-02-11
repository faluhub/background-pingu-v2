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
        paste_ee_match = re.search(r"https://(?:api\.)?paste\.ee/(?:p/|d/)([a-zA-Z0-9]+)", link)
        mclogs_match = re.search(r"https://mclo\.gs/(\w+)", link)
        if paste_ee_match: link = f"https://paste.ee/d/{paste_ee_match.group(1)}/0"
        elif mclogs_match: link = f"https://api.mclo.gs/1/raw/{mclogs_match.group(1)}"
        elif not ".txt" in link and not ".log" in link: return None
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
    def fabric_mods(self) -> list[str]:
        if self.type == "thread dump": return []

        excluded_prefixes = [
            "java ",
            "fabricloader ",
            "minecraft ",
        ]

        pattern = re.compile(r"\t- ([^\n]+)", re.DOTALL)

        fabric_mods = []
        for mod in pattern.findall(self._content):
            mod = mod.replace("_", "-")
            if not any(mod.startswith(prefix) for prefix in excluded_prefixes) and not " via " in mod:
                fabric_mods.append(mod)
        
        return fabric_mods
    
    @cached_property
    def whatever_mods(self) -> list[str]:
        return self.mods if len(self.mods) > 0 else self.fabric_mods

    @cached_property
    def java_version(self) -> str:
        version_match = re.compile(r"\nJava is version (\S+),").search(self._content) # mmc/prism logs
        if not version_match is None:
            return version_match.group(1)
        
        version_match = re.compile(r"\n\tJava Version: (\S+),").search(self._content) # crash reports
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
            except ValueError: pass
        
        match = re.search(r"\s*- java (\d+)", self._content)
        if not match is None:
            return int(match.group(1))

        return None
    
    @cached_property
    def minecraft_folder(self) -> str:
        match = re.compile(r"Minecraft folder is:\n(.*)\n").search(self._content)
        if not match is None: return match.group(1).strip()
        return None
    
    @cached_property
    def operating_system(self) -> OperatingSystem:
        if not self.minecraft_folder is None:
            if self.minecraft_folder.startswith("/"):
                if len(self.minecraft_folder) > 1 and self.minecraft_folder[1].isupper():
                    return OperatingSystem.MACOS
                return OperatingSystem.LINUX
            return OperatingSystem.WINDOWS
        
        if self.has_content("-natives-windows.jar"): return OperatingSystem.WINDOWS
        
        if self.has_content("Operating System: Windows"): return OperatingSystem.WINDOWS
        if self.has_content("Operating System: Mac OS"): return OperatingSystem.MACOS

        return None
    
    @cached_property
    def minecraft_version(self) -> str:
        for pattern in [
            r"Loading Minecraft (\S+) with Fabric Loader",
            r"Minecraft Version ID: (\S+)",
            r"Minecraft Version: (\S+)",
            r"\n\t- minecraft (\S+)\n",
            r"/net/minecraftforge/forge/(\S+?)-",
            r"--version, (\S+),",
        ]:
            match = re.compile(pattern).search(self._content)
            if not match is None:
                return match.group(1)
        
        return None
    
    @cached_property
    def parsed_mc_version(self) -> version.Version:
        if self.minecraft_version is None: return None
        
        try:
            return version.parse(self.minecraft_version)
        except version.InvalidVersion: return None
    
    @cached_property
    def fabric_mc_version(self) -> str:
        for pattern in [
            r"libraries/net/fabricmc/intermediary/(\S+)/intermediary-"
        ]:
            match = re.compile(pattern).search(self._content)
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
        for pattern in [
            r"Loading Minecraft \S+ with Fabric Loader (\S+)",
            r"libraries/net/fabricmc/fabric-loader/\S+/fabric-loader-(\S+).jar",
        ]:
            match = re.compile(pattern).search(self._content)
            try:
                if not match is None: return version.parse(match.group(1))
            except version.InvalidVersion: pass

        return None
    
    @cached_property
    def launcher(self) -> str:
        result = self._content.split(" ", 1)[0]
        if result in self.launchers: return result
        
        for launcher in self.launchers:
            if self.has_content(f"/{launcher}/") or self.has_content(f"\\{launcher}\\") or self.has_content(f"org.{launcher}."):
                return launcher
        
        if any(self.has_content(prism) for prism in [
            "org.prismlauncher.",
            "/PrismLauncher",
            "\\PrismLauncher",
        ]):
            return "Prism"
        
        if (self.has_content("\\AppData\\Roaming\\.minecraft")
            or self.has_content("/AppData/Roaming/.minecraft")
            or self.has_pattern(r"-Xmx(\d+)G")
        ):
            return "Official Launcher"
        
        if self.max_allocated == 1024:
            return "MultiMC"

        return None
    
    @cached_property
    def type(self) -> str:
        if any([self._content.startswith(launcher) for launcher in self.launchers]):
            return "full log"

        if self.has_content("-- Thread Dump --"):
            return "thread dump"

        if self._content.startswith("---- Minecraft Crash Report ----"):
            return "crash-report"

        if self.has_content("---------------  T H R E A D  ---------------"):
            return "hs_err_pid log"

        if self._content.startswith("["):
            return "latest.log"

        return None

    @cached_property
    def is_multimc_or_fork(self) -> bool:
        return not self.launcher is None and self.launcher != "Official Launcher"

    @cached_property
    def is_prism(self) -> bool:
        return self.launcher in ["Prism", "PolyMC"]

    @cached_property
    def edit_instance(self) -> bool:
        return "" if self.is_prism else " Instance"
    
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
        
        if self.has_pattern(r"Loading Minecraft \S+ with Fabric Loader"):
            return ModLoader.FABRIC
        
        match = re.search(r"Client brand changed to '(\S+)'", self._content)
        if match:
            for loader in ModLoader:
                if loader.value.lower() in match.group(1).lower():
                    return loader
        
        if self.has_content("client brand is untouched"):
            return ModLoader.VANILLA

        if any(self.has_content(content) for content in [
            "\nhttps://maven.minecraftforge.net",
            "\nhttps://maven.neoforged.net",
            "net.minecraftforge.",
            "--fml.forgeVersion, ",
        ]):
            return ModLoader.FORGE
        
        return None
    
    @cached_property
    def java_arguments(self) -> str:
        match = re.compile(r"Java Arguments:\n(.*?)\n", re.DOTALL).search(self._content)
        if not match is None:
            return match.group(1)
        
        match = re.compile(r"JVM Flags: \S+ total; (.*(?:\n|$))", re.DOTALL).search(self._content)
        if not match is None:
            return match.group(1)
        
        return None

    @cached_property
    def max_allocated(self) -> int:
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
    
    @cached_property
    def recommended_min_allocated(self) -> tuple[int, int, int]:
        min_limit_0, min_limit_1, min_limit_2 = 0, 0, 0

        if self.is_newer_than("1.18"):
            min_limit_0 += 5000
            min_limit_1 += 3400
            min_limit_2 += 1300
        elif self.is_newer_than("1.14"):
            min_limit_0 += 2800
            min_limit_1 += 1800
            min_limit_2 += 1200
        else:
            min_limit_0 += 2000
            min_limit_1 += 1500
            min_limit_2 += 700
        
        mod_cnt = len(self.whatever_mods)
        if self.mod_loader == ModLoader.FORGE:
            min_limit_0 += min(mod_cnt * 100, 5000)
            min_limit_1 += min(mod_cnt * 100, 1000)
            min_limit_2 += min(mod_cnt * 50, 200)
        
        if self.has_java_argument("shenandoah"):
            min_limit_0 *= 0.7
            min_limit_1 *= 0.7
            min_limit_2 *= 0.7
        
        if self.has_java_argument("zgc"):
            min_limit_0 *= 1.7
            min_limit_1 *= 1.3
            min_limit_2 *= 1.3
        
        return (min_limit_0, min_limit_1, min_limit_2)
    
    @cached_property
    def recommended_max_allocated(self) -> tuple[int, int, int]:
        max_limit_0, max_limit_1, max_limit_2 = 0, 0, 0

        if self.is_newer_than("1.18"):
            max_limit_0 += 15000
            max_limit_1 += 8000
            max_limit_2 += 6300
        elif self.is_newer_than("1.14"):
            max_limit_0 += 10000
            max_limit_1 += 4500
            max_limit_2 += 3200
        else:
            max_limit_0 += 8000
            max_limit_1 += 3200
            max_limit_2 += 2200
        
        mod_cnt = len(self.whatever_mods)
        if self.mod_loader == ModLoader.FORGE:
            max_limit_0 += min(mod_cnt * 400, 4000)
            max_limit_1 += max(min(mod_cnt * 200, 1500), 9000)
            max_limit_2 += max(min(mod_cnt * 100, 800), 8000)
        
        if self.has_java_argument("shenandoah"):
            max_limit_0 *= 0.7
            max_limit_1 *= 0.7
            max_limit_2 *= 0.7
        
        if self.has_java_argument("zgc"):
            max_limit_0 *= 1.3
            max_limit_1 *= 1.3
            max_limit_2 *= 1.3
        
        return (max_limit_0, max_limit_1, max_limit_2)

    @cached_property
    def ram_guide(self) -> tuple[str, int, int]:
        return (
            "allocate_ram_guide_mmc" if self.is_multimc_or_fork else "allocate_ram_guide",
            self.recommended_min_allocated[1],
            self.recommended_max_allocated[2]
        )
    
    @cached_property
    def libraries(self) -> str:
        pattern = r"\nLibraries:\n(.*?)\nNative libraries:\n"
        match = re.search(pattern, self._content, re.DOTALL)
        if not match is None:
            return match.group(1)
        
        return None
    
    @cached_property
    def stacktrace(self) -> str:
        ignored_pattern = r"(?s)---- Minecraft Crash Report ----.*?This is just a prompt for computer specs to be printed"
        log = re.sub(ignored_pattern, "", self._content)
        
        crash_patterns = [
            r"---- Minecraft Crash Report ----.*A detailed walkthrough of the error",
            r"Failed to start Minecraft:.*",
            r"Unable to launch\n.*",
            r"Exception caught from launcher\n.*",
            r"Reported exception thrown!\n.*",
            r"Shutdown failure!\n.*",
            r"Minecraft has crashed!.*",
        ]
        for crash_pattern in crash_patterns:
            match = re.search(crash_pattern, log, re.DOTALL)
            if not match is None:
                return match.group().lower().replace("fast_reset", "fastreset")
        
        return None
    
    @cached_property
    def exitcode(self) -> int:
        patterns = [
            r"Process crashed with exit code (-?\d+)",
            r"Process crashed with exitcode (-?\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, self._content, re.DOTALL)
            if not match is None:
                try: return int(match.group(1))
                except ValueError: pass
        
        for exit_code in [-1073741819, -1073740791, -805306369]:
            if self.has_content(f" {exit_code}"): return exit_code

        return None
    
    def is_newer_than(self, compared_version: str) -> bool:
        if self.parsed_mc_version is None: return False

        return self.parsed_mc_version >= version.parse(compared_version)
    
    def has_content(self, content: str) -> bool:
        return content.lower() in self._lower_content
    
    def has_content_in_stacktrace(self, content: str) -> bool:
        if self.stacktrace is None: return False
        return content.lower() in self.stacktrace.lower()

    def has_pattern(self, pattern: str) -> bool:
        return bool(re.compile(pattern, re.IGNORECASE).search(self._lower_content))
    
    def has_mod(self, mod_name: str) -> bool:
        for mod in self.mods + self.fabric_mods:
            if mod_name.lower() in mod.lower():
                return True
        return False
    
    def has_normal_mod(self, mod_name: str) -> bool:
        for mod in self.mods:
            if mod_name.lower() in mod.lower():
                return True
        return False
    
    def has_java_argument(self, argument: str) -> bool:
        return argument.lower() in self.java_arguments.lower()
    
    def has_library(self, content: str) -> bool:
        return content.lower() in self.libraries.lower()
    
    def upload(self) -> tuple[bool, str]:
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
        return f"mods={self.mods}\nfabric_mods={self.fabric_mods}\njava_version={self.java_version}\nmajor_java_version={self.major_java_version}\nminecraft_folder={self.minecraft_folder}\noperating_system={self.operating_system}\nminecraft_version={self.minecraft_version}\nfabric_version={self.fabric_version}\nlauncher={self.launcher}\nis_prism={self.is_prism}\nis_multimc_or_fork={self.is_multimc_or_fork}\nmod_loader={self.mod_loader}\njava_arguments={self.java_arguments}\nmax_allocated={self.max_allocated}"
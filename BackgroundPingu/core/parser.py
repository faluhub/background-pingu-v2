import re, requests, enum
from packaging import version
from cached_property import cached_property

class OperatingSystem(enum.IntEnum):
    WINDOWS = enum.auto()
    LINUX = enum.auto()
    MACOS = enum.auto()

class LogType(enum.Enum):
    FULL_LOG = "full log"
    THREAD_DUMP = "thread dump"
    CRASH_REPORT = "crash-report"
    HS_ERR_PID_LOG = "hs_err_pid log"
    LATEST_LOG = "latest.log"
    LAUNCHER_LOG = "launcher log"

class Launcher(enum.Enum):
    OFFICIAL_LAUNCHER = "Official Launcher"
    MULTIMC = "MultiMC"
    PRISM = "Prism"
    MODRINTH = "Modrinth App"

class ModLoader(enum.Enum):
    FABRIC = "Fabric"
    QUILT = "Quilt"
    FORGE = "Forge"
    VANILLA = "Vanilla"

class Log:
    def __init__(self, content: str) -> None:
        self.leaked_pc_username = False
        pattern = r"(/|\\|//|\\\\)(Users|home)(/|\\|//|\\\\)([^/\\]+)(/|\\|//|\\\\)"
        for match in re.findall(pattern, content):
            if match and match[3].lower() not in ["user", "admin", "********"]:
                self.leaked_pc_username = True
                break
        match = None
        content = re.sub(pattern, r"\1\2\3********\5", content)

        pattern = r"\"USERNAME=([^/\\]+)\"" # from mmc/prism logs
        for match in re.findall(pattern, content):
            if match and match[3].lower() not in ["user", "admin", "********"]:
                self.leaked_pc_username = True
                break
        match = None
        content = re.sub(pattern, r"\"USERNAME=********\"", content)

        # just replacing pc_username with "" is a bad idea
        # for instance, if it's "Alex", it could also replace it in the mod "Alex Caves", which would leak it

        pattern = r"Session ID is token:.{30,}?\n"
        if re.search(pattern, content) is not None:
            replacement = "Session ID is (redacted))\n"
            content = re.sub(pattern, replacement, content)
            self.leaked_session_id = True
        else: self.leaked_session_id = False

        self._content = content
        self._lower_content = self._content.lower()
        self.lines = self._content.count("\n") + 1
    
    @staticmethod
    def from_link(link: str):
        paste_ee_match = re.search(r"https://(?:api\.)?paste\.ee/(?:p/|d/)([a-zA-Z0-9]+)", link)
        mclogs_match = re.search(r"https://mclo\.gs/(\w+)", link)
        if paste_ee_match: link = f"https://paste.ee/d/{paste_ee_match.group(1)}/0"
        elif mclogs_match: link = f"https://api.mclo.gs/1/raw/{mclogs_match.group(1)}"
        elif not ".txt" in link and not ".log" in link and not ".tdump" in link: return None
        res = requests.get(link, timeout=5)
        if res.status_code == 200:
            return Log(res.text.replace("\r", ""))
        elif res.status_code != 404:
            return Log(f"__PINGU__DOWNLOAD_ERROR__{res.status_code}__")
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
        if self.type == LogType.THREAD_DUMP: return []

        excluded_prefixes = [
            "java ",
            "fabricloader ",
            "minecraft ",
        ]
        excluded_patterns = [
            r" via ",
            r"<0x.*>",
        ]

        pattern = re.compile(r"\t- ([^\n]+)", re.DOTALL)

        fabric_mods = []
        for mod in pattern.findall(self._content):
            mod = mod.replace("_", "-")
            if (not any(mod.startswith(prefix) for prefix in excluded_prefixes)
                and not any(re.search(pattern, mod) for pattern in excluded_patterns)
            ):
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
                if len(parts) > 1: return int(parts[1])
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
        
        if self.has_content("Operating System: Windows"): return OperatingSystem.WINDOWS
        if self.has_content("Operating System: Mac OS"): return OperatingSystem.MACOS
        if self.has_content("Operating System: Linux"): return OperatingSystem.LINUX
        
        if self.has_content("-natives-windows.jar"): return OperatingSystem.WINDOWS

        if self.has_content("/Applications/"): return OperatingSystem.MACOS

        return None
    
    @cached_property
    def minecraft_version(self) -> str:
        if self.type == LogType.LAUNCHER_LOG: return None

        for pattern in [
            r"Loading Minecraft (\S+) with Fabric Loader",
            r"Minecraft Version ID: (\S+)",
            r"Minecraft Version: (\S+)",
            r"\n\t- minecraft (\S+)\n",
            r"/com/mojang/minecraft/(\S+?)/",
            r"/net/minecraftforge/forge/(\S+?)-",
            r"--version, (\S+),",
            r"minecraft server version (\S+)\n",
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
    def loader_mc_version(self) -> str:
        for pattern in [
            r"libraries/net/fabricmc/intermediary/(\S+)/intermediary-",
            r"--fml.mcVersion (\S+)",
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
    def launcher(self) -> Launcher:
        for prism_name in [
            "prism",
            "polymc",
            "pollymc",
        ]:
            if self.has_pattern(rf"^{prism_name}"):
                return Launcher.PRISM
            if any(self.has_content(prism) for prism in [
                f"org.{prism_name}",
                f"/{prism_name}",
                f"\\{prism_name}",
            ]):
                return Launcher.PRISM
        
        for multimc_name in [
            "multimc",
            "ultimmc",
        ]:
            if self.has_pattern(rf"^{multimc_name}"):
                return Launcher.MULTIMC
            if any(self.has_content(multimc) for multimc in [
                f"org.{multimc_name}",
                f"/{multimc_name}",
                f"\\{multimc_name}",
            ]):
                return Launcher.MULTIMC
        
        if any(self.has_content(modrinth) for modrinth in [
            "com.modrinth.theseus",
        ]):
            return Launcher.MODRINTH
        
        if (self.has_content("\\AppData\\Roaming\\.minecraft")
            or self.has_content("/AppData/Roaming/.minecraft")
            or self.has_pattern(r"-Xmx(\d+)G")
        ):
            return Launcher.OFFICIAL_LAUNCHER
        
        if self.max_allocated == 1024:
            return Launcher.MULTIMC

        return None

    @cached_property
    def type(self) -> LogType:
        if any([self._content.startswith(launcher.value) for launcher in Launcher]):
            return LogType.FULL_LOG

        if any(self.has_content(thread_dump) for thread_dump in [
            "-- Thread Dump --",
            "\nFull thread dump"
        ]):
            return LogType.THREAD_DUMP

        if self._content.startswith("---- Minecraft Crash Report ----"):
            return LogType.CRASH_REPORT
        
        if self.has_content("---------------  T H R E A D  ---------------"):
            return LogType.HS_ERR_PID_LOG

        if self.has_content(" D | "):
            return LogType.LAUNCHER_LOG

        if self._content.startswith("["):
            return LogType.LATEST_LOG

        return None

    @cached_property
    def is_multimc_or_fork(self) -> bool:
        return not self.launcher is None and self.launcher != Launcher.OFFICIAL_LAUNCHER

    @cached_property
    def is_prism(self) -> bool:
        return self.launcher == Launcher.PRISM

    @cached_property
    def edit_instance(self) -> str:
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
        if not match is None:
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
            min_limit_1 += 3000
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
        
        if self.is_ssg_log:
            min_limit_0 *= 0.7
            min_limit_1 *= 0.7
            min_limit_2 *= 0.7
        
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
            max_limit_2 += 6000
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
        
        if self.is_ssg_log:
            max_limit_0 *= 0.8
            max_limit_1 *= 0.8
            max_limit_2 *= 0.8
        
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
        min_recomm = self.recommended_min_allocated[1]
        max_recomm = self.recommended_max_allocated[2]
        diff = max_recomm - min_recomm
        min_recomm = int(round(min_recomm + diff / 7, -2))
        max_recomm = int(round(max_recomm - diff / 7, -2))

        if self.is_multimc_or_fork:
            return (
                "allocate_ram_guide_mmc",
                min_recomm,
                max_recomm,
                "Prism" if self.is_prism else "MultiMC",
            )
        else:
            return ("allocate_ram_guide", min_recomm, max_recomm)

    @cached_property
    def java_update_guide(self) -> str:
        if self.launcher == Launcher.OFFICIAL_LAUNCHER:
            if self.operating_system == OperatingSystem.MACOS: return "mac_setup_guide"
            return "k4_setup_guide"

        return "java_update_guide"
    
    @cached_property
    def libraries(self) -> str:
        pattern = r"\nLibraries:\n(.*?)\nNative libraries:\n"
        match = re.search(pattern, self._content, re.DOTALL)
        if not match is None:
            return match.group(1)
        
        return None
    
    @cached_property
    def stacktrace(self) -> str:
        log = self._content
        ignored_patterns = [
            r"(?s)---- Minecraft Crash Report ----.*?This is just a prompt for computer specs to be printed",
            r"(?s)WARNING: coremods are present:.*?Contact their authors BEFORE contacting forge"
        ]
        for pattern in ignored_patterns:
            log = re.sub(pattern, "", log)
        
        crash_patterns = [
            r"---- Minecraft Crash Report ----.*A detailed walkthrough of the error",
            r"-- Crash --.*-- Mods --",
            r"Failed to start Minecraft:.*",
            r"Unable to launch\n.*",
            r"Exception caught from launcher\n.*",
            r"Reported exception thrown!\n.*",
            r"Shutdown failure!\n.*",
            r"Minecraft has crashed!.*",
            r"A mod crashed on startup!\n.*",
            r"Encountered an unexpected exception\n.*",
            r"Unhandled game exception\n.*",
        ]
        for crash_pattern in crash_patterns:
            match = re.search(crash_pattern, log, re.DOTALL)
            if not match is None:
                return match.group().lower().replace("fast_reset", "fastreset")
        
        return None
    
    @cached_property
    def exitcode(self) -> int:
        pattern = r"Process (crashed|exited) with (exit)? ?code (-?\d+)"
        match = re.search(pattern, self._content, re.DOTALL)
        if not match is None:
            try: return int(match.group(3))
            except ValueError: pass
        
        for exit_code in [-1073741819, -1073740791, -805306369, -1073740771]:
            if self.has_content(f" {exit_code}"): return exit_code

        return None

    @cached_property
    def is_ssg_log(self) -> bool:
        for ssg_mod in [
            "setspawn",
            "chunkcacher"
        ]:
            if self.has_mod(ssg_mod): return True
        
        return False

    @cached_property
    def is_ranked_log(self) -> bool:
        for ranked_mod in [
            "mcsrranked"
        ]:
            if self.has_mod(ranked_mod): return True
        
        if self.has_content("com.mcsrranked"): return True
        
        return False
    
    @cached_property
    def is_not_wall_log(self) -> bool:
        if self.is_ranked_log: return True
        
        if self.minecraft_folder is None: return False
        
        if not self.minecraft_folder.replace(self.minecraft_version, "").split("/.minecraft")[0][-1].isdigit():
            return True
        
        return False
    
    @cached_property
    def recommended_mods(self) -> list[str]:
        mods = []

        if self.operating_system == OperatingSystem.MACOS:
            mods.append("retino")

        if not self.is_newer_than("1.15"): return mods
        
        if self.operating_system == OperatingSystem.MACOS and self.minecraft_version == "1.16.1":
            mods.append("sodiummac")
        else:
            mods.append("sodium")
        mods.append("lithium")
        if not self.is_newer_than("1.20"): mods.append("starlight")

        if self.launcher != Launcher.OFFICIAL_LAUNCHER and not self.is_newer_than("1.17"):
            mods.append("voyager")
        
        if self.is_newer_than("1.17"):
            mods.append("planifolia")

        if self.is_ssg_log:
            mods += [
                "setspawn",
                "chunkcacher",
                "SpeedRunIGT",
                "antiresourcereload",
            ]
        elif not self.has_mod("mcsrranked") and not self.has_mod("peepopractice"):
            mods += [
                "antigone",
                "worldpreview",
                "SpeedRunIGT",
                "lazystronghold",
                "antiresourcereload",
                "fast-reset",
                "atum",
            ]
            if not self.is_not_wall_log:
                mods += [
                    "sleepbackground",
                    "state-output",
                ]
        
        return mods
    
    def is_newer_than(self, compared_version: str) -> bool:
        if self.parsed_mc_version is None: return False
        return self.parsed_mc_version >= version.parse(compared_version)
    
    def has_content(self, content: str) -> bool:
        return content.lower() in self._lower_content
    
    def has_content_in_stacktrace(self, content: str) -> bool:
        if self.stacktrace is None: return False
        return content.lower().replace("_","") in self.stacktrace.lower().replace("_","")

    def has_pattern(self, pattern: str) -> bool:
        return bool(re.compile(pattern, re.IGNORECASE).search(self._lower_content))
    
    def has_mod(self, mod_name: str) -> bool:
        mod_name = mod_name.lower().replace(" ", "").replace("-", "")
        for mod in self.mods + self.fabric_mods:
            if mod_name in mod.lower().replace(" ", "").replace("-", ""):
                return True
        return False
    
    def has_normal_mod(self, mod_name: str) -> bool:
        for mod in self.mods:
            if mod_name.lower() in mod.lower():
                return True
        return False
    
    def has_java_argument(self, argument: str) -> bool:
        if self.java_arguments is None: return None
        return argument.lower() in self.java_arguments.lower()
    
    def has_library(self, content: str) -> bool:
        if self.libraries is None: return False
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
        return f"""
mods={self.mods}
fabric_mods={self.fabric_mods}
java_version={self.java_version}
major_java_version={self.major_java_version}
minecraft_folder={self.minecraft_folder}
operating_system={self.operating_system}
minecraft_version={self.minecraft_version}
parsed_mc_version={self.parsed_mc_version}
loader_mc_version={self.loader_mc_version}
short_version={self.short_version}
fabric_version={self.fabric_version}
launcher={self.launcher}
type={self.type}
is_multimc_or_fork={self.is_multimc_or_fork}
is_prism={self.is_prism}
edit_instance={self.edit_instance}
mod_loader={self.mod_loader}
java_arguments={self.java_arguments}
max_allocated={self.max_allocated}
recommended_min_allocated={self.recommended_min_allocated}
recommended_max_allocated={self.recommended_max_allocated}
ram_guide={self.ram_guide}
java_update_guide={self.java_update_guide}
stacktrace={self.stacktrace}
exitcode={self.exitcode}
is_ssg_log={self.is_ssg_log}
is_ranked_log={self.is_ranked_log}
is_not_wall_log={self.is_not_wall_log}
recommended_mods={self.recommended_mods}
""".strip()
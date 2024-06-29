import semver, re, requests
from packaging import version
from BackgroundPingu.bot.main import BackgroundPingu
from BackgroundPingu.core.parser import Log, ModLoader, OperatingSystem, LogType, Launcher

class IssueBuilder:
    def __init__(self, bot: BackgroundPingu, log: Log) -> None:
        self.bot = bot
        self._messages = {
            "top_info": [],
            "error": [],
            "warning": [],
            "note": [],
            "info": []
        }
        self.log = log
        self.amount = 0
        self._last_added = None
        self.footer = ""
    
    def _add_to(self, type: str, value: str, add: bool=False):
        self._messages[type].append(value)
        if not add:
            self.amount += 1
            self._last_added = type
        return self

    def top_info(self, key: str, *args):
        return self._add_to("top_info", "‼️ **" + self.bot.strings.get(f"top_info.{key}", key).format(*args) + "**")

    def error(self, key: str, *args, experimental: bool=False, bold: bool=False):
        text = self.bot.strings.get(f"error.{key}", key).format(*args)
        if bold: text = f"**{text}**"
        if experimental: text = f"**[warning: experimental]** {text}"
        return self._add_to("error", "<:dangerkekw:1123554236626636880> " + text)
    
    def warning(self, key: str, *args, experimental: bool=False, bold: bool=False):
        text = self.bot.strings.get(f"warning.{key}", key).format(*args)
        if bold: text = f"**{text}**"
        if experimental: text = f"**[warning: experimental]** {text}"
        return self._add_to("warning", "<:warningkekw:1123563914454634546> " + text)
    
    def note(self, key: str, *args, experimental: bool=False, bold: bool=False):
        text = self.bot.strings.get(f"note.{key}", key).format(*args)
        if bold: text = f"**{text}**"
        if experimental: text = f"**[warning: experimental]** {text}"
        return self._add_to("note", "<:kekw:1123554521738657842> " + text)

    def info(self, key: str, *args, experimental: bool=False, bold: bool=False):
        text = self.bot.strings.get(f"info.{key}", key).format(*args)
        if bold: text = f"**{text}**"
        if experimental: text = f"**[warning: experimental]** {text}"
        return self._add_to("info", "<:infokekw:1123567743355060344> " + text)

    def add(self, key: str, *args, experimental: bool=False, bold: bool=False):
        text = self.bot.strings.get(f"add.{key}", key).format(*args)
        if bold: text = f"**{text}**"
        if experimental: text = f"**[warning: experimental]** {text}"
        return self._add_to(self._last_added, "<:reply:1121924702756143234>*" + text + "*", add=True)

    def has(self, type: str, key: str) -> bool:
        key = self.bot.strings.get(f"{type}.{key}", key).replace("*", "")
        for string in self._messages[type]:
            string = str(string).split(" ", 1)[1].replace("*", "")
            pattern = re.escape(key).replace(r"\{\}", r".*")
            if re.match(pattern, string):
                return True
        return False

    def has_values(self) -> bool:
        return self.amount > 0

    def set_footer(self, s: str):
        self.footer = s
        return self

    def build(self) -> list[str]:
        messages = []
        index = 0
        for i in self._messages:
            for j in self._messages[i]:
                if "Re-Upload Log" in j and self.has("top_info", "uploaded_log"): continue
                add = j + "\n" + ("\n" if i == "top_info" and index == len(self._messages[i]) - 1 else "")
                if len(messages) == 0 or index % 9 == 0: messages.append(add)
                else: messages[len(messages) - 1] += add
                index += 1
        return messages

class IssueChecker:
    def __init__(self, bot: BackgroundPingu, log: Log, link: str, server_id: int) -> None:
        self.bot = bot
        self.log = log
        self.link = link
        self.server_id = server_id
        self.java_17_mods = [
            "areessgee",
            "peepopractice",
        ]
        self.outdated_java_17_mods = [
            "antiresourcereload-1.16.1-4.0.0",
        ]
        self.not_needed_java_17_mods = [
            "serversiderng",
        ]
        self.assume_as_latest = [
            "sodiummac",
            "krypton",
            "optifine",
            "sodium-extra",
            "biomethreadlocalfix",
            "sleepbackground-3.8-1.8.x-1.12.x",
            "tab-focus",
            "voyager",
            "forceport",
        ]
        self.assume_as_legal = [
            "mcsrranked",
            "mangodfps",
            "statsperreset",
        ]
        self.mcsr_mods = [
            "worldpreview",
            "anchiale",
            "sleepbackground",
            "StatsPerWorld",
            "z-buffer-fog",
            "tab-focus",
            "setspawn",
            "SpeedRunIGT",
            "standardsettings",
            "forceport",
            "lazystronghold",
            "antiresourcereload",
            "extra-options",
            "chunkcacher",
            "serverSideRNG",
            "peepopractice",
            "fast-reset",
            "antigone",
            "mcsrranked",
        ]
        self.general_mods = [
            "atum",
            "sodium",
            "lithium",
            "starlight",
            "krypton",
            "lazydfu",
            "dynamicfps",
            "voyager",
            "platifonia",
            "retino",
        ]
    
    def get_mod_metadata(self, mod_filename: str) -> dict:
        mod_filename = mod_filename.lower().replace("optifine", "optifabric")
        filename = mod_filename.replace(" ", "").replace("-", "").replace("+", "").replace("_", "")
        for mod in self.bot.mods:
            original_name = mod["name"].lower()
            mod_name = original_name.replace(" ", "").replace("-", "").replace("_", "")
            mod_name = "zbufferfog" if mod_name == "legacyplanarfog" else mod_name
            mod_name = "dynamicmenufps" if mod_name == "dynamicfps" else mod_name
            if mod_name.endswith("mod"): mod_name = mod_name[:-3]
            if mod_name in filename:
                return mod
        return None
    
    def get_latest_version(self, metadata: dict) -> bool:
        if self.log.minecraft_version is None: return None
        formatted_mc_version = self.log.minecraft_version
        if formatted_mc_version.count(".") == 1: formatted_mc_version += ".0"
        try: minecraft_version = semver.Version.parse(formatted_mc_version)
        except: return None
        latest_match = None
        for file_data in metadata["files"]:
            for game_version in file_data["game_versions"]:
                all_versions = game_version.split(" ")
                for version in all_versions:
                    try:
                        if minecraft_version.match(version):
                            latest_match = file_data
                            if str(minecraft_version) in version:
                                return latest_match
                    except ValueError: continue
        return latest_match

    def check(self) -> IssueBuilder:
        builder = IssueBuilder(self.bot, self.log)

        if self.log.has_pattern(r"^__PINGU__DOWNLOAD_ERROR__(\d+)__"):
            # when updating it, also update upload_button.disabled in views.py
            match = re.search(r"^__PINGU__DOWNLOAD_ERROR__(\d+)__", self.log._content)
            if not match is None: builder.error("failed_to_download_log", match.group(1))
            return builder

        is_mcsr_log = any(self.log.has_mod(mcsr_mod) for mcsr_mod in self.mcsr_mods) or self.log.minecraft_version == "1.16.1"
        found_crash_cause = False
        illegal_mods = []
        missing_mods = []
        checked_mods = {}
        outdated_mods = {}
        all_incompatible_mods = {}
        duplicate_mods = []
        footer = ""

        if self.log.operating_system == OperatingSystem.MACOS: footer += " MacOS"
        elif self.log.operating_system == OperatingSystem.LINUX: footer += " Linux"

        if not self.log.launcher is None: footer += f" {self.log.launcher.value}"
        
        if not self.log.minecraft_version is None: footer += f" {self.log.minecraft_version}"

        if self.log.is_ranked_log: footer += " Ranked"
        elif self.log.is_ssg_log: footer += " SSG"
        elif is_mcsr_log: footer += " RSG"
        elif not self.log.mod_loader is None: footer += f" {self.log.mod_loader.value}"
        
        if self.log.type in [
            LogType.HS_ERR_PID_LOG,
            LogType.CRASH_REPORT,
            LogType.THREAD_DUMP,
            LogType.LAUNCHER_LOG,
        ]: footer += f" {self.log.type.value}"
        elif self.log.type == LogType.LATEST_LOG:
            footer += " latest.log"
            if self.log.stacktrace or self.log.exitcode: footer += " crash"
        elif self.log.stacktrace or self.log.exitcode: footer += " crash"
        else: footer += " log"
        
        builder.set_footer(footer.strip())

        if self.log.leaked_session_id:
            builder.error("leaked_session_id_token")
        
        if self.log.leaked_pc_username:
            builder.info("leaked_username").add("upload_log_leaked_username")
            if self.log.lines > 25000: builder.add("upload_log_25k_lines")
        
        if is_mcsr_log:
            for mod in self.log.mods:
                metadata = self.get_mod_metadata(mod)
                if not metadata is None:
                    mod_name = metadata["name"]

                    try:
                        for incompatible_mod in metadata["incompatible"]:
                            if all_incompatible_mods[mod_name] is None:
                                all_incompatible_mods[mod_name] = [incompatible_mod]
                            else:
                                all_incompatible_mods[mod_name].append(incompatible_mod)
                    except KeyError: pass
                    
                    if mod_name.lower() in checked_mods and not mod_name.lower() == "optifabric":
                        duplicate_mods.append(mod_name)
                        if checked_mods[mod_name.lower()] and mod_name in outdated_mods:
                            outdated_mods.pop(mod_name)
                        else:
                            continue
                    
                    latest_version = self.get_latest_version(metadata)
                    if not latest_version is None and not (latest_version["name"] == mod or latest_version["version"].replace("+","").replace(" ","") in mod.replace("+","").replace(" ","")):
                        if all(not weird_mod in mod.lower() for weird_mod in self.assume_as_latest):
                            outdated_mods[mod_name] = latest_version["page"]
                            checked_mods[mod_name.lower()] = True
                    else: checked_mods[mod_name.lower()] = False
                elif all(not weird_mod in mod.lower() for weird_mod in self.assume_as_legal): illegal_mods.append(mod)
        
        if is_mcsr_log and len(self.log.whatever_mods) > 0:
            for recommended_mod in self.log.recommended_mods:
                if not self.log.has_mod(recommended_mod):
                    metadata = self.get_mod_metadata(recommended_mod)
                    latest_version = self.get_latest_version(metadata)
                    if latest_version is None: continue
                    missing_mods.append([recommended_mod, latest_version["page"]])
        
        if len(outdated_mods) + len(missing_mods) > 5:
            if len(missing_mods) == 0:
                builder.warning(
                    "outdated_mods",
                    len(outdated_mods),
                    "`, `".join([mod for mod in outdated_mods.keys()]),
                ).add("update_mods").add("modcheck_v1_warning")
            elif len(outdated_mods) == 0:
                builder.warning(
                    "missing_mods",
                    len(missing_mods),
                    "`, `".join([mod[0] for mod in missing_mods]),
                ).add("update_mods").add("modcheck_v1_warning")
            else:
                builder.warning(
                    "missing_and_outdated_mods",
                    len(missing_mods),
                    "s" if len(missing_mods) > 1 else "",
                    "`, `".join([mod[0] for mod in missing_mods]),
                    len(outdated_mods),
                    "s" if len(outdated_mods) > 1 else "",
                    "`, `".join([mod for mod in outdated_mods.keys()]),
                ).add("update_mods").add("modcheck_v1_warning")
        elif len(outdated_mods) + len(missing_mods) > 0:
            if len(outdated_mods) > 0:
                builder.note(
                    "outdated_mods_linked",
                    len(outdated_mods),
                    "s" if len(outdated_mods) > 1 else "",
                    "s" if len(outdated_mods) > 1 else "",
                    ", ".join(f"[**{name}**]({link})" for name, link in outdated_mods.items()),
                )
            if len(missing_mods) > 0:
                builder.warning(
                    "missing_mods_linked",
                    len(missing_mods),
                    "s" if len(missing_mods) > 1 else "",
                    "them" if len(missing_mods) > 1 else "it",
                    ", ".join(f"[**{name}**]({link})" for name, link in missing_mods),
                )
            builder.add("update_mods").add("modcheck_v1_warning")

        for key, value in all_incompatible_mods.items():
            for incompatible_mod in value:
                if self.log.has_mod(incompatible_mod):
                    builder.error("incompatible_mod", key, incompatible_mod)
        
        if len(duplicate_mods) > 0:
            builder.note("duplicate_mods", ", ".join(set(duplicate_mods)))
        
        if len(illegal_mods) > 0:
            if len(illegal_mods) > 6: temp = "s"
            elif len(illegal_mods) > 1: temp = f"s (`{', '.join(illegal_mods)}`)"
            else: temp = f" (`{illegal_mods[0]}`)"
            builder.note("amount_illegal_mods", len(illegal_mods), temp)

        if len(self.log.mods) == 0:
            for mod in self.log.fabric_mods:
                if any(weird_mod in mod.lower() for weird_mod in self.assume_as_legal): continue
                metadata = self.get_mod_metadata(mod)
                if metadata is None: illegal_mods.append(mod)
            if len(illegal_mods) > 0:
                if len(illegal_mods) > 6: temp = "s"
                elif len(illegal_mods) > 1: temp = f"s (`{', '.join(illegal_mods)}`)"
                else: temp = f" (`{illegal_mods[0]}`)"
                builder.note(
                    "amount_illegal_mods",
                    len(illegal_mods),
                    temp,
                    experimental = (self.log.minecraft_version != "1.16.1")
                )
        
        if self.log.operating_system == OperatingSystem.MACOS:
            if self.log.has_mod("sodium") and not self.log.has_mod("sodiummac"):
                builder.error("not_using_mac_sodium")
        
        wrong_not_needed_mods = []
        if not self.log.major_java_version is None and self.log.major_java_version < 17:
            wrong_mods = []
            wrong_outdated_mods = []

            for installed_mod in self.log.whatever_mods:
                for mod in self.java_17_mods:
                    if mod in installed_mod.lower():
                        wrong_mods.append(mod)
                for mod in self.outdated_java_17_mods:
                    if mod in installed_mod.lower():
                        wrong_outdated_mods.append(mod)
                for mod in self.not_needed_java_17_mods:
                    if mod in installed_mod.lower():
                        wrong_not_needed_mods.append(mod)
            
            if len(wrong_mods) > 0:
                wrong_mods += wrong_outdated_mods
                builder.error(
                    "need_java_17_mods",
                    "mods" if len(wrong_mods) > 1 else "a mod",
                    "`, `".join(wrong_mods),
                    "s" if len(wrong_mods) == 1 else "",
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                ).add(self.log.java_update_guide)
                if self.log.is_prism: builder.add("prism_java_compat_check")
                found_crash_cause = True
            elif len(wrong_outdated_mods) > 0:
                builder.error(
                    "need_java_17_outdated_mods",
                    "mods" if len(wrong_outdated_mods) > 1 else "a mod",
                    "`, `".join(wrong_outdated_mods),
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                    "it" if len(wrong_outdated_mods) == 1 else "them"
                ).add(self.log.java_update_guide)
                if self.log.is_prism: builder.add("prism_java_compat_check")
                found_crash_cause = True
        
        if not found_crash_cause:
            if self.log.has_pattern(r"require the use of Java 1(7|6)"):
                builder.error(
                    "need_new_java_mc",
                    17,
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                ).add("java_update_guide")
                found_crash_cause = True
            if (self.log.is_newer_than("1.20.5")
                and not self.log.major_java_version is None
                and self.log.major_java_version < 21
            ):
                builder.error(
                    "need_new_java_mc",
                    21,
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                ).add("java_update_guide")
                found_crash_cause = True
        
        if not found_crash_cause and len(wrong_not_needed_mods) == 0:
            needed_java_version = None
            if self.log.has_content("java.lang.UnsupportedClassVersionError"):
                match = re.compile(r"class file version (\d+\.\d+)").search(self.log._content)
                if not match is None:
                    needed_java_version = round(float(match.group(1))) - 44
            compatibility_match = re.compile(r"The requested compatibility level (JAVA_\d+) could not be set.").search(self.log._content)
            if not compatibility_match is None:
                try:
                    parsed_version = int(compatibility_match.group(1).split("_")[1])
                    if needed_java_version is None or parsed_version > needed_java_version:
                        needed_java_version = parsed_version
                except: pass
            if not needed_java_version is None:
                builder.error(
                    "need_new_java",
                    needed_java_version,
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                ).add(self.log.java_update_guide)
                if self.log.is_prism: builder.add("prism_java_compat_check")
                found_crash_cause = True
            elif self.log.has_content("java.lang.UnsupportedClassVersionError: net/minecraft/class_310"):
                builder.error(
                    "need_new_java",
                    17,
                    f", but you're using `Java {self.log.major_java_version}`" if not self.log.major_java_version is None else "",
                ).add("k4_setup_guide")
                found_crash_cause = True
        
        pattern = r"This instance is not compatible with Java version (\d+)\.\nPlease switch to one of the following Java versions for this instance:\nJava version (\d+)"
        match = re.search(pattern, self.log._content)
        if not found_crash_cause and not match is None:
            switch_java = False
            if self.log.is_newer_than("1.20.5"):
                try:
                    current_version = int(match.group(1))
                    switch_java = (current_version < 21)
                except: switch_java = True
            elif self.log.is_newer_than("1.17"):
                try:
                    current_version = int(match.group(1))
                    switch_java = (current_version < 17)
                except: switch_java = True
            elif self.log.mod_loader == ModLoader.FORGE: switch_java = True
            if switch_java:
                current_version = match.group(1)
                compatible_version = match.group(2)
                builder.error(
                    "incorrect_java_prism",
                    current_version,
                    compatible_version,
                    compatible_version,
                    " (download the `.msi` file)" if self.log.operating_system == OperatingSystem.WINDOWS else
                    " (download the `.pkg` file)" if self.log.operating_system == OperatingSystem.MACOS else
                    "",
                    compatible_version
                )
            else: builder.error("java_comp_check")
            found_crash_cause = True
        
        if not found_crash_cause and any(self.log.has_content(crash_32_bit_java) for crash_32_bit_java in [
            "Could not reserve enough space for ",
            "Invalid maximum heap size: "
        ]):
            builder.error("32_bit_java_crash").add(self.log.java_update_guide)
            if self.log.is_prism: builder.add("prism_java_compat_check")
            found_crash_cause = True
        
        if not found_crash_cause and (any(self.log.has_content(broken_java) for broken_java in [
            "Could not start java:\n\n\nCheck your ",
            "Incompatible magic value 0 in class file sun/security/provider/SunEntries",
            "Assertion `version->filename == NULL || ! _dl_name_match_p (version->filename, map)' failed"
        ]) or self.log.has_pattern(r"The java binary \"(.+)\" couldn't be found.")):
            builder.error("broken_java").add("java_update_guide")
            if self.log.is_prism: builder.add("prism_java_compat_check")
            found_crash_cause = True
        
        if self.log.has_content("The java binary \"\" couldn't be found."):
            if self.log.has_content("Please set up java in the settings."): # java isn't selected globally & no override
                builder.error("no_java").add("java_update_guide")
                if self.log.is_prism: builder.add("prism_java_compat_check")
            else: # java isn't selected in instance settings
                builder.error("no_java").add("java_update_guide").add("java_override_warning")
                if self.log.is_prism: builder.add("prism_java_compat_check")
            found_crash_cause = True
        
        if self.log.has_content("java.awt.AWTError: Assistive Technology not found: org.GNOME.Accessibility.AtkWrapper"):
            builder.error("headless_java")
            found_crash_cause = True
        
        if self.log.has_content("mcwrap.py"):
            if self.log.launcher is None or self.log.launcher == Launcher.MULTIMC or not self.log.has_content("mac-lwjgl-fix"):
                builder.error("m1_multimc_hack").add("mac_setup_guide")
        
        elif not found_crash_cause and any(self.log.has_pattern(using_32_bit_java) for using_32_bit_java in [
            r"You might want to install a 64bit Java version",
            r", using 32 \((.+)\) architecture, from"
        ]):
            if self.log.operating_system == OperatingSystem.MACOS:
                builder.error("arm_java_multimc").add("mac_setup_guide")
            else:
                builder.error("32_bit_java").add("java_update_guide")
            found_crash_cause = True
        
        if not found_crash_cause and is_mcsr_log and not self.log.major_java_version is None and self.log.major_java_version < 17:
            builder.note("not_using_java_17", self.log.major_java_version).add(self.log.java_update_guide)
            if self.log.is_prism: builder.add("prism_java_compat_check")

        if self.log.operating_system == OperatingSystem.MACOS and not self.log.has_content("32-bit architecture"):
            if self.log.launcher == Launcher.MULTIMC:
                builder.note("mac_use_prism").add("mac_setup_guide")
            elif self.log.is_prism and self.log.has_content("using 64 (x86_64) architecture"):
                builder.note("mac_use_arm_java")
                if not found_crash_cause: builder.add(self.log.java_update_guide).add("prism_java_compat_check")
        
        if (self.log.mod_loader in [ModLoader.FORGE, None]
            and any(self.log.has_content(delete_launcher_cache_crash) for delete_launcher_cache_crash in [
                "Caused by: java.lang.NoSuchMethodError: 'boolean net.minecraftforge.",
                "Unable to detect the forge installer!",
                "Reason:\nOne or more subtasks failed"
        ])):
            builder.error("delete_launcher_cache")

        if ((self.log.is_newer_than("1.20") or not self.log.is_newer_than("1.1"))
            and self.log.has_content("[LWJGL] Failed to load a library. Possible solutions:") # so it works on snapshots too
        ):
            if self.log.launcher == Launcher.MULTIMC:
                builder.error("update_mmc")
                found_crash_cause = True
            else:
                builder.error("update_mmc", experimental=True)
        
        if self.log.has_content("[LWJGL] Platform/architecture mismatch detected for module: org.lwjgl"):
            builder.error("try_changing_lwjgl_version", self.log.edit_instance)
        
        if self.log.has_content("(Silent Mode)"):
            builder.error("try_changing_lwjgl_version", self.log.edit_instance, experimental=True)
        
        if any(self.log.has_content(new_java_old_fabric) for new_java_old_fabric in [
            "java.lang.IllegalArgumentException: Unsupported class file major version ",
            "java.lang.IllegalArgumentException: Class file major version "
        ]):
            mod_loader = self.log.mod_loader.value if self.log.mod_loader.value is not None else "mod"
            builder.error("new_java_old_fabric_crash", mod_loader, mod_loader)
            if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
            found_crash_cause = True
            
        elif any(self.log.has_content(crash) for crash in [
            "java.lang.ClassNotFoundException: can't find class com.llamalad7.mixinextras",
            "java.lang.ClassNotFoundException: com.llamalad7.mixinextras",
            "java.lang.NoClassDefFoundError: com/redlimerl/speedrunigt",
        ]):
            builder.error("old_fabric_crash").add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
            found_crash_cause = True
        
        elif not self.log.fabric_version is None:
            highest_srigt_ver = None
            for mod in self.log.mods:
                if "speedrunigt" in mod.lower():
                    match = re.compile(r"-(\d+(?:\.\d+)?)\+").search(mod)
                    if not match is None:
                        try: ver = version.parse(match.group(1))
                        except: pass
                        if highest_srigt_ver is None or ver > highest_srigt_ver:
                            highest_srigt_ver = ver
            if not highest_srigt_ver is None and highest_srigt_ver < version.parse("13.3") and self.log.fabric_version > version.parse("0.14.14"):
                builder.error("incompatible_srigt")
                found_crash_cause = True
            
            if self.log.fabric_version.__str__() in ["0.14.15", "0.14.16"]:
                builder.error("broken_fabric")
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
            elif self.log.fabric_version < version.parse("0.13.3"):
                builder.error("really_old_fabric")
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
            elif self.log.fabric_version < version.parse("0.14.14"):
                builder.warning("relatively_old_fabric")
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
            elif self.log.fabric_version < version.parse("0.15.0"):
                builder.note("old_fabric")
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "update")
        
        if len(self.log.mods) == 0 and self.log.has_content(".mrpack\n"):
            builder.error("using_modpack_as_mod", self.log.launcher.value if self.log.launcher is not None else "your launcher")

        if len(self.log.mods) > 0 and self.log.mod_loader == ModLoader.VANILLA:
            if any(self.log.has_library(loader) for loader in ["forge", "fabric", "quilt"]):
                builder.error("broken_loader", self.log.edit_instance)
            else:
                builder.error("no_loader")
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "install")
        
        if not self.log.mod_loader in [None, ModLoader.FABRIC, ModLoader.VANILLA]:
            if is_mcsr_log:
                builder.error("using_other_loader_mcsr", self.log.mod_loader.value)
                if self.log.is_newer_than("1.14"): builder.add("fabric_guide_prism" if self.log.is_prism else "fabric_guide_mmc", "install")
                found_crash_cause = True
            else:
                builder.note("using_other_loader", self.log.mod_loader.value)
        
        if not found_crash_cause:
            has_fabric_mod = any(self.log.has_mod(mcsr_mod) for mcsr_mod in self.mcsr_mods) or self.log.has_mod("fabric")
            has_quilt_mod = self.log.has_mod("quilt")
            has_forge_mod = self.log.has_mod("forge")
            
            if has_forge_mod and not has_quilt_mod and not has_fabric_mod:
                if self.log.mod_loader == ModLoader.FABRIC:
                    builder.error("rong_modloader", "Forge", "Fabric")
                    found_crash_cause = True
                elif self.log.mod_loader == ModLoader.QUILT:
                    builder.error("rong_modloader", "Forge", "Quilt")
                    found_crash_cause = True
            elif has_fabric_mod and not has_forge_mod and self.log.mod_loader == ModLoader.FORGE:
                builder.error("rong_modloader", "Fabric", "Forge")
                found_crash_cause = True
            elif has_quilt_mod and not has_forge_mod and self.log.mod_loader == ModLoader.FORGE:
                builder.error("rong_modloader", "Quilt", "Forge")
                found_crash_cause = True
        
        all_modloaders = [
            "fabric-loader",
            ModLoader.FORGE.value,
            "quilt-loader",
        ]
        found_modloaders = [modloader for modloader in all_modloaders if self.log.has_library(modloader)]
        if len(found_modloaders) > 1:
            builder.error("multiple_modloaders", "`, `".join(found_modloaders), self.log.edit_instance)
            found_crash_cause = True

        if not self.log.max_allocated is None:
            min_limit_0, min_limit_1, min_limit_2 = self.log.recommended_min_allocated
            if self.log.has_content("java.lang.OutOfMemoryError"):
                builder.error("too_little_ram_crash").add(*self.log.ram_guide)
                found_crash_cause = True
            elif self.log.max_allocated < min_limit_1 and self.log.has_content(" -805306369") and self.log.stacktrace is None:
                builder.error("too_little_ram_crash", experimental=True).add(*self.log.ram_guide)
            elif self.log.max_allocated < min_limit_0 and self.log.has_content(" -805306369") and self.log.stacktrace is None:
                builder.note("too_little_ram_crash", experimental=True).add(*self.log.ram_guide)
            elif self.log.max_allocated < min_limit_2:
                builder.warning("too_little_ram").add(*self.log.ram_guide)
            elif self.log.max_allocated < min_limit_1:
                builder.note("too_little_ram").add(*self.log.ram_guide)
            if is_mcsr_log and not self.log.is_newer_than("1.18"):
                max_limit_0, max_limit_1, max_limit_2 = self.log.recommended_max_allocated
                if self.log.max_allocated > max_limit_0:
                    builder.error("too_much_ram").add(*self.log.ram_guide)
                elif self.log.max_allocated > max_limit_1:
                    builder.warning("too_much_ram").add(*self.log.ram_guide)
                elif self.log.max_allocated > max_limit_2:
                    builder.note("too_much_ram").add(*self.log.ram_guide)
        elif self.log.has_content("OutOfMemoryError"):
            builder.error("too_little_ram_crash").add(*self.log.ram_guide)
            found_crash_cause = True

        if self.log.has_content("There is not enough space on the disk"):
            builder.error("out_of_disk_space")
            found_crash_cause = True
        elif not found_crash_cause and self.log.has_content("Failed to store chunk"):
            builder.note("out_of_disk_space", experimental=True)
        
        if any(self.log.has_pattern(out_of_memory_on_pc) for out_of_memory_on_pc in [
            r"There is insufficient memory for the Java Runtime Environment to continue",
            r"GL_OUT_OF_MEMORY",
            r"memory allocation (.*) failed",
        ]):
            builder.error("out_of_memory_pc", experimental=True)
            found_crash_cause = True

        if self.log.has_mod("phosphor") and not self.log.minecraft_version == "1.12.2":
            builder.note("starlight_better")
            metadata = self.get_mod_metadata("starlight")
            if not metadata is None:
                latest_version = self.get_latest_version(metadata)
                if not latest_version is None:
                    builder.add("mod_download", metadata["name"], latest_version["page"])
        
        if self.log.has_content("Failed to download the assets index"):
            builder.error("assets_index_fail")
        
        if self.log.has_content("NSWindow drag regions should only be invalidated on the Main Thread"):
            builder.error("mac_too_new_java")
        
        if self.log.has_content("Pixel format not accelerated"):
            builder.error("gl_pixel_format")
        
        if self.log.has_pattern(r"  \[(ig[0-9]+icd[0-9]+\.dll)[+ ](0x[0-9a-f]+)\]"):
            if self.log.has_content("speedrunigt") or self.log.has_mod("mcsrranked"):
                builder.error("eav_crash", experimental=True).add("eav_crash_srigt")
            else:
                builder.error("gl_pixel_format")
            if self.log.stacktrace is None: found_crash_cause = True
        
        elif (len(self.log.whatever_mods) == 0 or self.log.has_mod("xaero")) and self.log.has_content("Field too big for insn"):
            wrong_mods = [mod for mod in self.log.whatever_mods if "xaero" in mod.lower()]
            if len(wrong_mods) == 1: wrong_mods == ["xaero"]
            builder.error("mods_crash", "; ".join(wrong_mods))
            found_crash_cause = True
        
        elif (not found_crash_cause
            and self.log.stacktrace is None
            and (self.log.has_content("A fatal error has been detected by the Java Runtime Environment") or self.log.has_content("EXCEPTION_ACCESS_VIOLATION"))
        ):
            builder.error("eav_crash", experimental=True)
            if self.log.has_pattern(r"  \[ntdll\.dll\+(0x[0-9a-f]+)\]"):
                builder.add("eav_crash_1", bold=True)
                builder.add("eav_crash_1.1", bold=True)
                builder.add("eav_crash_1.2", bold=True)
                builder.add("eav_crash_1.3", bold=True)
            else:
                builder.add("eav_crash_1")
                builder.add("eav_crash_1.1")
                builder.add("eav_crash_1.2")
                builder.add("eav_crash_1.3")
            builder.add("eav_crash_2")
            builder.add("eav_crash_3")
            if ((len(self.log.whatever_mods) == 0 or self.log.has_mod("speedrunigt") or self.log.has_mod("mcsrranked"))
                and self.log.operating_system != OperatingSystem.MACOS
            ): builder.add("eav_crash_srigt")
            builder.add("eav_crash_disclaimer")
            if self.log.stacktrace is None: found_crash_cause = True
        
        if self.log.has_content("WGL_ARB_create_context_profile is unavailable"):
            builder.error("intel_hd2000").add("intell_hd2000_info")

        if self.log.has_content("org.lwjgl.LWJGLException: Could not choose GLX13 config") or self.log.has_content("GLFW error 65545: GLX: Failed to find a suitable GLXFBConfig"):
            builder.error("outdated_nvidia_flatpack_driver", experimental=True)
        
        if self.log.has_content("java.lang.NoSuchMethodError: sun.security.util.ManifestEntryVerifier.<init>(Ljava/util/jar/Manifest;)V"):
            builder.error("forge_java_bug")
            found_crash_cause = True
        
        if self.log.has_content("java.lang.IllegalStateException: GLFW error before init: [0x10008]Cocoa: Failed to find service port for display"):
            builder.error("incompatible_forge_mac")
            found_crash_cause = True
        
        system_libs = [lib for lib in ["GLFW", "OpenAL"] if self.log.has_content("Using system " + lib)]
        system_arg = None
        if len(system_libs) == 2: system_arg = f"{system_libs[0]} and {system_libs[1]} installations"
        elif len(system_libs) == 1: system_arg = f"{system_libs[0]} installation"
        if not system_arg is None:
            if self.log.has_content("Failed to locate library:"):
                builder.error("builtin_lib_crash",
                              system_arg,
                              self.log.launcher.value if self.log.launcher is not None else "your launcher",
                              " > Tweaks" if self.log.is_prism else "")
                found_crash_cause = True
            elif any(self.log.has_content_in_stacktrace(lib) for lib in ["GLFW", "OpenAL"]):
                builder.warning("builtin_lib_recommendation", system_arg)

        required_mod_match = re.findall(r"requires (.*?) of (\w+),", self.log._content)
        for required_mod in required_mod_match:
            mod_name = required_mod[1]
            if mod_name.lower() == "fabric": builder.error("requires_fabric_api")
            else: builder.error("requires_mod", mod_name)
        
        if is_mcsr_log and self.log.has_mod("fabric-api"):
            builder.warning("using_fabric_api")
        
        if self.log.has_content("Couldn't extract native jar"):
            builder.error("locked_libs")
            found_crash_cause = True
        
        if self.log.has_pattern(r"java\.io\.IOException: Directory \'(.+?)\' could not be created"):
            builder.error("try_admin_launch")
        
        if self.log.has_content("java.lang.NullPointerException: Cannot invoke \"net.minecraft.class_2680.method_26213()\" because \"state\" is null"):
            builder.error("old_sodium_crash")
            metadata = self.get_mod_metadata("sodium")
            if not metadata is None:
                latest_version = self.get_latest_version(metadata)
                if not latest_version is None:
                    builder.add("mod_download", metadata["name"], latest_version["page"])
            found_crash_cause = True
        elif self.log.has_content("me.jellysquid.mods.sodium.client.SodiumClientMod.options"):
            builder.error("sodium_config_crash")
            found_crash_cause = True
        
        if self.log.has_content_in_stacktrace("me.voidxwalker.options.extra.ExtraOptions.lambda$load"):
            builder.error("corrupted_mod_config", "extra-options")
            found_crash_cause = True
        
        pattern = r"Uncaught exception in thread \"Thread-\d+\"\njava\.util\.ConcurrentModificationException: null"
        if "java.util.ConcurrentModificationException" in re.sub(pattern, "", self.log._content):
            if self.log.short_version == "1.16" and not self.log.has_mod("voyager"):
                builder.error("no_voyager_crash")
            elif self.log.has_content("[SEVERE] [ForgeModLoader] Unable to launch") and not self.log.has_mod("legacyjavafixer"):
                builder.error("legacyjavafixer")
        
        if self.log.has_content("java.lang.IllegalStateException: Adding Entity listener a second time") and self.log.has_content("me.jellysquid.mods.lithium.common.entity.tracker.nearby"):
            builder.error("lithium_crash")
            found_crash_cause = True
        
        if any(self.log.has_content_in_stacktrace(f"at net.minecraft.class_{i}") for i in ["507", "513"]):
            builder.error("recipe_book_crash", experimental=True)
            # found_crash_cause = True
        
        if is_mcsr_log and any(self.log.has_content(snowman_crash) for snowman_crash in [
            "Cannot invoke \"net.minecraft.class_1657.method_7325()\"",
            "Cannot invoke \"net.minecraft.class_4184.method_19326()\"",
        ]):
            builder.error("snowman_crash")
            found_crash_cause = True
        
        if is_mcsr_log and not found_crash_cause and self.log.has_content("because \"☃\" is null"):
            builder.error("snowman_crash", experimental=True)
        
        if self.log.has_content("Cannot invoke \"net.minecraft.class_1170.method_3833()\" because the return value of \"net.minecraft.class_1170.method_6428(int)\" is null"):
            builder.error("invalid_biome_id_crash")
            found_crash_cause = True
        
        if self.log.has_pattern(r"Description: Exception in server tick loop[\s\n]*java\.lang\.IllegalStateException: Lock is no longer valid"):
            builder.error("wp_3_plus_crash")
            found_crash_cause = True
            metadata = self.get_mod_metadata("worldpreview")
            if not metadata is None:
                latest_version = self.get_latest_version(metadata)
                if not latest_version is None:
                    builder.add("mod_download", metadata["name"], latest_version["page"])
            found_crash_cause = True
        
        if is_mcsr_log and any(self.log.has_content(log_spam) for log_spam in [
            "Using missing texture, unable to load",
            "Exception loading blockstate definition",
            "Unable to load model",
            "java.lang.NullPointerException: Cannot invoke \"com.mojang.authlib.minecraft.MinecraftProfileTexture.getHash()\" because \"?\" is null",
            " to profiler if profiler tick hasn't started - missing "
        ]): builder.info("log_spam")

        if self.log.has_content("Launched instance in offline mode") and self.log.has_content("(missing)\n"):
            builder.error("online_launch_required", self.log.edit_instance)
            found_crash_cause = True
        
        if self.log.has_content("ClassLoaders$AppClassLoader cannot be cast to class java.net.URLClassLoader"):
            builder.error("forge_too_new_java")
            found_crash_cause = True
        
        if any(self.log.has_content(sodium_rtss_crash) for sodium_rtss_crash in [
            "RivaTuner Statistics Server (RTSS) is not compatible with Sodium",
            "READ ME! You appear to be using the RivaTuner Statistics Server (RTSS)!"
        ]):
            builder.error("sodium_rtss")
            found_crash_cause = True
        
        if self.log.has_mod("mcsrranked-1") or self.log.has_mod("mcsrranked-2") or self.log.has_mod("mcsrranked-3.1.jar"):
            builder.error("old_mod_version", "MCSR Ranked", "https://modrinth.com/mod/mcsr-ranked/versions/")
            if self.log.is_prism: builder.add("update_mods_prism")

        if self.log.has_mod("peepopractice-1") or self.log.has_mod("peepopractice-2.0"):
            builder.error("old_mod_version", "PeepoPractice", "https://github.com/faluhub/peepoPractice/releases/latest/")

        if self.log.has_pattern(r"^Prism Launcher version: [1-7]"):
            if self.log.has_pattern(r"^Prism Launcher version: [8-8]"):
                builder.note("semi_old_prism_version")
            else:
                builder.note("old_prism_version")
                if self.log.has_content("AppData/Roaming/PrismLauncher"): builder.add("update_prism_installer")

        match = re.search(r"MultiMC version: 0\.7\.0-(.{4})", self.log._content)
        if not match is None and self.log.operating_system == OperatingSystem.WINDOWS:
            if match.group(1) < "3863" or match.group(1) == "stab":
                builder.note("semi_old_mmc_version")

        match = re.search(r"Incompatible mod set found! READ THE BELOW LINES!(.*?$)", self.log._content, re.DOTALL)
        if not match is None:
            found_crash_cause = True
            ranked_rong_files = []
            ranked_rong_mods = []
            ranked_rong_versions = []
            ranked_anticheat = match.group(1).strip().replace("\t","")

            if self.log.has_pattern(r"You should delete these from Minecraft.\s*?Process "):
                builder.error("ranked_fabric_0_15_x")
            
            ranked_anticheat_split = ranked_anticheat.split("These Fabric Mods are whitelisted but different version! Make sure to update these!")
            if len(ranked_anticheat_split) > 1:
                ranked_anticheat, ranked_anticheat_split = ranked_anticheat_split[0], ranked_anticheat_split[1].split("\n")
                for mod in ranked_anticheat_split:
                    match = re.search(r"\[(.*?)\]", mod)
                    if match:
                        ranked_rong_versions.append(match.group(1))
            
            ranked_anticheat_split = ranked_anticheat.split("These Fabric Mods are whitelisted and you seem to be using the correct version but the files do not match. Try downloading these files again!")
            if len(ranked_anticheat_split) > 1:
                ranked_anticheat, ranked_anticheat_split = ranked_anticheat_split[0], ranked_anticheat_split[1].split("\n")
                for mod in ranked_anticheat_split:
                    match = re.search(r"\[(.*?)\]", mod)
                    if match:
                        ranked_rong_files.append(match.group(1))
            
            ranked_anticheat_split = ranked_anticheat.split("These Fabric Mods are not whitelisted! You should delete these from Minecraft.")
            if len(ranked_anticheat_split) > 1:
                ranked_anticheat, ranked_anticheat_split = ranked_anticheat_split[0], ranked_anticheat_split[1].split("\n")
                for mod in ranked_anticheat_split:
                    match = re.search(r"\[(.*?)\]", mod)
                    if match:
                        match = match.group(1)
                        ranked_rong_mods.append("Fabric API" if match == "fabric" else match)

            if len(ranked_rong_versions) > 5:
                builder.error("ranked_rong_versions", f"`{len(ranked_rong_versions)}` mods (`{ranked_rong_versions[0]}, {ranked_rong_versions[1]}, ...`) that are", "them").add("update_mods_ranked").add("modcheck_v1_warning")
            elif len(ranked_rong_versions) > 1:
                builder.error("ranked_rong_versions", f"`{len(ranked_rong_versions)}` mods (`{', '.join(ranked_rong_versions)}`) that are", "them").add("update_mods_ranked").add("modcheck_v1_warning")
            elif len(ranked_rong_versions) > 0:
                builder.error("ranked_rong_versions", f"a mod `{ranked_rong_versions[0]}` that is", "it").add("update_mods_ranked").add("modcheck_v1_warning")

            if len(ranked_rong_files) > 5:
                builder.error("ranked_rong_files", f"`{len(ranked_rong_files)}` mods (`{ranked_rong_files[0]}, {ranked_rong_files[1]}, ...`) that seem", "them").add("update_mods_ranked").add("modcheck_v1_warning")
            elif len(ranked_rong_files) > 1:
                builder.error("ranked_rong_files", f"`{len(ranked_rong_files)}` mods (`{', '.join(ranked_rong_files)}`) that seem", "them").add("update_mods_ranked").add("modcheck_v1_warning")
            elif len(ranked_rong_files) > 0:
                builder.error("ranked_rong_files", f"a mod `{ranked_rong_files[0]}` that seems", "it").add("update_mods_ranked").add("modcheck_v1_warning")

            if len(ranked_rong_mods) > 5:
                builder.error("ranked_rong_mods", f"`{len(ranked_rong_mods)}` mods (`{ranked_rong_mods[0]}, {ranked_rong_mods[1]}, ...`) that are", "them")
            elif len(ranked_rong_mods) > 1:
                builder.error("ranked_rong_mods", f"`{len(ranked_rong_mods)}` mods (`{', '.join(ranked_rong_mods)}`) that are", "them")
            elif len(ranked_rong_mods) > 0:
                builder.error("ranked_rong_mods", f"a mod `{ranked_rong_mods[0]}` that is", "it")
        
        if self.log.has_mod("optifine"):
            for incompatible_mod in ["WorldPreview", "Starlight"]:
                if self.log.has_mod(incompatible_mod):
                    builder.error("incompatible_mod", "Optifine", incompatible_mod)
                    found_crash_cause = True
            if self.log.has_mod("z-buffer-fog") and self.log.is_newer_than("1.14"):
                builder.error("incompatible_mod", "Optifine", "z-buffer-fog")
                found_crash_cause = True
            if self.log.is_newer_than("1.15"):
                if is_mcsr_log:
                    builder.error("use_sodium_not_optifine_mcsr").add("update_mods").add("modcheck_v1_warning")
                elif self.log.mod_loader == ModLoader.FORGE:
                    builder.error("use_sodium_not_optifine", "Embeddium").add("optifine_alternatives")
                else:
                    builder.error("use_sodium_not_optifine", "Sodium").add("optifine_alternatives")
        
        if self.log.has_mod("esimod"):
            for incompatible_mod in ["serverSideRNG", "SpeedRunIGT", "WorldPreview", "mcsrranked"]:
                if self.log.has_mod(incompatible_mod):
                    builder.error("incompatible_mod", "esimod", incompatible_mod)
        
        if self.log.has_mod("PeepoPractice"):
            for incompatible_mod in ["WorldPreview", "Atum"]:
                if self.log.has_mod(incompatible_mod):
                    builder.error("incompatible_mod", "PeepoPractice", incompatible_mod)
                    found_crash_cause = True

        if self.log.has_content("Mixin apply for mod areessgee failed areessgee.mixins.json:nether.StructureFeatureMixin from mod areessgee -> net.minecraft.class_3195"):
            builder.error("incompatible_mod", "AreEssGee", "PeepoPractice")
            found_crash_cause = True
        
        if self.log.has_mod("speedrunigt") and self.log.has_mod("stronghold-trainer"):
            builder.error("incompatible_mod", "SpeedRunIGT", "Stronghold Trainer")
            found_crash_cause = True
        
        if self.log.has_normal_mod("continuity") and self.log.has_mod("sodium") and not self.log.has_mod("indium"):
            builder.error("missing_dependency", "continuity", "indium")
            if self.log.has_content("Cannot invoke \"net.fabricmc.fabric.api.renderer.v1.Renderer.meshBuilder()\""):
                found_crash_cause = True
        elif self.log.has_content("Cannot invoke \"net.fabricmc.fabric.api.renderer.v1.Renderer.meshBuilder()\""):
            builder.error("missing_dependency_2", "indium")
            found_crash_cause = True
        
        if self.log.has_mod("worldpreview") and self.log.has_mod("carpet"):
            builder.error("incompatible_mod", "WorldPreview", "carpet")
            found_crash_cause = True
        
        if self.log.has_content("java.lang.ClassNotFoundException: dev.tildejustin.stateoutput.State"):
            builder.error("old_wp_with_stateoutput")
            found_crash_cause = True
        
        if not found_crash_cause and self.log.has_content("java.lang.StackOverflowError") and self.log.has_content("$atum$createDesiredWorld"):
            builder.error("stack_overflow_crash")
            found_crash_cause = True
        
        if self.log.has_content("Mappings not present!"):
            if not self.log.is_newer_than("1.14") and self.log.mod_loader == ModLoader.FABRIC:
                builder.error("legacy_fabric_modpack")
                found_crash_cause = True
            else:
                builder.warning("no_mappings", self.log.edit_instance, experimental=True)

        if (not self.log.loader_mc_version is None
            and not self.log.minecraft_version is None
            and self.log.minecraft_version != self.log.loader_mc_version
        ):
            builder.error(
                "minecraft_version_mismatch",
                "Forge" if self.log.mod_loader == ModLoader.FORGE else "Intermediary Mappings",
                self.log.edit_instance,
            )
            found_crash_cause = True
        
        if not found_crash_cause and self.log.has_content("ERROR]: Mixin apply for mod fabric-networking-api-v1 failed"):
            builder.error("delete_dot_fabric")
        
        if not found_crash_cause and self.log.has_content("com.google.gson.stream.MalformedJsonException"):
            pattern = r"due to errors, provided by '([\w\-+]+)'"
            match = re.search(pattern, self.log._content)
            if not match is None:
                mod_name = match.group(1)
                wrong_mod = [mod for mod in self.log.whatever_mods if mod_name.lower() in mod.lower()]
                if len(wrong_mod) > 0: wrong_mod = wrong_mod[0]
                else: wrong_mod = mod_name
                builder.error("corrupted_mod_config", wrong_mod)
                found_crash_cause = True
        pattern = r"Error analyzing \[(.*?)\]: java\.util\.zip\.ZipException: zip END header not found"
        match = re.search(pattern, self.log._content)
        if not match is None:
            builder.error("corrupted_file", match.group(1))
        
        if self.log.has_mod("serversiderng"):
            builder.error("using_ssrng").add("modcheck_v1_warning")
        
        if all(self.log.has_content(text) for text in [
            "net.minecraft.class_148: Feature placement",
            "java.lang.ArrayIndexOutOfBoundsException",
            "StarLightInterface"
        ]):
            builder.error("starlight_crash")
            found_crash_cause = True
        
        if not found_crash_cause:
            total = 0
            maxfps_0_indicators = [
                "########## GL ERROR ##########",
                "java.lang.ArithmeticException: / by zero",
                "at net.minecraft.class_3928.method_25394",
                " -805306369",
            ]

            for indicator in maxfps_0_indicators:
                if self.log.has_content(indicator): total += 1
            if total >= 2:
                builder.error("exitcode_805306369")
                found_crash_cause = True

        if (not found_crash_cause and self.log.stacktrace is None and self.log.exitcode == -1073741819
            or self.log.has_content("The instruction at 0x%p referenced memory at 0x%p. The memory could not be %s.")
        ):
            builder.error("exitcode", "-1073741819", experimental=True)
            builder.add("eav_crash_1").add("eav_crash_1.1").add("eav_crash_1.2").add("eav_crash_1.3")
            builder.add("exitcode_1073741819_2")
            if self.log.lines < 500:
                if self.log.has_mod("sodium") and not self.log.has_mod("sodiummac"): builder.add(f"exitcode_1073741819_3")
                builder.add(f"exitcode_1073741819_4")
            builder.add("exitcode_1073741819_5").add("exitcode_1073741819_1")

        if not found_crash_cause and self.log.stacktrace is None and self.log.exitcode == -1073740791:
            builder.error("exitcode", "-1073740791", experimental=True)
            builder.add("eav_crash_1").add("eav_crash_1.1").add("eav_crash_1.2").add("eav_crash_1.3")
            builder.add("exitcode_1073741819_2")
            if self.log.lines < 500: builder.add("exitcode_1073741819_4")
            builder.add("exitcode_1073741819_5")

        if not found_crash_cause and self.log.stacktrace is None and self.log.exitcode == -1073740771:
            builder.error("exitcode", "-1073740771", experimental=True)
            builder.add("eav_crash_1").add("eav_crash_1.1").add("eav_crash_1.2").add("eav_crash_1.3")
            builder.add("exitcode_1073741819_2")
            if self.log.lines < 500: builder.add("exitcode_1073741819_4")
            builder.add("exitcode_1073741819_5")
        
        if not self.log.minecraft_folder is None:
            if not found_crash_cause and "OneDrive" in self.log.minecraft_folder:
                builder.note("onedrive")
            if "C:/Program Files" in self.log.minecraft_folder:
                builder.note("program_files")
            if "Rar$" in self.log.minecraft_folder:
                builder.error("need_to_extract_from_zip", self.log.launcher.value if not self.log.launcher is None else "the launcher")

        if self.log.lines == 25000:
            builder.error("mclogs_cutoff")
        
        try:
            if self.log._content.splitlines()[-1].startswith("[23:5"):
                builder.error("midnight_bug") # for the first log part
        except IndexError: pass
        
        if self.log.has_pattern(r"^\[00:") and not self.log.has_content("Setting user:"):
            builder.error("midnight_bug") # for the second log part
        
        if (not found_crash_cause
            and any(self.link.endswith(file_extension) for file_extension in [".log", ".txt", ".tdump"])
            and self.log.has_content("minecraft")
            and not self.log.lines > 25000
        ):
            builder.info("upload_log_attachment")

        if self.log.has_content("Missing or unsupported mandatory dependencies"):
            builder.error("forge_missing_dependencies")
            found_crash_cause = True
        
        if (not found_crash_cause and self.log.is_multimc_or_fork
            and not self.log.type in [LogType.FULL_LOG, LogType.THREAD_DUMP, LogType.LAUNCHER_LOG]
        ):
            builder.info("send_full_log", self.log.launcher.value, self.log.edit_instance)

        pattern = r"\[Integrated Watchdog/ERROR\]:? This crash report has been saved to: (.*\.txt)"
        match = re.search(pattern, self.log._content)
        if not match is None:
            builder.info("send_watchdog_report", match.group(1))
            found_crash_cause = True

        if not found_crash_cause and self.log.has_content_in_stacktrace("atum"):
            if self.log.has_mod("autoresetter"):
                builder.error("downgrade_atum")
                found_crash_cause = True
            elif self.log.has_mod("beachfilter"):
                builder.error("old_mod_crash", "beachfilter", "https://github.com/DuncanRuns/BeachFilter-Mod/releases/latest/")
                found_crash_cause = True
            elif self.log.has_mod("fsg-wrapper-mod"):
                builder.error("old_mod_crash", "fsg wrapper", "https://github.com/DuncanRuns/FSG-Wrapper-Mod/releases/latest/")
                found_crash_cause = True
            elif self.log.has_content("java.lang.ClassNotFoundException: me.voidxwalker.autoreset.Atum"):
                builder.error(
                    "downgrade_atum",
                    experimental=(self.log.minecraft_version != "1.16.1")
                )
                found_crash_cause = True

        if not found_crash_cause:
            wrong_mods = []
            for pattern in [
                r"ERROR]: Mixin apply for mod ([\w\-+]+) failed",
                r"from mod ([\w\-+]+) failed injection check",
                r"due to errors, provided by '([\w\-+]+)'"
            ]:
                match = re.search(pattern, self.log._content)
                if not match is None:
                    mod_name = match.group(1)
                    wrong_mod = [mod for mod in self.log.whatever_mods if mod_name.lower() in mod.lower()]
                    if len(wrong_mod) > 0: wrong_mods += wrong_mod
                    else: wrong_mods.append(mod_name)

            if not self.log.stacktrace is None:
                if len(self.log.whatever_mods) == 0:
                    for mod in self.mcsr_mods + self.general_mods:
                        if mod.replace("-", "").lower() in self.log.stacktrace and not mod in wrong_mods and not mod.lower() in wrong_mods:
                            wrong_mods.append(mod)
                else:
                    for mod in self.log.whatever_mods:
                        mod_name = mod.lower().replace(".jar", "")
                        if not self.log.minecraft_version is None: mod_name = mod_name.replace(self.log.minecraft_version, "")
                        for c in ["+", "_", "=", ",", " "]: mod_name = mod_name.replace(c, "-")
                        mod_name_parts = mod_name.split("-")
                        mod_name = ""
                        for part in mod_name_parts:
                            part0 = part
                            for c in [
                                "fabric", "forge", "quilt",
                                "mod", "backport", "snapshot",
                                "build", "prism", "minecraft",
                                ".", "v", "mc",
                            ]:
                                part = part.replace(c, "")
                            for c in range(10): part = part.replace(str(c), "")
                            if part == "": break
                            elif len(part) > 1: mod_name += part0
                        if len(mod_name) < 5 and mod_name != "atum": mod_name = f".{mod_name}"
                        if len(mod_name) > 2 and mod_name in self.log.stacktrace:
                            if not mod in wrong_mods: wrong_mods.append(mod)
            
            if any(mayasmod in " ".join(wrong_mods) for mayasmod in [
                "peepopractice",
                "areessgee",
            ]) and self.server_id != 1070838405925179392:
                builder.error(
                    "mayas_mod_crash",
                    "s" if len(wrong_mods) > 1 else "",
                    "; ".join(wrong_mods[:12]),
                    "" if len(wrong_mods) > 1 else "s",
                )
            elif "ranked" in " ".join(wrong_mods) and self.server_id != 1056779246728658984:
                builder.error(
                    "ranked_mod_crash",
                    "s" if len(wrong_mods) > 1 else "",
                    "; ".join(wrong_mods[:12]),
                    "" if len(wrong_mods) > 1 else "s",
                )
            elif len(wrong_mods) == 1:
                builder.error("mod_crash", wrong_mods[0])
            elif len(wrong_mods) > 0 and len(wrong_mods) < 10:
                builder.error("mods_crash", "; ".join(wrong_mods))
        
        
        if self.link == "message":
            if self.log.has_pattern(r"-\s*1"):
                entity_culling_indicators = {
                    "entit": 2,
                    "F3": 1,
                    r"\be\b": 1,
                    "counter": 1
                }
                total = 0
                for pattern, value in entity_culling_indicators.items():
                    if self.log.has_pattern(pattern):
                        total += value
                if total >= 2: builder.error("entity_culling")
            
            if not found_crash_cause and any(self.log.has_content(crash) for crash in [
                "Process exited with code ",
                "Process crashed with exitcode ",
                "Process crashed with exit code ",
            ]):
                builder.error("send_full_log", self.log.edit_instance)
            
            pattern = r"https://minecraft\.fandom\.com/wiki/([A-Za-z0-9_]+)"
            for match in re.findall(pattern, self.log._content):
                if match.endswith("_"): match = match[:-1] # if someone uses an _ to make it cursive idk
                builder.note("fandom_wiki", match)

            if self.log.has_content("water") and self.log.has_content("invisible"):
                builder.error("chunk_multidraw")
        
        return builder
            

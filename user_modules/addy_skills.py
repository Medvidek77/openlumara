import core
import os

class AddySkills(core.module.Module):
    """
    Integrates Addy Osmani's Agent-Skills by injecting markdown skill files into the system prompt.
    """

    settings = {
        "enabled_skills": {"type": "array", "default": []}
    }

    def _get_skills_dir(self):
        # We put the downloaded skills in data/skills/
        skills_dir = os.path.join(core.get_data_path(), "skills")
        if not os.path.exists(skills_dir):
            os.makedirs(skills_dir, exist_ok=True)
        return skills_dir

    async def on_ready(self):
        # ensure directory exists on boot
        self._get_skills_dir()

        # Move skills from user_modules/data/skills/ if they exist there
        src_dir = os.path.join(core.get_path("user_modules"), "data", "skills")
        dst_dir = self._get_skills_dir()

        if os.path.exists(src_dir):
            for file in os.listdir(src_dir):
                if file.endswith(".md"):
                    src_file = os.path.join(src_dir, file)
                    dst_file = os.path.join(dst_dir, file)
                    with open(src_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    with open(dst_file, "w", encoding="utf-8") as f:
                        f.write(content)

        core.log("addy_skills", "Addy-Skills Module loaded.")

    @core.module.command("skill", help="Manage skills. Usage: /skill list, /skill enable <name>, /skill disable <name>")
    async def cmd_skill(self, args):
        if not args:
            return "Usage: /skill list | /skill enable <name> | /skill disable <name>"

        action = args[0].lower()
        skills_dir = self._get_skills_dir()
        available_skills = [f.replace(".md", "") for f in os.listdir(skills_dir) if f.endswith(".md")]
        enabled_skills = self.config.get("enabled_skills") or []

        if action == "list":
            if not available_skills:
                return "No skills found in data/skills/."
            else:
                msg = "Available Skills:\n"
                for skill in available_skills:
                    status = "[ENABLED]" if skill in enabled_skills else "[DISABLED]"
                    msg += f"- {skill} {status}\n"
                return msg

        elif action == "enable":
            if len(args) < 2:
                return "Usage: /skill enable <name>"
            skill_name = args[1]

            if skill_name not in available_skills:
                return f"Skill '{skill_name}' not found. Use '/skill list' to see available skills."

            if skill_name not in enabled_skills:
                enabled_skills.append(skill_name)
                self.config.set("enabled_skills", enabled_skills)
                core.config.save()
                return f"Skill '{skill_name}' has been enabled."
            else:
                return f"Skill '{skill_name}' is already enabled."

        elif action == "disable":
            if len(args) < 2:
                return "Usage: /skill disable <name>"
            skill_name = args[1]

            if skill_name in enabled_skills:
                enabled_skills.remove(skill_name)
                self.config.set("enabled_skills", enabled_skills)
                core.config.save()
                return f"Skill '{skill_name}' has been disabled."
            else:
                return f"Skill '{skill_name}' is not enabled."
        else:
            return f"Unknown action '{action}'. Usage: list, enable, disable."

    async def on_system_prompt(self):
        """
        Injects the content of the enabled skills into the system prompt.
        """
        enabled_skills = self.config.get("enabled_skills") or []
        if not enabled_skills:
            return None

        skills_dir = self._get_skills_dir()
        prompts = []

        for skill in enabled_skills:
            skill_path = os.path.join(skills_dir, f"{skill}.md")
            if os.path.exists(skill_path):
                with open(skill_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    prompts.append(f"--- BEGIN SKILL: {skill} ---\n{content}\n--- END SKILL: {skill} ---")

        if prompts:
            return "\n\n".join(prompts)

        return None

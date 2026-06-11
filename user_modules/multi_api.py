import core

class MultiApi(core.module.Module):
    """
    Module for hot-switching between Local and OpenRouter APIs without restarting.
    """

    settings = {
        "local_url": {"type": "string", "default": "http://127.0.0.1:8080/v1"},
        "local_key": {"type": "string", "default": ""},
        "local_model": {"type": "string", "default": ""},
        "openrouter_url": {"type": "string", "default": "https://openrouter.ai/api/v1"},
        "openrouter_key": {"type": "string", "default": ""},
        "openrouter_model": {"type": "string", "default": ""},
    }

    async def on_ready(self):
        core.log("multi_api", "Multi-API Hot-Switcher loaded.")

    @core.module.command("api", help="Switch API backend (usage: /api local or /api openrouter)")
    async def cmd_api(self, args):
        if not args:
            return "Usage: /api local OR /api openrouter"

        mode = args[0].lower()

        if mode == "local":
            url = self.config.get("local_url")
            key = self.config.get("local_key")
            model = self.config.get("local_model")

            self.manager.API.base_url = url
            self.manager.API.api_key = key
            if model:
                core.config.get("model")["id"] = model
                self.manager.API.model = model

            try:
                await self.manager.API.reconnect()
                msg = f"Successfully switched to Local API ({url})."
                core.log("multi_api", msg)
                return msg
            except Exception as e:
                msg = f"Failed to switch to Local API: {e}"
                core.log("multi_api", msg)
                return msg

        elif mode == "openrouter":
            url = self.config.get("openrouter_url")
            key = self.config.get("openrouter_key")
            model = self.config.get("openrouter_model")

            self.manager.API.base_url = url
            self.manager.API.api_key = key
            if model:
                core.config.get("model")["id"] = model
                self.manager.API.model = model

            try:
                await self.manager.API.reconnect()
                msg = f"Successfully switched to OpenRouter API."
                core.log("multi_api", msg)
                return msg
            except Exception as e:
                msg = f"Failed to switch to OpenRouter API: {e}"
                core.log("multi_api", msg)
                return msg
        else:
            return "Unknown API mode. Usage: /api local OR /api openrouter"

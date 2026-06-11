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

    @core.module.command("api", help={"local": "Switch to Local API (llama-server, ollama, etc.)", "openrouter": "Switch to OpenRouter API"})
    async def switch_api(self, args):
        if not args:
            return "Please specify an API target (e.g., /api local or /api openrouter)."

        target = args[0].lower().strip()

        if target == "local":
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
                if self.channel:
                    self.channel.announce(msg)
                return msg
            except Exception as e:
                msg = f"Failed to switch to Local API: {e}"
                core.log("multi_api", msg)
                if self.channel:
                    self.channel.announce(msg)
                return msg

        elif target == "openrouter":
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
                if self.channel:
                    self.channel.announce(msg)
                return msg
            except Exception as e:
                msg = f"Failed to switch to OpenRouter API: {e}"
                core.log("multi_api", msg)
                if self.channel:
                    self.channel.announce(msg)
                return msg
        else:
            return f"Unknown API target: {target}. Available targets: local, openrouter"

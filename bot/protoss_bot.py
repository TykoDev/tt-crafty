from sc2.bot_ai import BotAI
from .core import BotSettings

class ProtossBot(BotAI):
    def __init__(self, settings: BotSettings):
        super().__init__()
        print("ProtossBot is not yet implemented. See bot/protoss_spec.md")

    async def on_step(self, iteration: int):
        pass

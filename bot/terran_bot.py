from sc2.bot_ai import BotAI
from .core import BotSettings

class TerranBot(BotAI):
    def __init__(self, settings: BotSettings):
        super().__init__()
        print("TerranBot is not yet implemented. See bot/terran_spec.md")

    async def on_step(self, iteration: int):
        pass

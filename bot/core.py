from enum import Enum
from dataclasses import dataclass
import random
from sc2.bot_ai import BotAI
from sc2.data import Race

class BotPersonality(Enum):
    STANDARD = "Standard"
    ECONOMIC = "Economic"
    AGGRESSIVE = "Aggressive"
    CHEESE = "Cheese"

@dataclass
class BotSettings:
    mmr: int = 3000
    personality: BotPersonality = BotPersonality.STANDARD

class SkillManager:
    """
    Manages the bot's 'Skill' by simulating human limitations based on MMR.
    MMR Range: 0 - 9999
    """
    def __init__(self, mmr: int):
        self.mmr = mmr
        # Map MMR to Tier (approximate)
        if mmr < 2500: self.tier = "Bronze/Silver"
        elif mmr < 3500: self.tier = "Gold/Plat"
        elif mmr < 4500: self.tier = "Diamond"
        elif mmr < 5500: self.tier = "Master"
        else: self.tier = "GM"

        # Define Error Rates (Probability of doing nothing or messing up)
        # Higher MMR = Lower Error Rate
        self.error_rate = max(0, (6000 - mmr) / 10000.0) if mmr < 6000 else 0

        # APM Cap (Actions Per Minute sim) - Delay in steps
        # 22.4 steps per second.
        # Bronze (APM 30) -> Action every ~45 steps?
        # GM (APM 300+) -> Action every step.
        if mmr >= 5000:
            self.action_delay = 0
        else:
            # Simple formula to map MMR to step delay
            # 2000 MMR -> Delay 4
            # 5000 MMR -> Delay 0
            self.action_delay = int(max(0, (5000 - mmr) / 750.0))

    def should_skip_step(self, iteration: int) -> bool:
        """Determines if the bot should 'idle' this step due to APM limits."""
        if self.action_delay == 0:
            return False
        return (iteration % (self.action_delay + 1)) != 0

    def should_make_mistake(self) -> bool:
        """Determines if the bot should fail a check (e.g., miss an inject)."""
        return random.random() < self.error_rate

class PersonalityManager:
    """
    Determines the strategic direction based on personality.
    """
    def __init__(self, personality: BotPersonality):
        self.personality = personality

    def get_opener(self, race: Race = Race.Zerg):
        if race == Race.Zerg:
            if self.personality == BotPersonality.CHEESE:
                return "12_POOL"
            elif self.personality == BotPersonality.AGGRESSIVE:
                return "POOL_FIRST"
            elif self.personality == BotPersonality.ECONOMIC:
                return "HATCH_FIRST"
            else:
                return "HATCH_FIRST" # Standard

        elif race == Race.Terran:
            if self.personality == BotPersonality.CHEESE:
                return "PROXY_RAX"
            elif self.personality == BotPersonality.AGGRESSIVE:
                return "3_RAX"
            elif self.personality == BotPersonality.ECONOMIC:
                return "CC_FIRST"
            else:
                return "RAX_EXPAND" # Standard

        elif race == Race.Protoss:
            if self.personality == BotPersonality.CHEESE:
                return "CANNON_RUSH"
            elif self.personality == BotPersonality.AGGRESSIVE:
                return "4_GATE"
            elif self.personality == BotPersonality.ECONOMIC:
                return "NEXUS_FIRST"
            else:
                return "GATE_EXPAND" # Standard

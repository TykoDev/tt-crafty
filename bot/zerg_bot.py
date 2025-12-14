from sc2.bot_ai import BotAI
from sc2.data import Result
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from .core import BotSettings, SkillManager, PersonalityManager, BotPersonality

class ZergBot(BotAI):
    def __init__(self, settings: BotSettings):
        super().__init__()
        self.settings = settings
        self.skill_manager = SkillManager(settings.mmr)
        self.personality_manager = PersonalityManager(settings.personality)
        self.opener = self.personality_manager.get_opener()
        self.has_performed_opener = False

    async def on_start(self):
        print(f"ZergBot Started. MMR: {self.settings.mmr} ({self.skill_manager.tier}), Style: {self.settings.personality.name}")
        self.client.game_step = 2 # Lower is more responsive. 2 is standard for bots.

    async def on_step(self, iteration: int):
        # 1. Skill Throttling
        if self.skill_manager.should_skip_step(iteration):
            return

        # 2. Distribute Workers
        await self.distribute_workers()

        # 3. Supply
        await self.manage_supply()

        # 4. Build Order / Opener
        await self.execute_opener()

        # 5. Economy (Queens, Drones)
        await self.manage_economy()

        # 6. Army
        await self.manage_army()

    async def manage_supply(self):
        # If supply left < 3 (and supply < 200), build overlord.
        if self.supply_left < 4 and self.supply_cap < 200:
            if self.can_afford(UnitTypeId.OVERLORD) and self.larva.exists:
                # Skill check: Low MMR gets supply blocked
                if not self.skill_manager.should_make_mistake():
                    self.larva.random.train(UnitTypeId.OVERLORD)

    async def execute_opener(self):
        hq = self.townhalls.first

        if self.opener == "12_POOL":
            # 12 Pool Logic
            if self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0:
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.build(UnitTypeId.SPAWNINGPOOL, near=hq)

        elif self.opener == "HATCH_FIRST":
            # Hatch First
            if self.structures(UnitTypeId.HATCHERY).amount < 2 and not self.already_pending(UnitTypeId.HATCHERY):
                if self.can_afford(UnitTypeId.HATCHERY):
                    await self.expand_now()

        # Build Spawning Pool if not exists (for standard plays)
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount == 0 and not self.already_pending(UnitTypeId.SPAWNINGPOOL):
             if self.structures(UnitTypeId.HATCHERY).amount >= 2 or self.opener != "HATCH_FIRST":
                 if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                     await self.build(UnitTypeId.SPAWNINGPOOL, near=hq)

    async def manage_economy(self):
        # Train Drones
        # Don't overproduce drones if we are cheesing
        max_drones = 80
        if self.settings.personality == BotPersonality.CHEESE:
            max_drones = 25 # Cut workers early

        if self.supply_workers < max_drones and self.larva.exists and self.can_afford(UnitTypeId.DRONE):
             if not self.skill_manager.should_make_mistake(): # Miss drone cycles
                 self.larva.random.train(UnitTypeId.DRONE)

        # Build Queens
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            for hatch in self.townhalls.ready:
                if self.units(UnitTypeId.QUEEN).amount < self.townhalls.amount * 1.5:
                    if self.can_afford(UnitTypeId.QUEEN) and hatch.is_idle:
                        hatch.train(UnitTypeId.QUEEN)

        # Inject Larva (Queens)
        for queen in self.units(UnitTypeId.QUEEN):
            if queen.energy >= 25:
                hatch = self.townhalls.closest_to(queen)
                if hatch.is_ready and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER):
                     if not self.skill_manager.should_make_mistake(): # Miss injects
                         queen(AbilityId.EFFECT_INJECTLARVA, hatch)

    async def manage_army(self):
        # Train Zerglings
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
             if self.larva.exists and self.can_afford(UnitTypeId.ZERGLING):
                 # Balance drones and lings based on personality
                 if self.supply_workers >= 16 or self.settings.personality == BotPersonality.CHEESE:
                     self.larva.random.train(UnitTypeId.ZERGLING)

        # Attack
        army = self.units(UnitTypeId.ZERGLING)
        attack_threshold = 30
        if self.settings.personality == BotPersonality.CHEESE:
            attack_threshold = 6
        elif self.settings.personality == BotPersonality.AGGRESSIVE:
            attack_threshold = 15

        if army.amount >= attack_threshold:
            target = self.enemy_start_locations[0]
            for unit in army:
                unit.attack(target)

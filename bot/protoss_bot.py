from sc2.bot_ai import BotAI
from sc2.data import Result, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from .core import BotSettings, SkillManager, PersonalityManager, BotPersonality

class ProtossBot(BotAI):
    def __init__(self, settings: BotSettings):
        super().__init__()
        self.settings = settings
        self.skill_manager = SkillManager(settings.mmr)
        self.personality_manager = PersonalityManager(settings.personality)
        self.opener = None

    async def on_start(self):
        print(f"ProtossBot Started. MMR: {self.settings.mmr} ({self.skill_manager.tier}), Style: {self.settings.personality.name}")
        self.client.game_step = 2
        self.opener = self.personality_manager.get_opener(Race.Protoss)

    async def on_step(self, iteration: int):
        if self.skill_manager.should_skip_step(iteration):
            return

        await self.distribute_workers()
        await self.manage_supply()
        await self.manage_economy()
        await self.manage_buildings()
        await self.manage_army()

    async def manage_supply(self):
        if self.supply_left < 5 and self.supply_cap < 200:
            if self.can_afford(UnitTypeId.PYLON) and self.already_pending(UnitTypeId.PYLON) == 0:
                if not self.skill_manager.should_make_mistake():
                    if self.townhalls.exists:
                        await self.build(UnitTypeId.PYLON, near=self.townhalls.first)

    async def manage_economy(self):
        # Train Probes
        if self.townhalls.ready.exists and self.can_afford(UnitTypeId.PROBE):
            nexus = self.townhalls.ready.first
            if self.supply_workers < 70 and nexus.is_idle:
                 if not self.skill_manager.should_make_mistake():
                     nexus.train(UnitTypeId.PROBE)

        # Expand (Nexus)
        if self.opener == "NEXUS_FIRST" and self.townhalls.amount < 2:
             if self.can_afford(UnitTypeId.NEXUS) and not self.already_pending(UnitTypeId.NEXUS):
                 await self.expand_now()

        # General expansion
        if self.minerals > 400 and self.townhalls.amount < 4:
            if not self.already_pending(UnitTypeId.NEXUS):
                await self.expand_now()

        # Gas
        if self.structures(UnitTypeId.GATEWAY).exists:
             for nexus in self.townhalls.ready:
                 vGs = self.vespene_geyser.closer_than(15, nexus)
                 for vG in vGs:
                     if not self.structures(UnitTypeId.ASSIMILATOR).closer_than(1, vG).exists:
                         worker = self.select_build_worker(vG.position)
                         if worker and self.can_afford(UnitTypeId.ASSIMILATOR):
                             worker.build(UnitTypeId.ASSIMILATOR, vG)

    async def manage_buildings(self):
        if not self.townhalls.exists:
            return

        hq = self.townhalls.first
        pylons = self.structures(UnitTypeId.PYLON).ready

        if not pylons.exists:
            return

        # Cannon Rush (Defensive/Turtle for simplicity)
        if self.opener == "CANNON_RUSH":
             if not self.structures(UnitTypeId.FORGE).exists:
                  if self.can_afford(UnitTypeId.FORGE):
                       await self.build(UnitTypeId.FORGE, near=pylons.closest_to(hq))

             if self.structures(UnitTypeId.FORGE).ready.exists:
                  if self.can_afford(UnitTypeId.PHOTONCANNON) and self.structures(UnitTypeId.PHOTONCANNON).amount < 4:
                        await self.build(UnitTypeId.PHOTONCANNON, near=pylons.closest_to(hq))
             return # Skip other buildings if hardcore rushing/turtling

        # Gateways
        desired_gateways = self.townhalls.amount * 2
        if self.opener == "4_GATE":
            desired_gateways = 4

        if self.structures(UnitTypeId.GATEWAY).amount < desired_gateways:
             if self.can_afford(UnitTypeId.GATEWAY):
                  await self.build(UnitTypeId.GATEWAY, near=pylons.closest_to(hq))

        # Cyber Core
        if self.structures(UnitTypeId.GATEWAY).ready.exists and not self.structures(UnitTypeId.CYBERNETICSCORE).exists:
             if self.can_afford(UnitTypeId.CYBERNETICSCORE):
                 await self.build(UnitTypeId.CYBERNETICSCORE, near=pylons.closest_to(hq))

    async def manage_army(self):
        # Train Units
        for gate in self.structures(UnitTypeId.GATEWAY).ready:
            if gate.is_idle:
                if self.structures(UnitTypeId.CYBERNETICSCORE).ready.exists and self.can_afford(UnitTypeId.STALKER):
                     gate.train(UnitTypeId.STALKER)
                elif self.can_afford(UnitTypeId.ZEALOT):
                     gate.train(UnitTypeId.ZEALOT)

        # Attack
        army = self.units.of_type([UnitTypeId.STALKER, UnitTypeId.ZEALOT])
        threshold = 15
        if self.opener == "4_GATE": threshold = 8

        if army.amount > threshold:
             if self.enemy_start_locations:
                target = self.enemy_start_locations[0]
                for unit in army:
                    unit.attack(target)

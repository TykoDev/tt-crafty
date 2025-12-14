from sc2.bot_ai import BotAI
from sc2.data import Result, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.ids.buff_id import BuffId
from .core import BotSettings, SkillManager, PersonalityManager, BotPersonality

class TerranBot(BotAI):
    def __init__(self, settings: BotSettings):
        super().__init__()
        self.settings = settings
        self.skill_manager = SkillManager(settings.mmr)
        self.personality_manager = PersonalityManager(settings.personality)
        self.opener = None

    async def on_start(self):
        print(f"TerranBot Started. MMR: {self.settings.mmr} ({self.skill_manager.tier}), Style: {self.settings.personality.name}")
        self.client.game_step = 2
        self.opener = self.personality_manager.get_opener(Race.Terran)

    async def on_step(self, iteration: int):
        if self.skill_manager.should_skip_step(iteration):
            return

        await self.distribute_workers()
        await self.manage_supply()
        await self.manage_economy()
        await self.manage_buildings()
        await self.manage_addons()
        await self.manage_tech()
        await self.manage_upgrades()
        await self.manage_army()

    async def manage_supply(self):
        if self.supply_left < 5 and self.supply_cap < 200:
            if self.can_afford(UnitTypeId.SUPPLYDEPOT) and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
                if not self.skill_manager.should_make_mistake():
                    if self.townhalls.exists:
                        await self.build(UnitTypeId.SUPPLYDEPOT, near=self.townhalls.first)

    async def manage_economy(self):
        # Train SCVs
        for cc in self.townhalls.ready:
            if self.supply_workers < 70 and cc.is_idle:
                 if self.can_afford(UnitTypeId.SCV):
                     if not self.skill_manager.should_make_mistake():
                         cc.train(UnitTypeId.SCV)

        # Orbital Command
        for cc in self.townhalls(UnitTypeId.COMMANDCENTER).ready:
             if self.structures(UnitTypeId.BARRACKS).ready.exists and self.can_afford(UnitTypeId.ORBITALCOMMAND):
                  cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

        # MULEs
        for oc in self.townhalls(UnitTypeId.ORBITALCOMMAND).ready:
             if oc.energy >= 50:
                 mfs = self.mineral_field.closer_than(10, oc)
                 if mfs.exists:
                     if not self.skill_manager.should_make_mistake():
                         oc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, mfs.largest)

        # Expand
        if self.opener == "CC_FIRST" and self.townhalls.amount < 2:
             if self.can_afford(UnitTypeId.COMMANDCENTER) and not self.already_pending(UnitTypeId.COMMANDCENTER):
                 await self.expand_now()

        if self.minerals > 400 and self.townhalls.amount < 4:
            if not self.already_pending(UnitTypeId.COMMANDCENTER):
                await self.expand_now()

        # Gas
        if self.structures(UnitTypeId.BARRACKS).exists:
             for cc in self.townhalls.ready:
                 vGs = self.vespene_geyser.closer_than(15, cc)
                 for vG in vGs:
                     if not self.structures(UnitTypeId.REFINERY).closer_than(1, vG).exists:
                         worker = self.select_build_worker(vG.position)
                         if worker and self.can_afford(UnitTypeId.REFINERY):
                             worker.build(UnitTypeId.REFINERY, vG)

    async def manage_buildings(self):
        if not self.townhalls.exists:
            return

        hq = self.townhalls.first

        # Barracks
        desired_rax = 3 if self.opener == "3_RAX" or self.opener == "PROXY_RAX" else 2
        if self.townhalls.amount > 1:
            desired_rax += 2 * (self.townhalls.amount - 1)

        if self.structures(UnitTypeId.BARRACKS).amount < desired_rax:
             if self.can_afford(UnitTypeId.BARRACKS):
                  if self.structures(UnitTypeId.SUPPLYDEPOT).ready.exists or self.supply_cap > 15:
                      await self.build(UnitTypeId.BARRACKS, near=hq)

    async def manage_addons(self):
        for rax in self.structures(UnitTypeId.BARRACKS).ready:
             if rax.add_on_tag == 0:
                 # 1st Rax -> Tech Lab, others Reactor
                 if self.structures(UnitTypeId.BARRACKSTECHLAB).amount < 1:
                      if self.can_afford(UnitTypeId.BARRACKSTECHLAB):
                           rax.build(UnitTypeId.BARRACKSTECHLAB)
                 elif self.can_afford(UnitTypeId.BARRACKSREACTOR):
                      rax.build(UnitTypeId.BARRACKSREACTOR)

    async def manage_tech(self):
         if not self.townhalls.exists: return
         hq = self.townhalls.first

         # Factory (requires Barracks)
         if self.structures(UnitTypeId.BARRACKS).ready.exists:
              if not self.structures(UnitTypeId.FACTORY).exists:
                   if self.can_afford(UnitTypeId.FACTORY):
                        await self.build(UnitTypeId.FACTORY, near=hq)

         # Starport (requires Factory)
         if self.structures(UnitTypeId.FACTORY).ready.exists:
              if not self.structures(UnitTypeId.STARPORT).exists:
                   if self.can_afford(UnitTypeId.STARPORT):
                        await self.build(UnitTypeId.STARPORT, near=hq)

    async def manage_upgrades(self):
        tl = self.structures(UnitTypeId.BARRACKSTECHLAB).ready.first
        if tl:
             if self.can_afford(UpgradeId.STIMPACK) and not self.already_pending_upgrade(UpgradeId.STIMPACK):
                  tl.research(UpgradeId.STIMPACK)
             elif self.can_afford(UpgradeId.SHIELDWALL) and not self.already_pending_upgrade(UpgradeId.SHIELDWALL):
                  tl.research(UpgradeId.SHIELDWALL)

    async def manage_army(self):
        # Marines
        for rax in self.structures(UnitTypeId.BARRACKS).ready:
             if self.can_afford(UnitTypeId.MARINE):
                  if rax.add_on_tag != 0 and self.structures(UnitTypeId.BARRACKSREACTOR).find_by_tag(rax.add_on_tag):
                       if len(rax.orders) < 2:
                            rax.train(UnitTypeId.MARINE)
                  elif rax.is_idle:
                       rax.train(UnitTypeId.MARINE)

        # Tanks
        for fac in self.structures(UnitTypeId.FACTORY).ready:
             if fac.is_idle and self.can_afford(UnitTypeId.SIEGETANK):
                  fac.train(UnitTypeId.SIEGETANK)

        # Medivacs
        for sp in self.structures(UnitTypeId.STARPORT).ready:
             if sp.is_idle and self.can_afford(UnitTypeId.MEDIVAC):
                  sp.train(UnitTypeId.MEDIVAC)

        # Attack
        army = self.units.of_type([UnitTypeId.MARINE, UnitTypeId.MARAUDER, UnitTypeId.SIEGETANK, UnitTypeId.MEDIVAC])
        threshold = 20
        if self.opener == "PROXY_RAX": threshold = 6

        if army.amount > threshold:
             if self.enemy_start_locations:
                target = self.enemy_start_locations[0]
                for unit in army:
                    unit.attack(target)

                    # Stim
                    if unit.type_id == UnitTypeId.MARINE and unit.distance_to(target) < 15:
                        if not unit.has_buff(BuffId.STIMPACK) and unit.health > 10:
                            if self.already_pending_upgrade(UpgradeId.STIMPACK) == 1: # check if researched?
                                # already_pending checks if being researched.
                                # to check if done, we check self.state.upgrades
                                # But easier: try to use ability, if fail ignore
                                unit(AbilityId.EFFECT_STIM_MARINE)

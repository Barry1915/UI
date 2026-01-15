from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, TypedDict


PlantType = Literal[
    "peashooter",
    "repeater",
    "snowpea",
    "sunflower",
    "twin_sunflower",
    "wallnut",
    "cherrybomb",
    "chomper",
    "spikeweed",
]


class PlantCatalogItem(TypedDict):
    type: PlantType
    name: str
    desc: str
    cost: int
    hpMax: int


@dataclass
class Plant:
    id: int
    type: PlantType
    row: int
    col: int
    hp: int
    placed_tick: int = 0
    last_action_tick: int = 0


@dataclass
class Zombie:
    id: int
    row: int
    x: float
    hp: int
    speed: float
    attack_damage: int
    attack_cooldown_ticks: int
    last_attack_tick: int = 0
    slow_until_tick: int = 0
    slow_factor: float = 0.6
    last_spike_tick: int = 0


@dataclass
class Projectile:
    id: int
    row: int
    x: float
    speed: float
    damage: int
    kind: Literal["pea", "snow"] = "pea"
    slow_ticks: int = 0
    slow_factor: float = 0.6


@dataclass
class SunToken:
    id: int
    row: int
    col: int
    value: int
    expires_at_tick: int


@dataclass
class GameConfig:
    rows: int = 5
    cols: int = 9
    tick_ms: int = 100
    start_sun: int = 150


@dataclass
class Game:
    config: GameConfig = field(default_factory=GameConfig)
    running: bool = False
    game_over: bool = False
    game_over_reason: Optional[str] = None

    tick: int = 0
    sun: int = 150
    difficulty: int = 1  # 1..3

    _next_id: int = 1
    _spawn_rng: random.Random = field(default_factory=random.Random)

    plants: Dict[str, Plant] = field(default_factory=dict)  # key = "r,c"
    zombies: List[Zombie] = field(default_factory=list)
    projectiles: List[Projectile] = field(default_factory=list)
    sun_tokens: List[SunToken] = field(default_factory=list)
    effects: List[Dict[str, Any]] = field(default_factory=list)

    last_spawn_tick: int = 0

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.running = False
        self.game_over = False
        self.game_over_reason = None
        self.tick = 0
        self.sun = self.config.start_sun
        self.plants = {}
        self.zombies = []
        self.projectiles = []
        self.sun_tokens = []
        self.effects = []
        self.last_spawn_tick = 0
        self._next_id = 1

    def set_difficulty(self, difficulty: int) -> None:
        self.difficulty = max(1, min(3, int(difficulty)))

    def _new_id(self) -> int:
        nid = self._next_id
        self._next_id += 1
        return nid

    @staticmethod
    def _cell_key(row: int, col: int) -> str:
        return f"{row},{col}"

    def place_plant(self, row: int, col: int, plant_type: PlantType) -> Dict[str, Any]:
        if self.game_over:
            return {"ok": False, "error": "game_over"}
        if not (0 <= row < self.config.rows and 0 <= col < self.config.cols):
            return {"ok": False, "error": "out_of_bounds"}

        key = self._cell_key(row, col)
        if key in self.plants:
            return {"ok": False, "error": "cell_occupied"}

        cost, hp = self._plant_cost_hp(plant_type)
        if self.sun < cost:
            return {"ok": False, "error": "not_enough_sun", "need": cost, "have": self.sun}

        self.sun -= cost
        self.plants[key] = Plant(
            id=self._new_id(),
            type=plant_type,
            row=row,
            col=col,
            hp=hp,
            placed_tick=self.tick,
        )
        return {"ok": True}

    def remove_plant(self, row: int, col: int) -> Dict[str, Any]:
        key = self._cell_key(row, col)
        if key not in self.plants:
            return {"ok": False, "error": "no_plant"}
        del self.plants[key]
        return {"ok": True}

    def collect_sun(self, token_id: int) -> Dict[str, Any]:
        for i, token in enumerate(self.sun_tokens):
            if token.id == token_id:
                self.sun += token.value
                self.sun_tokens.pop(i)
                return {"ok": True, "value": token.value}
        return {"ok": False, "error": "sun_not_found"}

    def toggle_running(self, running: Optional[bool] = None) -> None:
        if self.game_over:
            self.running = False
            return
        self.running = (not self.running) if running is None else bool(running)

    def step(self) -> None:
        if self.game_over:
            self.running = False
            return

        self.tick += 1
        self._maybe_spawn_zombie()
        self._plants_act()
        self._move_projectiles_and_hit()
        self._zombies_act()
        self._expire_sun_tokens()
        self._expire_effects()
        self._check_game_over()

    def _plant_cost_hp(self, plant_type: PlantType) -> tuple[int, int]:
        if plant_type == "peashooter":
            return 100, 5
        if plant_type == "repeater":
            return 175, 5
        if plant_type == "snowpea":
            return 175, 5
        if plant_type == "sunflower":
            return 50, 4
        if plant_type == "twin_sunflower":
            return 125, 6
        if plant_type == "wallnut":
            return 50, 18
        if plant_type == "cherrybomb":
            return 150, 999
        if plant_type == "chomper":
            return 150, 8
        if plant_type == "spikeweed":
            return 100, 10
        return 100, 5

    def plant_catalog(self) -> List[PlantCatalogItem]:
        # Order here controls front-end card ordering
        catalog: List[PlantCatalogItem] = []
        for t, name, desc in [
            ("sunflower", "向日葵", "稳定产出阳光"),
            ("twin_sunflower", "双子向日葵", "更高效率产出阳光"),
            ("peashooter", "豌豆射手", "自动射击"),
            ("repeater", "双发射手", "一次发射两颗豌豆"),
            ("snowpea", "寒冰射手", "命中后减速僵尸"),
            ("wallnut", "坚果墙", "高生命值，阻挡僵尸"),
            ("spikeweed", "地刺", "僵尸踩踏时持续受伤"),
            ("chomper", "食人花", "吞噬贴脸僵尸（有冷却）"),
            ("cherrybomb", "樱桃炸弹", "短延时爆炸，范围高伤害"),
        ]:
            cost, hp = self._plant_cost_hp(t)  # type: ignore[arg-type]
            catalog.append({"type": t, "name": name, "desc": desc, "cost": cost, "hpMax": hp})  # type: ignore[typeddict-item]
        return catalog

    def _maybe_spawn_zombie(self) -> None:
        base_interval = {1: 35, 2: 28, 3: 22}[self.difficulty]
        if self.tick - self.last_spawn_tick < base_interval:
            return

        self.last_spawn_tick = self.tick
        row = self._spawn_rng.randrange(0, self.config.rows)
        hp = {1: 8, 2: 11, 3: 14}[self.difficulty]
        speed = {1: 0.045, 2: 0.055, 3: 0.065}[self.difficulty]  # cols per tick
        z = Zombie(
            id=self._new_id(),
            row=row,
            x=self.config.cols + 0.8,
            hp=hp,
            speed=speed,
            attack_damage=1,
            attack_cooldown_ticks=8,
        )
        self.zombies.append(z)

    def _plants_act(self) -> None:
        for plant in list(self.plants.values()):
            if plant.hp <= 0:
                self.plants.pop(self._cell_key(plant.row, plant.col), None)
                continue

            if plant.type == "peashooter":
                shoot_interval = 10
                if self.tick - plant.last_action_tick >= shoot_interval:
                    # Shoot only if there is a zombie in the same row ahead
                    if any(z.row == plant.row and z.x >= plant.col for z in self.zombies):
                        plant.last_action_tick = self.tick
                        self.projectiles.append(
                            Projectile(
                                id=self._new_id(),
                                row=plant.row,
                                x=plant.col + 0.3,
                                speed=0.22,
                                damage=1,
                                kind="pea",
                            )
                        )
            elif plant.type == "repeater":
                shoot_interval = 10
                if self.tick - plant.last_action_tick >= shoot_interval:
                    if any(z.row == plant.row and z.x >= plant.col for z in self.zombies):
                        plant.last_action_tick = self.tick
                        self.projectiles.append(
                            Projectile(id=self._new_id(), row=plant.row, x=plant.col + 0.28, speed=0.22, damage=1, kind="pea")
                        )
                        self.projectiles.append(
                            Projectile(id=self._new_id(), row=plant.row, x=plant.col + 0.38, speed=0.22, damage=1, kind="pea")
                        )
            elif plant.type == "snowpea":
                shoot_interval = 11
                if self.tick - plant.last_action_tick >= shoot_interval:
                    if any(z.row == plant.row and z.x >= plant.col for z in self.zombies):
                        plant.last_action_tick = self.tick
                        self.projectiles.append(
                            Projectile(
                                id=self._new_id(),
                                row=plant.row,
                                x=plant.col + 0.3,
                                speed=0.20,
                                damage=1,
                                kind="snow",
                                slow_ticks=40,
                                slow_factor=0.6,
                            )
                        )
            elif plant.type == "sunflower":
                produce_interval = 60
                if self.tick - plant.last_action_tick >= produce_interval:
                    plant.last_action_tick = self.tick
                    token = SunToken(
                        id=self._new_id(),
                        row=plant.row,
                        col=plant.col,
                        value=25,
                        expires_at_tick=self.tick + 200,
                    )
                    self.sun_tokens.append(token)
            elif plant.type == "twin_sunflower":
                produce_interval = 55
                if self.tick - plant.last_action_tick >= produce_interval:
                    plant.last_action_tick = self.tick
                    token = SunToken(
                        id=self._new_id(),
                        row=plant.row,
                        col=plant.col,
                        value=50,
                        expires_at_tick=self.tick + 220,
                    )
                    self.sun_tokens.append(token)
            elif plant.type == "wallnut":
                # Tank plant, no actions
                pass
            elif plant.type == "cherrybomb":
                # Short fuse, then explode and disappear
                fuse_ticks = 8
                if self.tick - plant.placed_tick >= fuse_ticks:
                    self._explode_at(plant.row, plant.col, radius=1, damage=8)
                    self.plants.pop(self._cell_key(plant.row, plant.col), None)
            elif plant.type == "chomper":
                # Eat a zombie that is overlapping this tile (powerful, long cooldown)
                cooldown = 90
                if self.tick - plant.last_action_tick < cooldown:
                    continue
                target = self._find_overlapping_zombie(row=plant.row, col=plant.col, threshold=0.35)
                if target is not None:
                    plant.last_action_tick = self.tick
                    target.hp = 0
                    self.effects.append(
                        {
                            "id": self._new_id(),
                            "type": "chomp",
                            "row": plant.row,
                            "col": plant.col,
                            "expiresAtTick": self.tick + 14,
                        }
                    )
            elif plant.type == "spikeweed":
                # Passive plant: damage is applied in zombie step (so it works while zombies move/attack)
                pass

    def _move_projectiles_and_hit(self) -> None:
        if not self.projectiles:
            return

        alive: List[Projectile] = []
        for p in self.projectiles:
            p.x += p.speed
            hit = False
            for z in self.zombies:
                if z.row != p.row:
                    continue
                # collision threshold around zombie x
                if abs(z.x - p.x) <= 0.25:
                    z.hp -= p.damage
                    if p.slow_ticks > 0:
                        z.slow_until_tick = max(z.slow_until_tick, self.tick + p.slow_ticks)
                        z.slow_factor = min(z.slow_factor, p.slow_factor)
                    hit = True
                    break
            if hit:
                continue
            if p.x <= self.config.cols + 0.8:
                alive.append(p)
        self.projectiles = alive
        self.zombies = [z for z in self.zombies if z.hp > 0]

    def _zombies_act(self) -> None:
        if not self.zombies:
            return

        for z in self.zombies:
            # Spikeweed damage (even if zombie is attacking)
            spike = self._find_plant_at_tile(z.row, int(z.x), want_type="spikeweed")
            if spike is not None and self.tick - z.last_spike_tick >= 5:
                z.last_spike_tick = self.tick
                z.hp -= 1

            # Find nearest plant in front of the zombie (smallest col where zombie overlaps)
            target: Optional[Plant] = None
            for plant in self.plants.values():
                if plant.row != z.row:
                    continue
                if (plant.col - 0.15) <= z.x <= (plant.col + 0.35):
                    target = plant
                    break

            if target is None:
                eff_speed = z.speed * (z.slow_factor if self.tick < z.slow_until_tick else 1.0)
                z.x -= eff_speed
                continue

            if self.tick - z.last_attack_tick >= z.attack_cooldown_ticks:
                z.last_attack_tick = self.tick
                target.hp -= z.attack_damage
                if target.hp <= 0:
                    self.plants.pop(self._cell_key(target.row, target.col), None)

    def _expire_sun_tokens(self) -> None:
        if not self.sun_tokens:
            return
        self.sun_tokens = [t for t in self.sun_tokens if t.expires_at_tick > self.tick]

    def _expire_effects(self) -> None:
        if not self.effects:
            return
        self.effects = [e for e in self.effects if int(e.get("expiresAtTick", 0)) > self.tick]

    def _find_overlapping_zombie(self, row: int, col: int, threshold: float) -> Optional[Zombie]:
        for z in self.zombies:
            if z.row != row:
                continue
            if abs(z.x - col) <= threshold:
                return z
        return None

    def _find_plant_at_tile(self, row: int, col: int, want_type: PlantType) -> Optional[Plant]:
        p = self.plants.get(self._cell_key(row, col))
        if p is None or p.type != want_type:
            return None
        return p

    def _explode_at(self, row: int, col: int, radius: int, damage: int) -> None:
        self.effects.append(
            {"id": self._new_id(), "type": "explosion", "row": row, "col": col, "radius": radius, "expiresAtTick": self.tick + 14}
        )
        for z in self.zombies:
            if abs(z.row - row) <= radius and abs(z.x - col) <= (radius + 0.6):
                z.hp -= damage

    def _check_game_over(self) -> None:
        for z in self.zombies:
            if z.x <= -0.2:
                self.game_over = True
                self.game_over_reason = "zombies_reached_house"
                self.running = False
                return

    def serialize(self) -> Dict[str, Any]:
        plants = [
            {
                "id": p.id,
                "type": p.type,
                "row": p.row,
                "col": p.col,
                "hp": p.hp,
            }
            for p in self.plants.values()
        ]
        zombies = [
            {
                "id": z.id,
                "row": z.row,
                "x": z.x,
                "hp": z.hp,
                "slowed": self.tick < z.slow_until_tick,
            }
            for z in self.zombies
        ]
        projectiles = [
            {
                "id": pr.id,
                "row": pr.row,
                "x": pr.x,
                "kind": pr.kind,
            }
            for pr in self.projectiles
        ]
        suns = [
            {
                "id": s.id,
                "row": s.row,
                "col": s.col,
                "value": s.value,
                "expiresAtTick": s.expires_at_tick,
            }
            for s in self.sun_tokens
        ]
        return {
            "tick": self.tick,
            "running": self.running,
            "gameOver": self.game_over,
            "gameOverReason": self.game_over_reason,
            "sun": self.sun,
            "difficulty": self.difficulty,
            "config": {
                "rows": self.config.rows,
                "cols": self.config.cols,
                "tickMs": self.config.tick_ms,
            },
            "plantCatalog": self.plant_catalog(),
            "plants": plants,
            "zombies": zombies,
            "projectiles": projectiles,
            "sunTokens": suns,
            "effects": self.effects,
        }


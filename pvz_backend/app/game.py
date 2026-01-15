from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


PlantType = Literal["peashooter", "sunflower", "wallnut"]


@dataclass
class Plant:
    id: int
    type: PlantType
    row: int
    col: int
    hp: int
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


@dataclass
class Projectile:
    id: int
    row: int
    x: float
    speed: float
    damage: int


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
        self.plants[key] = Plant(id=self._new_id(), type=plant_type, row=row, col=col, hp=hp)
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
        self._check_game_over()

    def _plant_cost_hp(self, plant_type: PlantType) -> tuple[int, int]:
        if plant_type == "peashooter":
            return 100, 5
        if plant_type == "sunflower":
            return 50, 4
        if plant_type == "wallnut":
            return 50, 18
        return 100, 5

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
            elif plant.type == "wallnut":
                # Tank plant, no actions
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
            # Find nearest plant in front of the zombie (smallest col where zombie overlaps)
            target: Optional[Plant] = None
            for plant in self.plants.values():
                if plant.row != z.row:
                    continue
                if (plant.col - 0.15) <= z.x <= (plant.col + 0.35):
                    target = plant
                    break

            if target is None:
                z.x -= z.speed
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
            }
            for z in self.zombies
        ]
        projectiles = [
            {
                "id": pr.id,
                "row": pr.row,
                "x": pr.x,
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
            "plants": plants,
            "zombies": zombies,
            "projectiles": projectiles,
            "sunTokens": suns,
        }


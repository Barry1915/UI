from __future__ import annotations

import asyncio
import contextlib
import json
from typing import Any, Dict

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .game import Game


app = FastAPI(title="PVZ Mini Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/pvz", tags=["pvz"])


@router.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True}


async def _ws_send_state(ws: WebSocket, game: Game) -> None:
    await ws.send_json({"type": "state", "state": game.serialize()})


@router.websocket("/ws")
async def pvz_ws(ws: WebSocket) -> None:
    await ws.accept()
    game = Game()
    lock = asyncio.Lock()

    await ws.send_json(
        {
            "type": "hello",
            "message": "pvz-ws-ready",
            "state": game.serialize(),
        }
    )

    async def tick_loop() -> None:
        try:
            while True:
                await asyncio.sleep(game.config.tick_ms / 1000)
                async with lock:
                    if game.running:
                        game.step()
                    # Always push state at fixed rate for smooth UI
                    await _ws_send_state(ws, game)
        except Exception:
            # connection closed or send failed
            return

    ticker = asyncio.create_task(tick_loop())

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except Exception:
                await ws.send_json({"type": "error", "error": "invalid_json"})
                continue

            mtype = msg.get("type")
            async with lock:
                if mtype == "toggle":
                    game.toggle_running(msg.get("running"))
                    await ws.send_json({"type": "ack", "action": "toggle", "ok": True})
                    await _ws_send_state(ws, game)
                elif mtype == "reset":
                    game.reset()
                    await ws.send_json({"type": "ack", "action": "reset", "ok": True})
                    await _ws_send_state(ws, game)
                elif mtype == "difficulty":
                    game.set_difficulty(int(msg.get("value", 1)))
                    await ws.send_json({"type": "ack", "action": "difficulty", "ok": True})
                    await _ws_send_state(ws, game)
                elif mtype == "place":
                    row = int(msg.get("row", -1))
                    col = int(msg.get("col", -1))
                    plant_type = str(msg.get("plantType", "peashooter"))
                    if plant_type not in ("peashooter", "sunflower", "wallnut"):
                        await ws.send_json({"type": "ack", "action": "place", "ok": False, "error": "bad_plant_type"})
                        continue
                    result = game.place_plant(row=row, col=col, plant_type=plant_type)  # type: ignore[arg-type]
                    await ws.send_json({"type": "ack", "action": "place", **result})
                    await _ws_send_state(ws, game)
                elif mtype == "remove":
                    row = int(msg.get("row", -1))
                    col = int(msg.get("col", -1))
                    result = game.remove_plant(row=row, col=col)
                    await ws.send_json({"type": "ack", "action": "remove", **result})
                    await _ws_send_state(ws, game)
                elif mtype == "collectSun":
                    token_id = int(msg.get("id", -1))
                    result = game.collect_sun(token_id)
                    await ws.send_json({"type": "ack", "action": "collectSun", **result})
                    await _ws_send_state(ws, game)
                else:
                    await ws.send_json({"type": "error", "error": "unknown_type", "got": mtype})
    except WebSocketDisconnect:
        return
    finally:
        ticker.cancel()
        with contextlib.suppress(Exception):
            await ticker


app.include_router(router)


"""Détection de gestes main à partir des landmarks MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class Gesture(Enum):
    NONE = auto()
    DRAW = auto()       # 1 doigt (index)
    SELECT = auto()     # 2 doigts (index + majeur)
    ERASE = auto()      # paume ouverte
    SAVE = auto()       # pouce levé


@dataclass
class HandState:
    gesture: Gesture
    tip: tuple[float, float] | None      # index tip (px)
    palm: tuple[float, float] | None     # centre paume (px)
    landmarks_px: list[tuple[int, int]]


# Indices MediaPipe Hands
WRIST = 0
THUMB_CMC, THUMB_MCP, THUMB_IP, THUMB_TIP = 1, 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP = 5, 6, 7, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP = 9, 10, 11, 12
RING_MCP, RING_PIP, RING_DIP, RING_TIP = 13, 14, 15, 16
PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP = 17, 18, 19, 20


def _lm_to_px(lm, w: int, h: int) -> tuple[int, int]:
    return int(lm.x * w), int(lm.y * h)


def _finger_up(landmarks, tip_i: int, pip_i: int, handedness: str) -> bool:
    """Doigt levé si tip plus haut que PIP (y plus petit en image)."""
    return landmarks[tip_i].y < landmarks[pip_i].y - 0.02
    
def _thumb_up(landmarks, handedness: str) -> bool:
    """Pouce dirigé vers le haut, indépendamment de la main gauche/droite."""
    tip = landmarks[THUMB_TIP]
    ip = landmarks[THUMB_IP]
    mcp = landmarks[THUMB_MCP]
    index_mcp = landmarks[INDEX_MCP]
    return (
        tip.y < ip.y - 0.02            # le bout est au-dessus de l'articulation
        and ip.y < mcp.y               # le pouce est bien étendu vers le haut
        and tip.y < index_mcp.y - 0.04 # il dépasse le poing
    )

def _fingers_extended(landmarks, handedness: str) -> dict[str, bool]:
    return {
        "thumb": _thumb_up(landmarks, handedness),
        "index": _finger_up(landmarks, INDEX_TIP, INDEX_PIP, handedness),
        "middle": _finger_up(landmarks, MIDDLE_TIP, MIDDLE_PIP, handedness),
        "ring": _finger_up(landmarks, RING_TIP, RING_PIP, handedness),
        "pinky": _finger_up(landmarks, PINKY_TIP, PINKY_PIP, handedness),
    }


def classify_gesture(landmarks, handedness: str, w: int, h: int) -> HandState:
    ext = _fingers_extended(landmarks, handedness)
    others = [ext["middle"], ext["ring"], ext["pinky"]]
    others_down = not any(others)
    all_up = all([ext["index"], ext["middle"], ext["ring"], ext["pinky"]])

    tip = _lm_to_px(landmarks[INDEX_TIP], w, h)
    palm_ids = [WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP]
    px = [_lm_to_px(landmarks[i], w, h) for i in palm_ids]
    palm = (
        int(sum(p[0] for p in px) / len(px)),
        int(sum(p[1] for p in px) / len(px)),
    )
    all_px = [_lm_to_px(landmarks[i], w, h) for i in range(21)]

    # Pouce levé seul (ou presque) → save
    if ext["thumb"] and not ext["index"] and not ext["middle"] and not ext["ring"] and not ext["pinky"]:
        return HandState(Gesture.SAVE, tip, palm, all_px)

    # Paume ouverte → gomme
    if all_up and not ext["thumb"]:
        return HandState(Gesture.ERASE, tip, palm, all_px)
    if all_up:
        return HandState(Gesture.ERASE, tip, palm, all_px)

    # 2 doigts (index + majeur), reste baissé → select
    if ext["index"] and ext["middle"] and not ext["ring"] and not ext["pinky"]:
        return HandState(Gesture.SELECT, tip, palm, all_px)

    # 1 doigt (index seul) → draw
    if ext["index"] and others_down and not ext["thumb"]:
        return HandState(Gesture.DRAW, tip, palm, all_px)
    if ext["index"] and others_down:
        return HandState(Gesture.DRAW, tip, palm, all_px)

    return HandState(Gesture.NONE, tip, palm, all_px)


class EMAPoint:
    """Lissage Exponential Moving Average pour réduire le tremblement."""

    def __init__(self, alpha: float = 0.35):
        self.alpha = alpha
        self._x: float | None = None
        self._y: float | None = None

    def reset(self) -> None:
        self._x = None
        self._y = None

    def update(self, pt: tuple[float, float] | None) -> tuple[int, int] | None:
        if pt is None:
            self.reset()
            return None
        x, y = float(pt[0]), float(pt[1])
        if self._x is None:
            self._x, self._y = x, y
        else:
            a = self.alpha
            self._x = a * x + (1 - a) * self._x
            self._y = a * y + (1 - a) * self._y
        return int(self._x), int(self._y)

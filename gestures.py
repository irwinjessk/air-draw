"""Détection de gestes de la main à partir des landmarks MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from config import FINGER_MARGIN, THUMB_FIST_MARGIN, THUMB_TIP_MARGIN


class Gesture(Enum):
    NONE = auto()
    DRAW = auto()     # 1 doigt (index)
    SELECT = auto()   # 2 doigts (index + majeur)
    ERASE = auto()    # paume ouverte
    SAVE = auto()     # pouce levé


@dataclass
class HandState:
    gesture: Gesture
    tip: tuple[int, int]                 # bout de l'index (px)
    palm: tuple[int, int]                # centre de la paume (px)
    landmarks_px: list[tuple[int, int]]


# Indices MediaPipe Hands
WRIST = 0
THUMB_MCP, THUMB_IP, THUMB_TIP = 2, 3, 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_MCP, RING_PIP, RING_TIP = 13, 14, 16
PINKY_MCP, PINKY_PIP, PINKY_TIP = 17, 18, 20

PALM_IDS = (WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP)
FOUR_FINGERS = ("index", "middle", "ring", "pinky")


def _to_px(lm, w: int, h: int) -> tuple[int, int]:
    return int(lm.x * w), int(lm.y * h)


def _finger_up(landmarks, tip_i: int, pip_i: int) -> bool:
    """Doigt levé si le bout est plus haut que l'articulation PIP."""
    return landmarks[tip_i].y < landmarks[pip_i].y - FINGER_MARGIN


def _thumb_up(landmarks) -> bool:
    """Pouce dirigé vers le haut, indépendamment de la main gauche/droite."""
    tip = landmarks[THUMB_TIP]
    ip = landmarks[THUMB_IP]
    mcp = landmarks[THUMB_MCP]
    index_mcp = landmarks[INDEX_MCP]
    return (
        tip.y < ip.y - THUMB_TIP_MARGIN             # bout au-dessus de l'articulation
        and ip.y < mcp.y                            # pouce bien étendu vers le haut
        and tip.y < index_mcp.y - THUMB_FIST_MARGIN  # dépasse le poing
    )


def _fingers_extended(landmarks) -> dict[str, bool]:
    return {
        "thumb": _thumb_up(landmarks),
        "index": _finger_up(landmarks, INDEX_TIP, INDEX_PIP),
        "middle": _finger_up(landmarks, MIDDLE_TIP, MIDDLE_PIP),
        "ring": _finger_up(landmarks, RING_TIP, RING_PIP),
        "pinky": _finger_up(landmarks, PINKY_TIP, PINKY_PIP),
    }


def _identify(ext: dict[str, bool]) -> Gesture:
    """Associe l'état des doigts à un geste (l'ordre des tests compte)."""
    others_down = not (ext["middle"] or ext["ring"] or ext["pinky"])

    if ext["thumb"] and not any(ext[f] for f in FOUR_FINGERS):
        return Gesture.SAVE
    if all(ext[f] for f in FOUR_FINGERS):
        return Gesture.ERASE
    if ext["index"] and ext["middle"] and not ext["ring"] and not ext["pinky"]:
        return Gesture.SELECT
    if ext["index"] and others_down:
        return Gesture.DRAW
    return Gesture.NONE


def classify_gesture(landmarks, w: int, h: int) -> HandState:
    all_px = [_to_px(landmarks[i], w, h) for i in range(21)]
    palm_pts = [all_px[i] for i in PALM_IDS]
    palm = (
        int(sum(p[0] for p in palm_pts) / len(palm_pts)),
        int(sum(p[1] for p in palm_pts) / len(palm_pts)),
    )
    gesture = _identify(_fingers_extended(landmarks))
    return HandState(gesture, all_px[INDEX_TIP], palm, all_px)


class EMAPoint:
    """Lissage par moyenne mobile exponentielle (réduit le tremblement)."""

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
        if self._x is None or self._y is None:
            self._x, self._y = x, y
        else:
            a = self.alpha
            self._x = a * x + (1 - a) * self._x
            self._y = a * y + (1 - a) * self._y
        return int(self._x), int(self._y)
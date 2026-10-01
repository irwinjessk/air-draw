"""Interface : barre de couleurs, CLEAR ALL, barre d'aide, statut."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from config import (
    BGR,
    BUTTON_FONT_SCALE,
    BUTTON_GAP,
    BUTTON_PAD,
    CLEAR_ALL,
    HINT_FONT_SCALE,
    HINT_H,
    HINT_TEXT,
    MENU_H,
    MENU_OPACITY,
    PALETTE,
    STATUS_FONT_SCALE,
    WHITE,
)

FONT = cv2.FONT_HERSHEY_SIMPLEX


@dataclass
class ColorButton:
    name: str
    color_bgr: BGR
    text_color: BGR
    x1: int
    x2: int

    @property
    def is_clear(self) -> bool:
        return self.name == CLEAR_ALL


def build_buttons(frame_w: int) -> list[ColorButton]:
    n = len(PALETTE)
    usable = frame_w - 2 * BUTTON_PAD - BUTTON_GAP * (n - 1)
    bw = usable // n
    buttons: list[ColorButton] = []
    x = BUTTON_PAD
    for name, color, text_color in PALETTE:
        buttons.append(ColorButton(name, color, text_color, x, x + bw))
        x += bw + BUTTON_GAP
    return buttons


def _draw_button(frame: np.ndarray, btn: ColorButton, active: bool) -> None:
    y1, y2 = 10, MENU_H - 10
    cv2.rectangle(frame, (btn.x1, y1), (btn.x2, y2), btn.color_bgr, -1)
    cv2.rectangle(frame, (btn.x1, y1), (btn.x2, y2), WHITE, 3 if active else 1)

    (tw, th), _ = cv2.getTextSize(btn.name, FONT, BUTTON_FONT_SCALE, 2)
    tx = btn.x1 + (btn.x2 - btn.x1 - tw) // 2
    ty = y1 + (y2 - y1 + th) // 2
    cv2.putText(frame, btn.name, (tx, ty), FONT, BUTTON_FONT_SCALE, btn.text_color, 2, cv2.LINE_AA)


def draw_menu(frame: np.ndarray, buttons: list[ColorButton], active_color: BGR) -> None:
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, MENU_H), (20, 20, 20), -1)
    cv2.addWeighted(overlay, MENU_OPACITY, frame, 1 - MENU_OPACITY, 0, frame)

    for btn in buttons:
        _draw_button(frame, btn, active=(not btn.is_clear) and btn.color_bgr == active_color)

    cv2.rectangle(frame, (0, MENU_H), (w, MENU_H + HINT_H), (0, 0, 0), -1)
    cv2.putText(frame, HINT_TEXT, (12, MENU_H + 20), FONT, HINT_FONT_SCALE,
                (240, 240, 240), 1, cv2.LINE_AA)


def draw_status(frame: np.ndarray, gesture_name: str, message: str) -> None:
    """Affiche le geste détecté (debug) et le message de statut en bas."""
    h = frame.shape[0]
    cv2.putText(frame, f"Geste: {gesture_name}", (12, h - 50), FONT,
                STATUS_FONT_SCALE, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(frame, message, (12, h - 18), FONT,
                STATUS_FONT_SCALE, WHITE, 2, cv2.LINE_AA)


def hit_test(buttons: list[ColorButton], x: int, y: int) -> ColorButton | None:
    if y > MENU_H:
        return None
    for btn in buttons:
        if btn.x1 <= x <= btn.x2:
            return btn
    return None
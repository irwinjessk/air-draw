"""Barre de couleurs + CLEAR ALL."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ColorButton:
    name: str
    color_bgr: tuple[int, int, int]
    x1: int
    x2: int


MENU_H = 70
HINT_H = 28


def build_buttons(frame_w: int) -> list[ColorButton]:
    names = [
        ("BLUE", (255, 100, 40)),
        ("GREEN", (60, 200, 60)),
        ("RED", (40, 40, 255)),
        ("YELLOW", (0, 220, 255)),
        ("CLEAR ALL", (50, 50, 50)),
    ]
    n = len(names)
    gap = 8
    pad = 10
    usable = frame_w - 2 * pad - gap * (n - 1)
    bw = usable // n
    buttons: list[ColorButton] = []
    x = pad
    for name, color in names:
        buttons.append(ColorButton(name, color, x, x + bw))
        x += bw + gap
    return buttons


def draw_menu(
    frame: np.ndarray,
    buttons: list[ColorButton],
    active_color: tuple[int, int, int],
) -> None:
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, MENU_H), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    for btn in buttons:
        is_clear = btn.name == "CLEAR ALL"
        is_active = (not is_clear) and btn.color_bgr == active_color
        y1, y2 = 10, MENU_H - 10
        cv2.rectangle(frame, (btn.x1, y1), (btn.x2, y2), btn.color_bgr, -1)
        if is_active:
            cv2.rectangle(frame, (btn.x1, y1), (btn.x2, y2), (255, 255, 255), 3)
        else:
            cv2.rectangle(frame, (btn.x1, y1), (btn.x2, y2), (255, 255, 255), 1)

        label = btn.name
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        tx = btn.x1 + (btn.x2 - btn.x1 - tw) // 2
        ty = y1 + (y2 - y1 + th) // 2
        text_color = (255, 255, 255) if is_clear or btn.name in ("BLUE", "RED", "GREEN") else (20, 20, 20)
        if btn.name == "YELLOW":
            text_color = (20, 20, 20)
        cv2.putText(frame, label, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2, cv2.LINE_AA)

    # Barre d’aide
    y0 = MENU_H
    cv2.rectangle(frame, (0, y0), (w, y0 + HINT_H), (0, 0, 0), -1)
    hint = "1 Finger: Draw | 2 Fingers: Select Color | Open Palm: Eraser | Thumbs Up: Save"
    cv2.putText(
        frame,
        hint,
        (12, y0 + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (240, 240, 240),
        1,
        cv2.LINE_AA,
    )


def hit_test(buttons: list[ColorButton], x: int, y: int) -> ColorButton | None:
    if y > MENU_H:
        return None
    for btn in buttons:
        if btn.x1 <= x <= btn.x2:
            return btn
    return None

"""Calque de dessin : traits, gomme, fusion avec la vidéo, sauvegarde."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from config import BGR, BRUSH_SIZE, CANVAS_MASK_THRESHOLD, ERASER_RADIUS, OUTPUT_DIR


class DrawingCanvas:
    def __init__(self, width: int, height: int) -> None:
        self.layer = np.zeros((height, width, 3), dtype=np.uint8)

    def ensure_size(self, width: int, height: int) -> bool:
        """Recrée le calque si la taille change. Retourne True si recréé."""
        if self.layer.shape[:2] == (height, width):
            return False
        self.layer = np.zeros((height, width, 3), dtype=np.uint8)
        return True

    def clear(self) -> None:
        self.layer[:] = 0

    def draw_stroke(self, start: tuple[int, int], end: tuple[int, int], color: BGR) -> None:
        cv2.line(self.layer, start, end, color, BRUSH_SIZE, cv2.LINE_AA)
        cv2.circle(self.layer, end, BRUSH_SIZE // 2, color, -1, cv2.LINE_AA)

    def erase(self, center: tuple[int, int]) -> None:
        cv2.circle(self.layer, center, ERASER_RADIUS, (0, 0, 0), -1)

    def overlay_on(self, frame: np.ndarray) -> np.ndarray:
        """Fusionne le calque sur la vidéo (noir = transparent)."""
        gray = cv2.cvtColor(self.layer, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, CANVAS_MASK_THRESHOLD, 255, cv2.THRESH_BINARY)
        bg = cv2.bitwise_and(frame, frame, mask=cv2.bitwise_not(mask))
        fg = cv2.bitwise_and(self.layer, self.layer, mask=mask)
        return cv2.add(bg, fg)

    def save(self, output_dir: Path = OUTPUT_DIR) -> Path | None:
        """Enregistre le dessin en PNG (fond blanc). Retourne le chemin ou None."""
        output_dir.mkdir(exist_ok=True)
        path = output_dir / f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        out = np.full_like(self.layer, 255)
        drawn = cv2.cvtColor(self.layer, cv2.COLOR_BGR2GRAY) > CANVAS_MASK_THRESHOLD
        out[drawn] = self.layer[drawn]

        if cv2.imwrite(str(path), out):
            print(f"Sauvé : {path}")
            return path
        print(f"ERREUR : impossible d'écrire {path}")
        return None
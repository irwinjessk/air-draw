"""Application Air Draw : boucle principale et réactions aux gestes."""

from __future__ import annotations

import time

import cv2
import numpy as np

from camera import open_camera
from canvas import DrawingCanvas
from config import (
    DEFAULT_COLOR_NAME,
    ERASER_RADIUS,
    FLASH_DURATION,
    HINT_H,
    INITIAL_STATUS,
    MENU_H,
    SAVE_COOLDOWN,
    SMOOTHING_ALPHA,
    WINDOW_NAME,
)
from gestures import EMAPoint, Gesture, HandState
from hand_tracker import HandTracker
from ui import build_buttons, draw_menu, draw_status, hit_test


class AirDrawApp:
    def __init__(self) -> None:
        self.cap, first_frame = open_camera()
        h, w = first_frame.shape[:2]

        self.canvas = DrawingCanvas(w, h)
        self.buttons = build_buttons(w)
        self.color = next(b.color_bgr for b in self.buttons if b.name == DEFAULT_COLOR_NAME)
        self.tracker = HandTracker()
        self.smoother = EMAPoint(alpha=SMOOTHING_ALPHA)

        self.prev_pt: tuple[int, int] | None = None
        self.last_save_ts = 0.0
        self.flash_msg = ""
        self.flash_until = 0.0
        self.status = INITIAL_STATUS

    # ---------- état ----------

    def _lift_pen(self) -> None:
        """Interrompt le trait en cours (le prochain point ne sera pas relié)."""
        self.smoother.reset()
        self.prev_pt = None

    def _flash(self, message: str) -> None:
        self.flash_msg = message
        self.flash_until = time.time() + FLASH_DURATION

    def _save(self, report_error: bool) -> None:
        path = self.canvas.save()
        if path is not None:
            self._flash(f"Sauvé : {path.name}")
        elif report_error:
            self._flash("Erreur de sauvegarde")

    # ---------- réactions aux gestes ----------

    def _on_draw(self, frame: np.ndarray, tip: tuple[int, int]) -> None:
        smooth = self.smoother.update(tip)
        if smooth is not None:
            if self.prev_pt is not None:
                self.canvas.draw_stroke(self.prev_pt, smooth, self.color)
            self.prev_pt = smooth
            self.status = "Dessin"
        cv2.circle(frame, tip, 10, self.color, 2)

    def _on_select(self, frame: np.ndarray, tip: tuple[int, int]) -> None:
        self._lift_pen()
        btn = hit_test(self.buttons, tip[0], tip[1])
        if btn is None:
            self.status = "2 doigts — pointe une couleur"
        elif btn.is_clear:
            self.canvas.clear()
            self.status = "Canvas effacé"
        else:
            self.color = btn.color_bgr
            self.status = f"Couleur : {btn.name}"
        cv2.circle(frame, tip, 12, (255, 255, 255), 2)

    def _on_erase(self, frame: np.ndarray, palm: tuple[int, int]) -> None:
        self._lift_pen()
        self.canvas.erase(palm)
        cv2.circle(frame, palm, ERASER_RADIUS, (220, 220, 220), 2)
        self.status = "Gomme"

    def _on_save(self) -> None:
        self._lift_pen()
        now = time.time()
        if now - self.last_save_ts > SAVE_COOLDOWN:
            self._save(report_error=True)
            self.last_save_ts = now
        self.status = "Pouce levé — sauvegarde"

    def _handle_gesture(self, frame: np.ndarray, state: HandState | None) -> Gesture:
        gesture = state.gesture if state else Gesture.NONE
        tip = state.tip if state else None
        palm = state.palm if state else None

        if gesture == Gesture.DRAW and tip is not None and tip[1] > MENU_H + HINT_H:
            self._on_draw(frame, tip)
        elif gesture == Gesture.SELECT and tip is not None:
            self._on_select(frame, tip)
        elif gesture == Gesture.ERASE and palm is not None:
            self._on_erase(frame, palm)
        elif gesture == Gesture.SAVE:
            self._on_save()
        else:
            self._lift_pen()
            if gesture == Gesture.NONE:
                self.status = "Montre ta main"
        return gesture

    # ---------- clavier ----------

    def _handle_key(self, key: int) -> bool:
        """Retourne False pour quitter."""
        if key in (ord("q"), 27):
            return False
        if key == ord("c"):
            self.canvas.clear()
            self.status = "Canvas effacé"
        elif key == ord("s"):
            self._save(report_error=False)
        return True

    # ---------- boucle ----------

    def run(self) -> None:
        print("Air Draw démarré — q pour quitter, s pour sauvegarder, c pour effacer")
        try:
            while True:
                ok, frame = self.cap.read()
                if not ok:
                    break

                frame = cv2.flip(frame, 1)  # effet miroir (selfie)
                h, w = frame.shape[:2]
                if self.canvas.ensure_size(w, h):
                    self.buttons = build_buttons(w)

                state = self.tracker.detect(frame)
                gesture = self._handle_gesture(frame, state)

                composed = self.canvas.overlay_on(frame)
                draw_menu(composed, self.buttons, self.color)
                shown = self.flash_msg if time.time() < self.flash_until else self.status
                draw_status(composed, gesture.name, shown)

                cv2.imshow(WINDOW_NAME, composed)
                if not self._handle_key(cv2.waitKey(1) & 0xFF):
                    break
        finally:
            self.tracker.close()
            self.cap.release()
            cv2.destroyAllWindows()
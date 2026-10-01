#!/usr/bin/env python3
"""Air Draw — canvas gestuel webcam (OpenCV + MediaPipe)."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np

from gestures import EMAPoint, Gesture, classify_gesture
from ui import MENU_H, HINT_H, build_buttons, draw_menu, hit_test

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
BRUSH = 8
ERASER = 48
SAVE_COOLDOWN = 1.5   # secondes entre deux sauvegardes par geste
FLASH_DURATION = 2.0  # durée d'affichage du message "Sauvé"


def overlay_canvas(frame: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    """Fusionne le calque de dessin (noir = transparent) sur la vidéo."""
    gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 8, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
    fg = cv2.bitwise_and(canvas, canvas, mask=mask)
    return cv2.add(bg, fg)


def save_canvas(canvas: np.ndarray) -> Path | None:
    """Enregistre le dessin en PNG (fond blanc + traits). Retourne le chemin ou None."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    out = np.full_like(canvas, 255)
    mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    out[mask > 8] = canvas[mask > 8]
    ok = cv2.imwrite(str(path), out)
    if ok:
        print(f"Sauvé : {path}")
        return path
    print(f"ERREUR : impossible d'écrire {path}")
    return None


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    cap = None
    for idx in (0, 1, 2):
        trial = cv2.VideoCapture(idx)
        trial.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        trial.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        ok, frame = trial.read()
        if trial.isOpened() and ok and frame is not None:
            cap = trial
            print(f"Webcam ouverte (index {idx})")
            break
        trial.release()

    if cap is None:
        raise SystemExit(
            "Impossible d’ouvrir la webcam. Ferme Chrome/Meet/autre app qui l’utilise."
        )

    ok, frame = cap.read()
    if not ok:
        raise SystemExit("Pas d’image webcam.")

    h, w = frame.shape[:2]
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    buttons = build_buttons(w)
    color = buttons[2].color_bgr  # RED par défaut
    ema = EMAPoint(alpha=0.32)
    prev_pt: tuple[int, int] | None = None
    last_save_ts = 0.0
    flash_msg = ""
    flash_until = 0.0
    status = "Prêt — 1 doigt pour dessiner"

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    mp_styles = mp.solutions.drawing_styles

    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        model_complexity=1,
        min_detection_confidence=0.65,
        min_tracking_confidence=0.65,
    )

    print("Air Draw démarré — q pour quitter, s pour sauvegarder, c pour effacer")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)  # miroir selfie
            h, w = frame.shape[:2]
            if canvas.shape[:2] != (h, w):
                canvas = np.zeros((h, w, 3), dtype=np.uint8)
                buttons = build_buttons(w)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            gesture = Gesture.NONE
            tip = None
            palm = None

            if result.multi_hand_landmarks:
                hand_lms = result.multi_hand_landmarks[0]
                handedness = "Right"
                if result.multi_handedness:
                    # Après flip, on inverse le label MediaPipe
                    label = result.multi_handedness[0].classification[0].label
                    handedness = "Left" if label == "Right" else "Right"

                state = classify_gesture(hand_lms.landmark, handedness, w, h)
                gesture = state.gesture
                tip = state.tip
                palm = state.palm

                mp_draw.draw_landmarks(
                    frame,
                    hand_lms,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style(),
                )

            # --- Gestes ---
            if gesture == Gesture.DRAW and tip is not None and tip[1] > MENU_H + HINT_H:
                smooth = ema.update(tip)
                if smooth is not None:
                    if prev_pt is not None:
                        cv2.line(canvas, prev_pt, smooth, color, BRUSH, cv2.LINE_AA)
                        cv2.circle(canvas, smooth, BRUSH // 2, color, -1, cv2.LINE_AA)
                    prev_pt = smooth
                    status = "Dessin"
                cv2.circle(frame, tip, 10, color, 2)
            elif gesture == Gesture.SELECT and tip is not None:
                ema.reset()
                prev_pt = None
                btn = hit_test(buttons, tip[0], tip[1])
                if btn is not None:
                    if btn.name == "CLEAR ALL":
                        canvas[:] = 0
                        status = "Canvas effacé"
                    else:
                        color = btn.color_bgr
                        status = f"Couleur : {btn.name}"
                else:
                    status = "2 doigts — pointe une couleur"
                cv2.circle(frame, tip, 12, (255, 255, 255), 2)
            elif gesture == Gesture.ERASE and palm is not None:
                ema.reset()
                prev_pt = None
                cv2.circle(canvas, palm, ERASER, (0, 0, 0), -1)
                cv2.circle(frame, palm, ERASER, (220, 220, 220), 2)
                status = "Gomme"
            elif gesture == Gesture.SAVE:
                ema.reset()
                prev_pt = None
                now = time.time()
                if now - last_save_ts > SAVE_COOLDOWN:
                    path = save_canvas(canvas)
                    last_save_ts = now
                    if path is not None:
                        flash_msg = f"Sauvé : {path.name}"
                    else:
                        flash_msg = "Erreur de sauvegarde"
                    flash_until = now + FLASH_DURATION
                status = "Pouce levé — sauvegarde"
            else:
                ema.reset()
                prev_pt = None
                if gesture == Gesture.NONE:
                    status = "Montre ta main"

            composed = overlay_canvas(frame, canvas)
            draw_menu(composed, buttons, color)

            # Geste détecté (utile pour déboguer)
            cv2.putText(
                composed,
                f"Geste: {gesture.name}",
                (12, h - 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Message de statut (le message de sauvegarde reste visible quelques secondes)
            shown = flash_msg if time.time() < flash_until else status
            cv2.putText(
                composed,
                shown,
                (12, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Air Draw", composed)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("c"):
                canvas[:] = 0
                status = "Canvas effacé"
            if key == ord("s"):
                path = save_canvas(canvas)
                if path is not None:
                    flash_msg = f"Sauvé : {path.name}"
                    flash_until = time.time() + FLASH_DURATION

    finally:
        hands.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
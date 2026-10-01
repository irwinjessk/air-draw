"""Constantes de configuration d'Air Draw."""

from __future__ import annotations

from pathlib import Path

BGR = tuple[int, int, int]

# --- Chemins ---
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

# --- Webcam / fenêtre ---
CAMERA_INDICES = (0, 1, 2)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
WINDOW_NAME = "Air Draw"

# --- MediaPipe ---
MAX_HANDS = 1
MODEL_COMPLEXITY = 1
MIN_DETECTION_CONFIDENCE = 0.65
MIN_TRACKING_CONFIDENCE = 0.65

# --- Dessin ---
BRUSH_SIZE = 8
ERASER_RADIUS = 48
SMOOTHING_ALPHA = 0.32
CANVAS_MASK_THRESHOLD = 8   # en dessous : pixel considéré comme transparent
SAVE_COOLDOWN = 1.5         # secondes entre deux sauvegardes par geste
FLASH_DURATION = 2.0        # durée d'affichage du message "Sauvé"

# --- Seuils de détection des gestes (coordonnées normalisées 0..1) ---
FINGER_MARGIN = 0.02
THUMB_TIP_MARGIN = 0.02
THUMB_FIST_MARGIN = 0.04

# --- Interface ---
MENU_H = 70
HINT_H = 28
BUTTON_GAP = 8
BUTTON_PAD = 10
BUTTON_FONT_SCALE = 0.55
HINT_FONT_SCALE = 0.48
STATUS_FONT_SCALE = 0.65
MENU_OPACITY = 0.65

CLEAR_ALL = "CLEAR ALL"
DEFAULT_COLOR_NAME = "RED"

WHITE: BGR = (255, 255, 255)
DARK: BGR = (20, 20, 20)

# (nom, couleur BGR, couleur du texte)
PALETTE: list[tuple[str, BGR, BGR]] = [
    ("BLUE", (255, 100, 40), WHITE),
    ("GREEN", (60, 200, 60), WHITE),
    ("RED", (40, 40, 255), WHITE),
    ("YELLOW", (0, 220, 255), DARK),
    (CLEAR_ALL, (50, 50, 50), WHITE),
]

HINT_TEXT = "1 Finger: Draw | 2 Fingers: Select Color | Open Palm: Eraser | Thumbs Up: Save"
INITIAL_STATUS = "Prêt — 1 doigt pour dessiner"
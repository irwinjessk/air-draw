"""Ouverture de la webcam."""

from __future__ import annotations

import cv2
import numpy as np

from config import CAMERA_INDICES, FRAME_HEIGHT, FRAME_WIDTH


def open_camera() -> tuple[cv2.VideoCapture, np.ndarray]:
    """Essaie les index de caméra configurés. Retourne (capture, première frame)."""
    for idx in CAMERA_INDICES:
        cap = cv2.VideoCapture(idx)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        ok, frame = cap.read()
        if cap.isOpened() and ok and frame is not None:
            print(f"Webcam ouverte (index {idx})")
            return cap, frame
        cap.release()

    raise SystemExit(
        "Impossible d’ouvrir la webcam. Ferme Chrome/Meet/autre app qui l’utilise."
    )
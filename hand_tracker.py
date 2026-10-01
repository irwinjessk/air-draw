"""Wrapper MediaPipe Hands : détection + classification du geste."""

from __future__ import annotations

import cv2
import mediapipe as mp
import numpy as np

from config import (
    MAX_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    MODEL_COMPLEXITY,
)
from gestures import HandState, classify_gesture


class HandTracker:
    def __init__(self) -> None:
        self._mp_hands = mp.solutions.hands
        self._mp_draw = mp.solutions.drawing_utils
        self._mp_styles = mp.solutions.drawing_styles
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            model_complexity=MODEL_COMPLEXITY,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

    def detect(self, frame: np.ndarray, draw: bool = True) -> HandState | None:
        """Analyse une frame BGR. Dessine le squelette de la main si draw=True."""
        h, w = frame.shape[:2]
        result = self._hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not result.multi_hand_landmarks:
            return None

        hand_lms = result.multi_hand_landmarks[0]
        state = classify_gesture(hand_lms.landmark, w, h)

        if draw:
            self._mp_draw.draw_landmarks(
                frame,
                hand_lms,
                self._mp_hands.HAND_CONNECTIONS,
                self._mp_styles.get_default_hand_landmarks_style(),
                self._mp_styles.get_default_hand_connections_style(),
            )
        return state

    def close(self) -> None:
        self._hands.close()
# ✋🎨 Air Draw

**Dessine dans les airs avec ta main.** Air Draw est une application de dessin sans contact : une webcam, une main, et quelques lignes de Python suffisent. Pas de souris, pas de clavier, pas d'écran tactile.

Le projet s'appuie sur la **vision par ordinateur** (Computer Vision), le **suivi de la main** (Hand Tracking) et la **reconnaissance de gestes** (Hand Gesture Recognition) pour transformer des mouvements naturels en interface utilisateur.

> 📸 *Ajoute ici un GIF ou une capture d'écran de démonstration (`docs/demo.gif`).*
>
> `![Démo Air Draw](docs/demo.gif)`

---

## ✨ Fonctionnalités

- Détection de la main en temps réel avec **21 points de repère** (landmarks) via MediaPipe
- Dessin au doigt sur un canvas virtuel superposé au flux vidéo
- Menu de couleurs sélectionnable par geste (Bleu, Vert, Rouge, Jaune) et bouton **Clear All**
- Gomme contrôlée par la paume de la main
- Lissage du tracé par **Exponential Moving Average (EMA)** pour réduire les tremblements
- Sauvegarde du dessin en **PNG** (fond blanc) par un simple pouce levé
- Affichage en direct du geste détecté, pratique pour déboguer

---

## 🖐️ Gestes

| Geste | Action |
|-------|--------|
| ☝️ Index seul levé | **Dessiner** |
| ✌️ Index + majeur levés | **Sélectionner** une couleur ou *Clear All* (pointe le bouton dans le menu) |
| 🖐️ Paume ouverte (4 doigts levés) | **Gommer** |
| 👍 Pouce levé, autres doigts repliés | **Sauvegarder** le dessin dans `output/` |

### Raccourcis clavier

| Touche | Action |
|--------|--------|
| `s` | Sauvegarder le dessin |
| `c` | Effacer le canvas |
| `q` ou `Échap` | Quitter |

---

## ⚙️ Comment ça marche

```
Webcam
  ↓  OpenCV capture le flux vidéo (image miroir)
MediaPipe Hands
  ↓  détecte la main et ses 21 landmarks
gestures.py
  ↓  analyse la position des doigts → DRAW / SELECT / ERASE / SAVE / NONE
main.py
  ↓  transforme le geste en action (trait, couleur, gomme, sauvegarde)
Canvas virtuel (NumPy)
  ↓  fusionné avec la vidéo, puis affiché avec OpenCV
output/drawing_AAAAMMJJ_HHMMSS.png
```

1. **Capture** : OpenCV lit la webcam et retourne l'image comme un miroir.
2. **Détection** : MediaPipe Hands localise la main et ses 21 points de repère.
3. **Reconnaissance** : une couche dédiée compare la position des extrémités des doigts à leurs articulations pour déterminer quels doigts sont levés, puis en déduit le geste.
4. **Action** : en mode dessin, la position de l'index est lissée (EMA) puis reliée au point précédent pour former un trait sur le canvas.
5. **Affichage** : le canvas (fond noir = transparent) est superposé à la vidéo, avec le menu et les informations d'état.

---

## 📁 Structure du projet

```
air-draw/
├── main.py            # Boucle principale : webcam, gestes → actions, affichage, sauvegarde
├── gestures.py        # Classification des gestes + lissage EMA
├── ui.py              # Menu de couleurs (boutons, affichage, détection de survol)
├── requirements.txt   # Dépendances Python
├── .gitignore
└── output/            # Dessins sauvegardés (créé automatiquement, ignoré par Git)
```

---

## 🚀 Installation

**Prérequis** : Python 3.10 (ou version compatible avec MediaPipe) et une webcam.

```bash
# 1. Cloner le dépôt
git clone https://github.com/TON_USERNAME/air-draw.git
cd air-draw

# 2. Créer et activer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python main.py
```

---

## 🎮 Utilisation

1. Lance `python main.py` et place ta main devant la webcam, bien éclairée.
2. Lève l'**index** pour dessiner.
3. Lève **index + majeur** et pointe une couleur du menu pour la choisir.
4. Ouvre la **paume** pour gommer.
5. Fais un **pouce levé** (poing fermé, pouce bien vertical) pendant environ 1 seconde pour sauvegarder. Le fichier apparaît dans `output/`.

Une temporisation de 1,5 s évite de créer plusieurs fichiers à la suite.

---

## 🔧 Paramètres modifiables

| Paramètre | Fichier | Rôle |
|-----------|---------|------|
| `BRUSH` | `main.py` | Épaisseur du pinceau |
| `ERASER` | `main.py` | Rayon de la gomme |
| `EMAPoint(alpha=0.32)` | `main.py` | Lissage : plus petit = plus fluide mais plus lent |
| `min_detection_confidence`, `min_tracking_confidence` | `main.py` | Sensibilité de MediaPipe |
| Seuils des doigts | `gestures.py` | Ajustent la reconnaissance de chaque geste |

---

## 🩺 Dépannage

- **« Impossible d'ouvrir la webcam »** : ferme les applications qui l'utilisent (Chrome, Meet, Zoom...).
- **Un geste n'est pas reconnu** : regarde la ligne `Geste: ...` affichée en bas de la fenêtre pour voir ce que le programme comprend, puis ajuste ton geste ou les seuils dans `gestures.py`.
- **Avertissements Qt / Wayland / protobuf dans le terminal** : ils sont sans gravité et n'empêchent pas l'application de fonctionner.

---

## 🛠️ Technologies

- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) : capture vidéo, dessin, interface
- [MediaPipe](https://developers.google.com/mediapipe) : Hand Tracking
- [NumPy](https://numpy.org/) : manipulation du canvas

---

## 🗺️ Pistes d'amélioration

- [ ] Réglage de l'épaisseur du pinceau par geste
- [ ] Annuler / rétablir (undo / redo)
- [ ] Prise en charge de deux mains
- [ ] Export en SVG
- [ ] Reconnaissance de gestes personnalisables

---

## 👤 Auteur

Projet réalisé par [@irwin_jess](https://github.com/irwinjessk/air-draw.git).

Les retours et suggestions sont les bienvenus : ouvre une *issue* ou propose une *pull request*.

---

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
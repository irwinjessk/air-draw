# Air Draw

Dessine dans l’air avec ta main et la webcam (Python · OpenCV · MediaPipe).

```
/home/djriga/SCOUT/
├── foulard-ar/
├── finger-frame-ar/
└── air-draw/          ← ce projet
```

## Gestes

| Geste | Action |
|--------|--------|
| **1 doigt** (index) | Dessiner |
| **2 doigts** (index + majeur) | Choisir une couleur / Clear dans le menu du haut |
| **Paume ouverte** | Gomme (centre de la paume) |
| **Pouce levé** | Sauvegarder le dessin (`output/drawing_*.png`) |

## Lancer

```bash
cd /home/djriga/SCOUT/air-draw
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Touches clavier :
- `c` — clear
- `s` — save
- `q` / `Esc` — quitter

"""
Detectare forme geometrice: cercuri, patrate/dreptunghiuri, triunghiuri
Foloseste doar contururi - fara HoughCircles
"""

import cv2
import numpy as np
from tkinter import Tk, filedialog

# ── Selectie imagine ───────────────────────────────────────────
root = Tk()
root.withdraw()
path = filedialog.askopenfilename(
    title="Selecteaza o imagine",
    filetypes=[("Imagini", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Toate", "*.*")]
)
root.destroy()

if not path:
    print("Nicio imagine selectata.")
    exit()

img = cv2.imread(path)
if img is None:
    print("Nu pot deschide imaginea.")
    exit()

output = img.copy()
h_img, w_img = img.shape[:2]
MIN_AREA = w_img * h_img * 0.005   # minim 0.5% din imagine

# ── Preprocesare ───────────────────────────────────────────────
gray    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (7, 7), 0)
edges   = cv2.Canny(blurred, 50, 150)
kernel  = np.ones((3, 3), np.uint8)
edges   = cv2.dilate(edges, kernel, iterations=1)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

counts = {"Cerc": 0, "Patrat": 0, "Dreptunghi": 0, "Triunghi": 0}

# Sorteaza descrescator dupa arie - formele mari au prioritate
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Tine evidenta bounding box-urilor deja etichetate ca sa nu se suprapuna
labeled_boxes = []

def overlaps(x, y, w, h):
    """Returneaza True daca bbox-ul se suprapune cu unul deja etichetat."""
    for (bx, by, bw, bh) in labeled_boxes:
        ix = max(x, bx)
        iy = max(y, by)
        iw = min(x+w, bx+bw) - ix
        ih = min(y+h, by+bh) - iy
        if iw > 0 and ih > 0:
            overlap_area = iw * ih
            own_area     = w * h
            if overlap_area / own_area > 0.4:
                return True
    return False

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < MIN_AREA:
        continue

    perimeter = cv2.arcLength(cnt, True)
    if perimeter == 0:
        continue

    # Solidity - ignora forme concave (zgomot, text, UI)
    hull      = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    if hull_area == 0:
        continue
    solidity = area / hull_area
    if solidity < 0.80:
        continue

    approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
    n      = len(approx)
    circularity = 4 * np.pi * area / (perimeter ** 2)

    x, y, w, h = cv2.boundingRect(approx)
    cx = x + w // 2
    cy = y + h // 2

    # Sari daca se suprapune cu o forma deja detectata
    if overlaps(x, y, w, h):
        continue

    # ── Clasificare ──
    if n == 3:
        label = "Triunghi"
        color = (50, 200, 50)
        counts["Triunghi"] += 1

    elif n == 4:
        aspect = w / float(h)
        label  = "Patrat" if 0.85 <= aspect <= 1.15 else "Dreptunghi"
        color  = (80, 80, 255)
        counts["Patrat" if label == "Patrat" else "Dreptunghi"] += 1

    elif n >= 6 and circularity > 0.75:
        label = "Cerc"
        color = (0, 200, 255)
        counts["Cerc"] += 1

    else:
        continue

    labeled_boxes.append((x, y, w, h))
    cv2.drawContours(output, [approx], -1, color, 3)

    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.65, 2)
    cv2.rectangle(output, (cx - tw//2 - 4, cy - th - 6),
                           (cx + tw//2 + 4, cy + 4), (20, 20, 20), -1)
    cv2.putText(output, label, (cx - tw//2, cy),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

# ── Rezumat ────────────────────────────────────────────────────
summary = [
    f"Cercuri:       {counts['Cerc']}",
    f"Patrate:       {counts['Patrat']}",
    f"Dreptunghiuri: {counts['Dreptunghi']}",
    f"Triunghiuri:   {counts['Triunghi']}",
]
for i, line in enumerate(summary):
    cv2.putText(output, line, (12, 30 + i*28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0), 4)
    cv2.putText(output, line, (12, 30 + i*28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255,255,255), 2)

# ── Afisare ────────────────────────────────────────────────────
max_dim = 1000
h0, w0  = output.shape[:2]
scale   = min(max_dim / w0, max_dim / h0, 1.0)
if scale < 1.0:
    output = cv2.resize(output, (int(w0*scale), int(h0*scale)), interpolation=cv2.INTER_AREA)

cv2.imshow("Detectare forme  [apasa orice tasta pentru a inchide]", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
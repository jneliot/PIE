import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk
from scipy.misc import derivative
from scipy.optimize import fsolve

épaisseur = 1

## Dessiner les tangentes sur l'image
def dessinerTangentes(image, resultatsTangentes, ellipse):
    # Récupération des résultats calculés
    ordonneeCentreEllipse = resultatsTangentes["centreEllipse"][1]
    (abscisseGauche, ordonneeBase) = resultatsTangentes["intersectionGauche"]
    abscisseDroite = resultatsTangentes["intersectionDroite"][0]
    abscisseCentreBase = abscisseGauche+(abscisseDroite-abscisseGauche)/2
    penteGauche, penteDroite = resultatsTangentes["penteGauche"], resultatsTangentes["penteDroite"]
    f = resultatsTangentes["fonctionEllipse"]

    def h(x):
        return f(x)
    
    dessinerCourbe(image, h, x_min=abscisseGauche, x_max=abscisseDroite, couleur=(255, 255, 255))

    def T(m, x, x0):
        return m*(x-x0)+ordonneeBase

    # Fonction pour tracer une ligne représentant une tangente
    def tracerLigneTangente(m, x0, couleur):
        longueur = 100  # Longueur de la tangente affichée
        x1 = int(x0 - longueur)
        x2 = int(x0 + longueur)
        y1 = int(T(m, x1, x0))
        y2 = int(T(m, x2, x0))

        cv2.line(image, (x1, y1), (x2, y2), couleur, 1)

    # Tracer les tangentes en utilisant les fonctions calculées
    tracerLigneTangente(penteGauche, abscisseGauche, (0, 255, 0))  # Vert
    tracerLigneTangente(penteDroite, abscisseDroite, (255, 0, 0))  # Rouge

def dessinerCourbe(image, f, x_min, x_max, pas=1, couleur=(0, 255, 0)):
    hauteur, largeur = image.shape[:2]
    points = []

    for x in range(int(x_min), int(x_max), pas):
        try:
            y = f(x)  # Calcul de y
            if not np.isnan(y) and not np.isinf(y):  # Vérification que y est valide
                x_cv = int(x)  # Conversion en coordonnées OpenCV
                y_cv = int(hauteur - y)  # OpenCV a un axe y inversé
                points.append((x_cv, y_cv))
        except:
            pass  # Ignore les erreurs (division par zéro, valeurs infinies...)

    if len(points) > 1:
        cv2.polylines(image, [np.array(points, np.int32)], isClosed=False, color=couleur, thickness=épaisseur)

def dessinerBaseGoutte(image, baseGauche, baseDroite):
    """Trace la ligne représentant la base de la goutte."""
    cv2.line(image, baseGauche, baseDroite, (255, 0, 255), 1)  # Violet

def dessinerCroix(image, x, y, couleur, taille=5, épaisseur=1):
    """Dessine une croix fine à la position (x, y)."""
    x, y = int(x), int(y)
    cv2.line(image, (x - taille, y - taille), (x + taille, y + taille), couleur, épaisseur)
    cv2.line(image, (x - taille, y + taille), (x + taille, y - taille), couleur, épaisseur)

## Dessiner les points d'intérêt sur l'image
def dessinerPoints(image, points):
    """Affiche les points sous forme de croix fines."""
    couleur = (255, 255, 255)  # Blanc
    for point in points:
        dessinerCroix(image, point[0], point[1], couleur)
        couleur = (max(0, 255-(1/5)*couleur[0]), max(0, 255-(1/5)*couleur[0]), max(0, 255-(1/5)*couleur[0]))

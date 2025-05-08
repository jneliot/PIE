import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk
from scipy.misc import derivative
from scipy.optimize import fsolve

épaisseur = 1

## Prétraitement de l'image
def pretraiterImage(cheminImage):
    """
    Applique un prétraitement avancé à une image :
    - Conversion en niveaux de gris
    - Réduction du bruit avec un flou gaussien
    - Détection et suppression des artefacts lumineux avec un seuillage adaptatif et un inpainting
    - Détection des contours avec Canny

    :param cheminImage: Chemin vers l'image à traiter.
    :return: Image originale et image avec contours détectés.
    """
    # Charger l'image
    image = cv2.imread(cheminImage)
    if image is None:
        raise ValueError("L'image n'a pas pu être chargée. Assurez-vous qu'elle est valide.")

    # Conversion en niveaux de gris
    imageGrise = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Contraste
    imageContraste = cv2.convertScaleAbs(imageGrise, alpha=1.2, beta=-20)

    # Application d'un flou gaussien pour réduire le bruit
    imageFloue = cv2.GaussianBlur(imageContraste, (5, 5), 0)

    # Détection des contours avec Canny
    imageContours = cv2.Canny(imageFloue, 50, 50)

    # Affichage du résultat pour vérifier le traitement
    #cv2.imshow("Image Améliorée", imageFloue)
    #cv2.imshow("Contours", imageContours)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return image, imageContours

## Trouver le plus grand contour
def trouverPlusGrandContour(imageContours):
    contours, _ = cv2.findContours(imageContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Aucun contour détecté.")
    return max(contours, key=cv2.contourArea)

## Ajuster une ellipse
def ajusterEllipse(image, contourGoutte):
    ellipse = cv2.fitEllipse(contourGoutte)
    cv2.ellipse(image, ellipse, (255, 0, 0), épaisseur)
    return ellipse

## Identifier la base de la goutte (sol)
def trouverBaseGoutte(image, contourGoutte, ellipse):
    (xE, yE), (a, b), angle = ellipse
    x, y, largeur, hauteur = cv2.boundingRect(contourGoutte)
    centreBase = (int(xE), y + hauteur)

    delta_x=b*math.sqrt(1-((y + hauteur-yE)/a)**2)

    baseGauche = (x, y + hauteur)
    baseDroite = (x + largeur, y + hauteur)

    print("h_réelle(xE)=", yE-a/2)

   
    """cv2.drawContours(image, [contourGoutte], -1, (0, 255, 0), 1)
    x, y, largeur, hauteur = cv2.boundingRect(contourGoutte)
    baseGauche = (x, y + hauteur)
    baseDroite = (x + largeur, y + hauteur)
    centreBase = (x + largeur/2,y + hauteur) """

    print(baseGauche, baseDroite, centreBase)

    return baseGauche, baseDroite, centreBase

## Calculer les angles des tangentes et les intersections ellipse/base
def calculerTangentes(ellipse, baseGoutte):
    # Extraction des paramètres de l'ellipse
    (centreX, centreY), (axeA, axeB), theta = ellipse
    axeA, axeB = axeA / 2, axeB / 2  # Convertir en demi-axes
    baseGauche, baseDroite, centreBase = baseGoutte
    ordonneeBase = baseGauche[1]  # Y de la base

    # Calcul des vraies intersections avec l'ellipse
    abscisseGauche = baseGauche[0]
    abscisseDroite = baseDroite[0]

    theta=math.radians(theta)
    
    def f(x):
        def equationEllipse(y):
            # Appliquer la rotation inverse
            x_prime = (x - centreX) * np.cos(theta) + (y - centreY) * np.sin(theta)
            y_prime = -(x - centreX) * np.sin(theta) + (y - centreY) * np.cos(theta)
            
            # Équation de l'ellipse dans le repère tourné
            return (x_prime ** 2) / (axeA ** 2) + (y_prime ** 2) / (axeB ** 2) - 1
        
        # Utilisation de fsolve pour trouver y
        y_init = centreY + axeB  # Estimation initiale pour la résolution
        y_solution = fsolve(equationEllipse, y_init)[0]

        return y_solution
    
    """def f(x):
        try:
            return centreY + axeB * math.sqrt(max(1 - ((x - centreX) / axeA) ** 2, 0))
        except:
            pass  # Ignore les erreurs (division par zéro, valeurs infinies...)"""

    # Calcul des angles des tangentes
    penteGauche = -derivative(f, abscisseGauche, dx=1e-6)
    penteDroite = -derivative(f, abscisseDroite, dx=1e-6)

    # Renvoi des résultats avec les équations des tangentes
    return {
        "fonctionEllipse": f,
        "penteGauche": penteGauche,
        "penteDroite": penteDroite,
        "centreEllipse": (centreX, centreY),
        "intersectionGauche": (abscisseGauche, ordonneeBase),
        "intersectionDroite": (abscisseDroite, ordonneeBase)
    }

import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk
from scipy.misc import derivative
from scipy.optimize import fsolve

épaisseur = 1

# Étape 1 : Prétraitement de l'image
def pretraiterImage(cheminImage):
    image = cv2.imread(cheminImage)
    if image is None:
        raise ValueError("L'image n'a pas pu être chargée. Assurez-vous qu'elle est valide.")

    imageGrise = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    imageFloue = cv2.GaussianBlur(imageGrise, (5, 5), 0)
    imageContours = cv2.Canny(imageFloue, 50, 50)

    return image, imageContours

# Étape 2 : Trouver le plus grand contour
def trouverPlusGrandContour(imageContours):
    contours, _ = cv2.findContours(imageContours, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("Aucun contour détecté.")
    return max(contours, key=cv2.contourArea)

# Étape 3 : Ajuster une ellipse
def ajusterEllipse(image, contourGoutte):
    ellipse = cv2.fitEllipse(contourGoutte)
    cv2.ellipse(image, ellipse, (255, 0, 0), épaisseur)
    return ellipse

#  🚩 Étape 4 : Identifier la base de la goutte (sol)
def trouverBaseGoutte(image, contourGoutte, ellipse):
    (xE, yE), (a, b), angle = ellipse
    x, y, largeur, hauteur = cv2.boundingRect(contourGoutte)
    centreBase = (int(xE), y + hauteur)

    delta_x=b*math.sqrt(1-((y + hauteur-yE)/a)**2)

    baseGauche = (int(xE-delta_x/2), y + hauteur)
    baseDroite = (int(xE+delta_x/2), y + hauteur)

    print("h_réelle(xE)=", yE-a/2)

   
    """cv2.drawContours(image, [contourGoutte], -1, (0, 255, 0), 1)
    x, y, largeur, hauteur = cv2.boundingRect(contourGoutte)
    baseGauche = (x, y + hauteur)
    baseDroite = (x + largeur, y + hauteur)
    centreBase = (x + largeur/2,y + hauteur) """

    print(baseGauche, baseDroite, centreBase)

    return baseGauche, baseDroite, centreBase

# Étape 5 : Calculer les angles des tangentes et les intersections ellipse/base
def calculerTangentes(ellipse, baseGoutte):
    # Extraction des paramètres de l'ellipse
    (centreX, centreY), (axeA, axeB), theta = ellipse
    axeA, axeB = axeA / 2, axeB / 2  # Convertir en demi-axes
    baseGauche, baseDroite, centreBase = baseGoutte
    ordonneeBase = baseGauche[1]  # Y de la base

    # ✅ Calcul des vraies intersections avec l'ellipse
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

    # ✅ Calcul des angles des tangentes
    penteGauche = -derivative(f, abscisseGauche, dx=1e-6)
    penteDroite = -derivative(f, abscisseDroite, dx=1e-6)

    # ✅ Renvoi des résultats avec les équations des tangentes
    return {
        "fonctionEllipse": f,
        "penteGauche": penteGauche,
        "penteDroite": penteDroite,
        "centreEllipse": (centreX, centreY),
        "intersectionGauche": (abscisseGauche, ordonneeBase),
        "intersectionDroite": (abscisseDroite, ordonneeBase)
    }

# 🔹 Étape 6 : Dessiner les tangentes sur l'image
def dessinerTangentes(image, resultatsTangentes, ellipse):
    # Récupération des résultats calculés
    ordonneeCentreEllipse = resultatsTangentes["centreEllipse"][1]
    (abscisseGauche, ordonneeBase) = resultatsTangentes["intersectionGauche"]
    abscisseDroite = resultatsTangentes["intersectionDroite"][0]
    abscisseCentreBase = abscisseGauche+(abscisseDroite-abscisseGauche)/2
    penteGauche, penteDroite = resultatsTangentes["penteGauche"], resultatsTangentes["penteDroite"]
    f = resultatsTangentes["fonctionEllipse"]

    """def h(x):
        return f(x)
    
    dessinerCourbe(image, h, x_min=abscisseGauche, x_max=abscisseDroite, couleur=(255, 255, 255))"""

    def T(m, x, x0):
        return m*(x-x0)+ordonneeBase

    # 🔹 Fonction pour tracer une ligne représentant une tangente
    def tracerLigneTangente(m, x0, couleur):
        longueur = 100  # Longueur de la tangente affichée
        x1 = int(x0 - longueur)
        x2 = int(x0 + longueur)
        y1 = int(T(m, x1, x0))
        y2 = int(T(m, x2, x0))

        cv2.line(image, (x1, y1), (x2, y2), couleur, 1)

    # 🔹 Tracer les tangentes en utilisant les fonctions calculées
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

# Étape 7 : Dessiner les points d'intérêt sur l'image
def dessinerPoints(image, points):
    """Affiche les points sous forme de croix fines."""
    couleur = (255, 255, 255)  # Blanc
    for point in points:
        dessinerCroix(image, point[0], point[1], couleur)
        couleur = (max(0, 255-(1/5)*couleur[0]), max(0, 255-(1/5)*couleur[0]), max(0, 255-(1/5)*couleur[0]))

# Interface graphique
def interface():
    root = tk.Tk()
    root.title("Analyse de Goutte d'Eau")
    root.geometry("550x550")

    Label(root, text="Chargez une image pour analyser les angles des tangentes",
          font=("Arial", 12), wraplength=500, justify="center").pack(pady=10)

    # 🔹 Ajout de l'initialisation du label pour éviter l'erreur
    chargementAffichage = Label(root, text="", font=("Arial", 12))
    chargementAffichage.pack()

    def choisirImage():
        cheminImage = filedialog.askopenfilename(title="Choisir une image",
                                                filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if cheminImage:
            chargementAffichage.config(text="Traitement en cours...")
            root.update()

            try:
                imageOriginale, imageContours = pretraiterImage(cheminImage)
                contourGoutte = trouverPlusGrandContour(imageContours)
                ellipse = ajusterEllipse(imageOriginale, contourGoutte)
                baseGoutte = trouverBaseGoutte(imageOriginale, contourGoutte, ellipse)
                tangentes = calculerTangentes(ellipse, baseGoutte)

                dessinerTangentes(imageOriginale, tangentes, ellipse)
                dessinerBaseGoutte(imageOriginale, baseGoutte[0], baseGoutte[1])
                dessinerPoints(imageOriginale, [ellipse[0], baseGoutte[2], tangentes["intersectionGauche"], tangentes["intersectionDroite"]])


                imageTK = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageOriginale, cv2.COLOR_BGR2RGB)))
                imageAffichage.config(image=imageTK)
                imageAffichage.image = imageTK

                cv2.imwrite("image_resultat.png", imageOriginale)

                angleGauche, angleDroit = -math.degrees(math.atan(tangentes['penteGauche'])), -math.degrees(math.atan(tangentes['penteDroite']))
                angleValeursAffichage.config(text=f"{angleGauche:.2f}° | {angleDroit:.2f}°", fg="red")


            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
            finally:
                chargementAffichage.config(text="")

    Button(root, text="Charger une image", font=("Arial", 12), command=choisirImage).pack(pady=20)

    # 🔹 Ajout des autres labels nécessaires
    imageAffichage = Label(root)
    imageAffichage.pack(pady=20)

    angleAffichage = Label(root, text="", font=("Arial", 14))
    angleAffichage.pack(pady=10)

    angleValeursAffichage = Label(root, text="", font=("Arial", 14))
    angleValeursAffichage.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    interface()

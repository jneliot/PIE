#! /home/pie12/Desktop/PIE/env python3

import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk
from scipy.misc import derivative
from scipy.optimize import fsolve

import pretraitement as pre
import affichage as aff
import camera_link as cam
import cache_management as cache

## Interface graphique
def interface():
    root = tk.Tk()
    root.title("Analyse de Goutte d'Eau")
    root.geometry("550x550")
    root.attributes("-fullscreen", True)

    Label(root, text="Chargez une image pour analyser les angles des tangentes",
          font=("Arial", 12), wraplength=500, justify="center").pack(pady=10)

    # Ajout de l'initialisation du label pour éviter l'erreur
    chargementAffichage = Label(root, text="", font=("Arial", 12))
    chargementAffichage.pack()
    
    def choisirImage():
        
        cheminImage = filedialog.askopenfilename(title="Choisir une image",)
        ## cam.get_photo()
        ## cheminImage = "../cache/temp.jpg"
        if cheminImage:
            chargementAffichage.config(text="Traitement en cours...")
            root.update()

            try:
                imageOriginale, imageContours = pre.pretraiterImage(cheminImage)
                contourGoutte = pre.trouverPlusGrandContour(imageContours)
                ellipse = pre.ajusterEllipse(imageOriginale, contourGoutte)
                baseGoutte = pre.trouverBaseGoutte(imageOriginale, contourGoutte, ellipse)
                tangentes = pre.calculerTangentes(ellipse, baseGoutte)

                aff.dessinerTangentes(imageOriginale, tangentes, ellipse)
                aff.dessinerBaseGoutte(imageOriginale, baseGoutte[0], baseGoutte[1])
                aff.dessinerPoints(imageOriginale, [ellipse[0], baseGoutte[2], tangentes["intersectionGauche"], tangentes["intersectionDroite"]])

                imageTK = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageOriginale, cv2.COLOR_BGR2RGB)))
                imageAffichage.config(image=imageTK)
                imageAffichage.image = imageTK

                angleGauche, angleDroit = -math.degrees(math.atan(tangentes['penteGauche'])), -math.degrees(math.atan(tangentes['penteDroite']))
                angleValeursAffichage.config(text=f"{angleGauche:.2f}° | {angleDroit:.2f}°", fg="red")

                cache.pre_cache()
                cv2.imwrite("../cache/temp1.png", imageOriginale)
                cache.update_cache([angleGauche, angleDroit])

            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
            finally:
                chargementAffichage.config(text="")
    
    def afficherImageCache():
        try:
            selection = listboxCache.curselection()
            if selection:
                index = selection[0]
                imagePath = f"../cache/temp{index + 1}.jpg"
                imageOriginale = cv2.imread(imagePath)
                if imageOriginale is not None:
                    imageTK = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(imageOriginale, cv2.COLOR_BGR2RGB)))
                    imageAffichage.config(image=imageTK)
                    imageAffichage.image = imageTK

                    # Afficher les angles correspondants
                    angles = cache.get_cache_angles(index)
                    angleValeursAffichage.config(text=angles[0]+"° | " + angles[1] + "°", fg="red")
                else:
                    messagebox.showerror("Erreur", "L'image sélectionnée n'existe pas dans le cache.")
            else:
                messagebox.showwarning("Avertissement", "Veuillez sélectionner une image dans la liste.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
    
    Button(root, text="Charger une image", font=("Arial", 12), command=choisirImage).pack(pady=20)

    # Ajout des autres labels nécessaires
    imageAffichage = Label(root)
    imageAffichage.pack(pady=20)

    angleAffichage = Label(root, text="", font=("Arial", 14))
    angleAffichage.pack(pady=10)

    angleValeursAffichage = Label(root, text="", font=("Arial", 14))
    angleValeursAffichage.pack(pady=10)
    
    Label(root, text="Sélectionnez une image dans l'historique :", font=("Arial", 12)).pack(pady=10)
    listboxCache = tk.Listbox(root, height=5, selectmode=tk.SINGLE)
    listboxCache.pack(pady=10)
    for i in range(5):
            listboxCache.insert("end", f"Image {i+1}")

    Button(root, text="Afficher l'image du cache", font=("Arial", 12), command=afficherImageCache).pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    interface()

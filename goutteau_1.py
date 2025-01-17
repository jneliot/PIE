
import cv2
import numpy as np
import math
import tkinter as tk
from tkinter import filedialog, Label, Button, messagebox
from PIL import Image, ImageTk

thick = 1

# Étape 1 : Prétraitement de l'image
def preprocess_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("L'image n'a pas pu être chargée. Assurez-vous qu'elle est valide.")
    image_original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return image_original, edges

# Étape 2 : Trouver le plus grand contour
def find_largest_contour(edges):
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [c for c in contours if len(c) >= 5]  # Garder seulement les contours valides pour fitEllipse
    if not contours:
        raise ValueError("Aucun contour valide détecté.")
    contour_goutte = max(contours, key=cv2.contourArea)
    return contour_goutte

# Étape 3 : Ajuster une ellipse
def fit_and_draw_ellipse(image, contour_goutte):
    ellipse = cv2.fitEllipse(contour_goutte)
    cv2.ellipse(image, ellipse, (255, 0, 0), thick)
    return ellipse

# Étape 4 : Identifier la base de la goutte (sol)
def find_base_of_drop(contour_goutte):
    x_coords = contour_goutte[:, :, 0].flatten()
    y_coords = contour_goutte[:, :, 1].flatten()
    y_base = np.max(y_coords)
    base_points = [(x, y) for x, y in zip(x_coords, y_coords) if abs(y - y_base) < 2]
    base_left = min(base_points, key=lambda p: p[0])
    base_right = max(base_points, key=lambda p: p[0])
    return base_left, base_right

# Étape 5 : Calculer et dessiner la tangente
def calculate_tangent_at_contact(ellipse, contour_goutte, image):
    (xc, yc), (a, b), angle = ellipse
    a, b = a / 2, b / 2

    x_coords = contour_goutte[:, :, 0].flatten()
    y_coords = contour_goutte[:, :, 1].flatten()
    y_base = np.max(y_coords)

    base_left = min([(x, y) for x, y in zip(x_coords, y_coords) if abs(y - y_base) < 2], key=lambda p: p[0])
    base_right = max([(x, y) for x, y in zip(x_coords, y_coords) if abs(y - y_base) < 2], key=lambda p: p[0])

    def tangent_slope(x, y):
        return -((b ** 2) * (x - xc)) / ((a ** 2) * (y - yc))

    slope_left = tangent_slope(base_left[0], base_left[1])
    slope_right = tangent_slope(base_right[0], base_right[1])

    def draw_tangent(point, slope, image, color):
        x0, y0 = point
        length = 100
        x1 = int(x0 - length)
        y1 = int(y0 - slope * length)
        x2 = int(x0 + length)
        y2 = int(y0 + slope * length)
        cv2.line(image, (x1, y1), (x2, y2), color, 2)

    draw_tangent(base_left, slope_left, image, (0, 255, 0))
    draw_tangent(base_right, slope_right, image, (255, 0, 0))

    angle_left = abs(math.degrees(math.atan(slope_left)))
    angle_right = abs(math.degrees(math.atan(slope_right)))

    return angle_left, angle_right

# Étape 6 : Interface graphique
def create_gui():
    def process_image():
        file_path = filedialog.askopenfilename(title="Choisir une photo de la goutte",
                                               filetypes=[("Images", "*.png")])
        if not file_path:
            return

        loading_label = Label(root, text="Traitement en cours...", font=("Arial", 14))
        loading_label.pack()
        root.update()

        try:
            image_original, edges = preprocess_image(file_path)
            contour_goutte = find_largest_contour(edges)
            ellipse = fit_and_draw_ellipse(image_original, contour_goutte)
            base_left, base_right = find_base_of_drop(contour_goutte)
            angle_left, angle_right = calculate_tangent_at_contact(ellipse, contour_goutte, image_original)

            messagebox.showinfo("Résultat", f"Angle gauche : {angle_left:.2f}°\nAngle droit : {angle_right:.2f}°")

            result_path = "result.png"
            cv2.imwrite(result_path, image_original)

            result_image = Image.open(result_path)
            result_image = result_image.resize((300, 200))
            result_photo = ImageTk.PhotoImage(result_image)

            result_label.config(image=result_photo)
            result_label.image = result_photo
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue : {e}")
        finally:
            loading_label.pack_forget()

    global root, result_label
    root = tk.Tk()
    root.title("Analyse de Goutte d'Eau")
    root.geometry("500x700")

    Label(root, text="Prenez une photo de la goutte et calculez\n"
                     "l'angle de la tangente au périmètre de la goutte",
          font=("Arial", 12), wraplength=400, justify="center").pack(pady=10)

    Button(root, text="Charger une photo", font=("Arial", 12), command=process_image).pack(pady=20)

    result_label = Label(root)
    result_label.pack(pady=20)

    explanation_label = Label(root, font=("Arial", 10), wraplength=400, justify="center")
    explanation_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()

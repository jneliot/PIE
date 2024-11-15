import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
thick=1

def preprocess_image(image_path):
    # Charger l'image en couleurs
    image = cv2.imread(image_path)
    image_original = image.copy()
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Appliquer un flou pour réduire le bruit
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Utiliser la détection de contours de Canny
    edges = cv2.Canny(blurred, 50, 150)
    return image_original, edges


def find_largest_contour(edges):
    # Trouver les contours de l'image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Sélectionner le plus grand contour (supposé être la goutte d'eau)
    contour_goutte = max(contours, key=cv2.contourArea)
    return contour_goutte


def draw_contour_and_base(image, contour_goutte):
    # Dessiner le contour de la goutte sur l'image originale
    cv2.drawContours(image, [contour_goutte], -1, (0, 255, 0), 1)
    # Ajuster un rectangle englobant à la goutte d'eau
    x, y, w, h = cv2.boundingRect(contour_goutte)
    # Dessiner l'horizontale correspondant au prolongement de la partie plate de la goutte
    base_rectangle = (x - h, y + h)  # Coordonnées de la base du rectangle englobant
    cv2.line(image, base_rectangle, (x + w + h, y + h), (0, 0, 255), 1)
    
    return (x - h, y + h), (x + w + h, y + h)


def fit_and_draw_ellipse(image, contour_goutte):
    # Ajuster une ellipse au contour
    ellipse = cv2.fitEllipse(contour_goutte)
    
    # Dessiner l'ellipse
    cv2.ellipse(image, ellipse, (255, 0, 0), thick)
    # Extraire les paramètres de l'ellipse ajustée
    centre, axes, angle = ellipse
    a, b = axes
    theta = np.linspace(0, 2 * np.pi, 1000)
    xc, yc = map(int, centre)
    x, y = ellipse_equation(a, b, theta, xc, yc)
    
    return theta, xc, yc, x, y, a, b


def ellipse_equation(a, b, theta, xc, yc):
    x = xc + a * np.cos(theta)
    y = yc + b * np.sin(theta)
    return x, y


def ellipse_tangent_slope(a, b, theta):
    m = -b * np.cos(theta) / (a * np.sin(theta))
    
    print("Angle: ", np.degrees(np.arctan((abs(m)))))
    return m


def draw_tangent_on_image(image, a, b, x, y, xc, yc, tangent_point_index):
    theta = np.linspace(0, 2 * np.pi, 1000)
    # Trouver le point de tangence sur l'ellipse avec le décalage du centre
    tangent_point = theta[tangent_point_index]
    x_tangent, y_tangent = xc , yc
    # Calculer la pente de la tangente
    slope = ellipse_tangent_slope(a, b, tangent_point)
    # Définir la fonction de la ligne tangente
    tangent_line = lambda x: -slope * (x - x_tangent) + y_tangent
    # Générer les coordonnées de la ligne tangente
    tangent_x = np.linspace(x_tangent - 100, x_tangent + 100, 100)
    tangent_y = tangent_line(tangent_x)
    # Dessiner la tangente sur l'image
    tangent_line_points = np.array(list(zip(tangent_x, tangent_y)), np.int32)
    tangent_line_points = tangent_line_points.reshape((-1, 1, 2))
    cv2.polylines(image, [tangent_line_points], isClosed=False, color=(0, 0, 255), thickness=1)
    return 0


def draw_point(x,y,image):
    x = int(x)  # Convertir en entier
    y = int(y)  # Convertir en entier
        
            # Couleur du point (en BGR)
    couleur = (0, 255, 0)  # Vert
            
            # Dessiner le point
    cv2.circle(image, (x, y), 3, couleur, 3)
    return 0
        
def main(image_path):
    
    
    image_original, edges = preprocess_image(image_path)
    
    contour_goutte = find_largest_contour(edges)
    
    base = draw_contour_and_base(image_original, contour_goutte)
    
    theta, xc, yc, x, y, a, b = fit_and_draw_ellipse(image_original, contour_goutte)
    
    ellipse_params = (a, b, xc, yc)  
    
    
    print(ellipse_params)
    
    y_base = base[0][1]
    
    x1 = xc + 0.5*b*math.sqrt(1 - ((y_base - yc) / (0.5*a))**2)
    x2 = xc - 0.5*b * math.sqrt(1 - ((y_base - yc) / (0.5*a))**2)
    
    
    
    m = (-y_base + yc)/(x1 - xc)
    angle_int = np.arctan((m))
    print(angle_int)
    
    
    
    
    theta = np.linspace(0, 2 * np.pi, 1000)
    # Calcul des écarts absolus entre les valeurs de theta et l'angle connu
    ecarts_absolus = np.abs(theta - angle_int)
    
    # Trouver l'indice du minimum de ces écarts absolus
    indice_plus_proche = np.argmin(ecarts_absolus)
    
    print("Indice le plus proche", indice_plus_proche)
    
    xt=x1
    yt=y_base
    
    
    draw_tangent_on_image(image_original,a,b,x,y,xt,yt,indice_plus_proche)
    
    draw_point(x1,y_base,image_original)
    draw_point(x1,yc,image_original)
    draw_point(xc,yc,image_original)
    
    plt.legend()
    
    # Afficher l'image avec le contour de la goutte, l'ellipse et la ligne d'angle
    plt.imshow(cv2.cvtColor(image_original, cv2.COLOR_BGR2RGB))
    plt.show()
    return 0
if __name__ == "__main__":
    image_path = "/Users/eliot/Desktop/DALL·E-2024-11-15-10.46.png"
    main(image_path)
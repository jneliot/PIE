# Analyse d'une Goutte d'Eau via Ajustement d'une Ellipse et Calcul des Tangentes

## 📌 Introduction
Ce projet vise à analyser la forme d'une goutte d'eau déposée sur une surface en ajustant une **ellipse** aux contours détectés et en calculant les **angles des tangentes** aux points d'intersection entre l'ellipse et la base de la goutte.

L'objectif est de garantir une représentation précise des paramètres géométriques de la goutte pour des applications scientifiques et industrielles (ex. mesure d'angle de contact).

---

## 📌 Démarche Générale
Le programme suit les étapes suivantes :

1. **Chargement et prétraitement de l'image**
   - Chargement de l'image contenant la goutte.
   - Conversion en **niveau de gris**.
   - Application d'un **filtrage et détection des contours** (Canny).

2. **Ajustement d'une ellipse au contour de la goutte**
   - Détection du plus grand contour de l'image.
   - Utilisation de **cv2.fitEllipse()** pour ajuster une ellipse aux points du contour.
   - Extraction des **paramètres de l'ellipse** :
     - Centre **(Xc, Yc)**
     - Demi-axes **(a, b)**
     - Angle d'inclinaison **θ**

3. **Détermination de la base de la goutte**
   - La base est d'abord estimée via **cv2.boundingRect()**.
   - Correction en calculant les **véritables intersections entre la base et l'ellipse**.

4. **Calcul des tangentes et des angles**
   - Détermination des pentes des tangentes via la **dérivée paramétrique de l'ellipse inclinée**.
   - Conversion des pentes en **angles en degrés**.
   - Superposition des tangentes sur l'image.

5. **Affichage et enregistrement des résultats**
   - Tracé de l'ellipse ajustée.
   - Dessin des tangentes en utilisant les pentes calculées.
   - Enregistrement de l'image finale avec les annotations.

---

## 📌 Méthodes Mathématiques Utilisées
### **1️⃣ Ajustement d'une ellipse à partir des contours**
L'ellipse ajustée suit l'équation :

\[ \frac{(x' - X_c)^2}{a^2} + \frac{(y' - Y_c)^2}{b^2} = 1 \]

avec transformation pour prendre en compte l'inclinaison :

\[
\begin{cases}
    x' = (x - X_c) \cos(\theta) + (y - Y_c) \sin(\theta) \\
    y' = -(x - X_c) \sin(\theta) + (y - Y_c) \cos(\theta)
\end{cases}
\]

### **2️⃣ Calcul des points d'intersection entre l'ellipse et la base**
Les points d'intersection \((x_i, y_i)\) sont obtenus en résolvant l'équation :

\[ x_i = X_c \pm a \sqrt{1 - \left(\frac{y_{	ext{base}} - Y_c}{b} \right)^2} \]

### **3️⃣ Détermination des tangentes aux intersections**
La pente des tangentes en un point d'intersection est donnée par :

\[
 m = \frac{-b^2 (x - X_c) \cos(\theta) - a^2 (y - Y_c) \sin(\theta)}{a^2 (y - Y_c) \cos(\theta) - b^2 (x - X_c) \sin(\theta)}
\]

L'angle de la tangente est ensuite calculé par :

\[ \theta = \arctan(m) \]

avec conversion en degrés :

\[ \theta_{\text{degrés}} = \frac{\theta_{\text{radians}} \times 180}{\pi} \]

---

## 📌 Améliorations Apportées
🔹 **Correction du tracé de la base** pour qu'elle ne dépasse pas l'ellipse.
🔹 **Utilisation de `cv2.fitEllipse()`** pour obtenir une meilleure approximation des contours.
🔹 **Correction des pentes des tangentes** en prenant en compte l'inclinaison de l'ellipse.
🔹 **Utilisation de `scipy.optimize.fsolve()`** pour résoudre numériquement certaines équations.

---

## 📌 Dépendances
Ce projet nécessite les bibliothèques suivantes :
```bash
pip install numpy opencv-python scipy
```

---

## 📌 Exemple d'Utilisation
```python
image = cv2.imread('goutte.jpg')
contour = detecter_contour(image)
ellipse = cv2.fitEllipse(contour)
baseGauche, baseDroite, centreBase = trouverBaseGoutte(image, contour, ellipse)
anglesTangentes = calculerAnglesTangentes(ellipse, (baseGauche, baseDroite, centreBase))
dessinerTangentes(image, anglesTangentes)
cv2.imwrite('resultat.png', image)
```

---

## 📌 Résultats Attendus
- ✅ Une **ellipse ajustée précisément** sur la goutte.
- ✅ Une **base qui s'aligne correctement** avec l'ellipse.
- ✅ Des **tangentes bien positionnées** et leurs **angles calculés correctement**.

🚀 **Prêt à analyser la géométrie des gouttes avec précision !** 🎯


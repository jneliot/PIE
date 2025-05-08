import os

cache_path = "cache/"



# Créer un historique de 5 images (temp1, temp2, ...) qu'on renomme et remplace au fur et à mesure
def pre_cache():
	try:
		files = os.listdir(cache_path)
		
		if("temp5.jpg" in files):
			os.remove("../cache/temp5.jpg")
		if("temp4.jpg" in files):
			os.rename("../cache/temp4.jpg", "../cache/temp5.jpg")
		if("temp3.jpg" in files):
			os.rename("../cache/temp3.jpg", "../cache/temp4.jpg")
		if("temp2.jpg" in files):
			os.rename("../cache/temp2.jpg", "../cache/temp3.jpg")
		if("temp1.jpg" in files):
			os.rename("../cache/temp1.jpg", "../cache/temp2.jpg")
	except Exception as e:
		print(f"Erreur lors de la pré-mise en cache : {e}")


# Créer un historique des 5 dernières données des mesures d'angles
def read_cache():
	f = open("../cache/historique.txt", "rb")
	lignes = f.readlines()
	f.close()
	return lignes

def update_cache(new_value):
	try:
		fr = open("../cache/historique.txt", "r")
		lignes = fr.readlines()
		fr.close()

		if len(lignes) > 4:
			lignes.pop()
		newline = str(new_value[0]) + " " + str(new_value[1]) + "\n"
		lignes.insert(0, newline)

		fw = open("../cache/historique.txt", "w")
		for ligne in lignes:
			fw.write(ligne)
		fw.close()
	except Exception as e:
		print(f"Erreur lors de la mise à jour du cache : {e}")
		
def get_cache_angles(index):
	fr = open("../cache/historique.txt", "r")
	lignes = fr.readlines()
	fr.close()
	angles = lignes[index].split()
	print(lignes)
	print(angles)
	res = ['{:.3f}'.format(float(angles[0])),'{:.3f}'.format(float(angles[1]))]
	print(res)
	return res

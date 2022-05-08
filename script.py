# -*- coding: utf-8 -*-
"""
Created on Wed May  4 14:43:57 2022

@author: Francois
"""

# Fichier source : https://www.data.gouv.fr/en/datasets/elections-legislatives-des-11-et-18-juin-2017-resultats-par-bureaux-de-vote-du-1er-tour/
# Qu'il faut passer en excel
# Puis enlever les colonnes en %
# Puis renommer les colonnes de chaque candidat avec _1, _2, etc jusqu'à _27

import os

os.chdir("D:\\Code\\Code_Python\\calcul_legislatives_2017_union")

import pandas, numpy, math

resultats = pandas.read_excel("Leg_2017_Resultats_BVT_T1_c.xlsx", converters={'Code de la circonscription':str,'Code du département':str,'Code de la commune':str,'Code du b.vote':str})
 
#%% # bloc à faire tourner sans modif
len(resultats)
resultats.head()
resultats.tail()
list(resultats.columns)

# Vire toutes les colonnes commençant par %
resultats = resultats.drop(labels = [i for i in list(resultats.columns) if i[0] =="%"], axis = 1)

liste_col_groupby = ["Code du département", "Libellé du département", "Code de la circonscription", "Libellé de la circonscription", *[i for i in list(resultats.columns) if i.startswith("N°") or i.startswith("Sexe") or i.startswith("Nom") or i.startswith("Prénom") or i.startswith("Nuance")]]

resultats = resultats.fillna(0)

# résultats réels par circo
par_circo = resultats.groupby(liste_col_groupby, as_index=False)[['Inscrits',
 'Abstentions',
 'Votants',
 'Blancs',
 'Nuls',
 'Exprimés',
 *["Voix_"+str(i+1) for i in range(27)] ]].sum()
del liste_col_groupby

liste_nuances = set()
for index, ligne in par_circo.iterrows():
    for i in range(27):
        i = i+1
        liste_nuances.add(ligne["Nuance_"+str(i)])
# print(liste_nuances)

bloc_gauche = ["COM", "FI", "SOC", "ECO", "DVG", "EXG", "RDG", "PG", "VEC"]
bloc_centre = ["REM", "MDM", "UDI"]
bloc_droite = ["LR", "DVD"]
bloc_ext_droite = ["EXD", "FN", "DLF"]

par_circo.at[258,"Nuance_6"] = "MDM"  # Jimmy Pahun, qui est MODEM et non DIV

nb_circo_enlevées = 0

#%%

##### BLOC si on veut augmenter les voix d'un camp

def modif_part(nuances_a_modif, prct_var):
    for index, ligne in par_circo.iterrows():
        for i in range(27):
            i = i+1
            if nuances_a_modif == "all" or ligne["Nuance_"+str(i)] in nuances_a_modif :
                var_voix = round(ligne["Voix_"+str(i)]*(prct_var/100))
                par_circo.at[index,"Voix_"+str(i)] += var_voix
                par_circo.at[index,"Exprimés"] += var_voix
                par_circo.at[index,"Votants"] += var_voix
                par_circo.at[index,"Abstentions"] -= var_voix
                
                if par_circo.at[index,"Votants"] > par_circo.at[index,"Inscrits"]:
                    print("Le nb de votants dépasse le nombre d'inscrits dans la circo", index)

# modif_part(nom ou liste de noms de partis ou "all", pourcentage de variation à la hausse ou à la baisse)
# modif_part("all", +35)
# modif_part(bloc_gauche, 30)
# modif_part(bloc_centre, -20)
# modif_part(bloc_droite, 30)

# calcul de la part de chaque bloc + participation

total_gauche, total_droite, total_centre, total_ext_droite, total_div, total_inscrits, total_bn = 0, 0, 0, 0, 0, 0,0
for index, ligne in par_circo.iterrows():
    for i in range(27):
        i = i+1
        if ligne["Nuance_"+str(i)] in bloc_gauche:
            total_gauche += ligne["Voix_"+str(i)]
        if ligne["Nuance_"+str(i)] in bloc_droite:
            total_droite += ligne["Voix_"+str(i)]
        if ligne["Nuance_"+str(i)] in bloc_centre:
            total_centre += ligne["Voix_"+str(i)]
        if ligne["Nuance_"+str(i)] in bloc_ext_droite:
            total_ext_droite += ligne["Voix_"+str(i)]
        if ligne["Nuance_"+str(i)] in ["DIV", "REG"]:
            total_div += ligne["Voix_"+str(i)]
    total_inscrits += ligne["Inscrits"]
    total_bn += ligne["Blancs"] + ligne["Nuls"]

total = total_gauche + total_droite + total_centre + total_ext_droite + total_div + total_bn

print("Gauche = ",round(total_gauche/total*100),"% - Centre =",round(total_centre/total*100),"% - Droite =",round(total_droite/total*100),"% - Ext droite =",round(total_ext_droite/total*100),"% - Div =",round(total_div/total*100), "% - Participation =", round(total/total_inscrits*100,2),"%")
del total, total_gauche, total_droite, total_centre, total_ext_droite, total_div, total_inscrits, total_bn

#%%
del liste_nuances

##### FAIRE TOURNER CE BLOC POUR QUE LES CIRCOS GAGNEES EN 2017 SOIENT CONSIDEREES COMME AUTOMATIQUEMENT REGAGNEES

par_circo["Code_circo"] = par_circo["Code du département"] + par_circo["Code de la circonscription"]

# si on veut enlever les circos déjà gagnées en 2017, par les SOC
par_circo = par_circo[~par_circo["Code_circo"].isin(["0203", "0702", "0703", "1402", "1603", "3108", "3202", "3304", "3503", "3804", "4003", "4201", "5301", "5405", "5913", "6101", "6302", "6403", "7104", "7202", "7204", "7515", "7605", "7711", "8201", "9409", "ZA04", "ZB01", "ZD01"])]
nb_circo_enlevées += 29

# par les GDR
par_circo = par_circo[~par_circo["Code_circo"].isin(["0301", "1313", "1304", "5916", "5920", "6305", "7603", "7606", "7608", "9201", "9302", "9304", "ZB02", "ZB04", "ZD02"])]
nb_circo_enlevées += 15

# par la FI
par_circo = par_circo[~par_circo["Code_circo"].isin(["0901", "0902", "3303", "3402", "5406", "5901", "5902", "7517", "8001", "9301", "9306", "9307", "9309", "9311", "9410", "ZD05", "ZP03"])]
nb_circo_enlevées += 17

# par les EDS
# par_circo = par_circo[~par_circo["Code_circo"].isin(["0401", "4901", "5502", "6902", "7901", "7902", "9105", "9411", "9510", "ZZ02"])]
# nb_circo_enlevées += 10

#%% # bloc à faire tourner sans modif
par_circo_union = 0
par_circo_union = par_circo[["Code du département", "Libellé du département", "Code de la circonscription", "Libellé de la circonscription", 'Inscrits', 'Abstentions', 'Votants', 'Blancs', 'Nuls', 'Exprimés']]
par_circo_union.loc[:,["Voix_centre"]] = 0
par_circo_union.loc[:,["Voix_droite"]] = 0
par_circo_union.loc[:,["Voix_ext_droite"]] = 0
par_circo_union.loc[:,["Voix_gauche"]] = 0
par_circo_union.loc[:,["Part_inscrits_gauche"]] = 0.0
par_circo_union.loc[:,["Part_exprimes_gauche"]] = 0.0
par_circo_union.loc[:,["nb_cand_T2_sup_125"]] = 0

for i in range(27):
    i = i+1
    par_circo_union.loc[:,["Prénom_"+str(i)]] = ""
    par_circo_union.loc[:,["Nom_"+str(i)]] = ""
    par_circo_union.loc[:,["Nuance_"+str(i)]] = ""
    par_circo_union.loc[:,["Voix_"+str(i)]] = 0
    par_circo_union.loc[:,["Part_inscrits_"+str(i)]] = 0.0
    par_circo_union.loc[:,["Part_exprimes_"+str(i)]] = 0.0

# maintenant, on regarde l'union de la gauche
for index, ligne in par_circo.iterrows():
    for i in range(27):
        i = i+1
        if ligne["Nuance_"+str(i)] in bloc_gauche:
            par_circo_union.at[index,"Voix_gauche"] += ligne["Voix_"+str(i)]
            par_circo_union.at[index,"Part_inscrits_gauche"] += ligne["Voix_"+str(i)] / ligne["Inscrits"]*100
            par_circo_union.at[index,"Part_exprimes_gauche"] += ligne["Voix_"+str(i)] / ligne["Exprimés"]*100
            
        elif ligne["Nuance_"+str(i)] in bloc_centre:
            
            par_circo_union.at[index,"Voix_centre"] += ligne["Voix_"+str(i)]
            
            par_circo_union.at[index,"Prénom_"+str(i)] = ligne["Prénom_"+str(i)]
            par_circo_union.at[index,"Nom_"+str(i)] = ligne["Nom_"+str(i)]
            par_circo_union.at[index,"Nuance_"+str(i)] = ligne["Nuance_"+str(i)]
            par_circo_union.at[index,"Voix_"+str(i)] = ligne["Voix_"+str(i)]       
            par_circo_union.at[index,"Part_inscrits_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Inscrits"]*100
            par_circo_union.at[index,"Part_exprimes_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Exprimés"]*100
            
        elif ligne["Nuance_"+str(i)] in bloc_droite:
            
            par_circo_union.at[index,"Voix_droite"] += ligne["Voix_"+str(i)]
            
            par_circo_union.at[index,"Prénom_"+str(i)] = ligne["Prénom_"+str(i)]
            par_circo_union.at[index,"Nom_"+str(i)] = ligne["Nom_"+str(i)]
            par_circo_union.at[index,"Nuance_"+str(i)] = ligne["Nuance_"+str(i)]
            par_circo_union.at[index,"Voix_"+str(i)] = ligne["Voix_"+str(i)]       
            par_circo_union.at[index,"Part_inscrits_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Inscrits"]*100
            par_circo_union.at[index,"Part_exprimes_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Exprimés"]*100
            
        elif ligne["Nuance_"+str(i)] in bloc_ext_droite:
            par_circo_union.at[index,"Voix_ext_droite"] += ligne["Voix_"+str(i)]
            
            par_circo_union.at[index,"Prénom_"+str(i)] = ligne["Prénom_"+str(i)]
            par_circo_union.at[index,"Nom_"+str(i)] = ligne["Nom_"+str(i)]
            par_circo_union.at[index,"Nuance_"+str(i)] = ligne["Nuance_"+str(i)]
            par_circo_union.at[index,"Voix_"+str(i)] = ligne["Voix_"+str(i)]       
            par_circo_union.at[index,"Part_inscrits_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Inscrits"]*100
            par_circo_union.at[index,"Part_exprimes_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Exprimés"]*100
            
        else:
            par_circo_union.at[index,"Prénom_"+str(i)] = ligne["Prénom_"+str(i)]
            par_circo_union.at[index,"Nom_"+str(i)] = ligne["Nom_"+str(i)]
            par_circo_union.at[index,"Nuance_"+str(i)] = ligne["Nuance_"+str(i)]
            par_circo_union.at[index,"Voix_"+str(i)] = ligne["Voix_"+str(i)]       
            par_circo_union.at[index,"Part_inscrits_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Inscrits"]*100
            par_circo_union.at[index,"Part_exprimes_"+str(i)] = ligne["Voix_"+str(i)] / ligne["Exprimés"]*100
            #par_circo_union.at[index,"Voix_non_gauche"] += ligne["Voix_"+str(i)]

# par_circo_union = par_circo_union.loc[[564]]

#%% # bloc à faire tourner sans modif
str_v = "Part_exprimes_"
str_v = "Voix_"

for index, ligne in par_circo_union.iterrows():
    score_du_n2 = 0.0
    score_du_n1 = 0.0
    id_n1 = ""
    id_n2 = ""
    if par_circo_union.at[index,"Part_inscrits_gauche"] > 12.5:
        par_circo_union.at[index,"nb_cand_T2_sup_125"] += 1   
    for i in range(27):
        i = i+1
        # on compte le nombre de gens qui ont dépassé les 12,5% des inscrits
        if par_circo_union.at[index,"Part_inscrits_"+str(i)] > 12.5:
            par_circo_union.at[index,"nb_cand_T2_sup_125"] += 1     
        
    # si yen a moins de deux, on récupère les deux meilleurs
    if par_circo_union.at[index,"nb_cand_T2_sup_125"] < 2:
        for i in range(27):
            i = i+1
            if par_circo_union.at[index, str_v+str(i)] > score_du_n1:
                score_du_n2 = score_du_n1
                score_du_n1 = par_circo_union.at[index, str_v+str(i)] 
                id_n2 = id_n1
                id_n1 = i
            elif par_circo_union.at[index, str_v+str(i)] > score_du_n2:
                score_du_n2 = par_circo_union.at[index, str_v+str(i)]
                id_n2 = i
        if par_circo_union.at[index, str_v+"gauche"] > score_du_n1:
            score_du_n2 = score_du_n1
            score_du_n1 = par_circo_union.at[index, str_v+"gauche"]
            id_n2 = id_n1
            id_n1 = "UDG"
        elif par_circo_union.at[index, str_v+"gauche"] > score_du_n2:
            score_du_n2 = par_circo_union.at[index, str_v+"gauche"] 
            id_n2 = "UDG"
        # et on élimine les autres
        for i in range(27):
            i = i+1
            if not(i == id_n1 or i == id_n2):
                par_circo_union.at[index,"Prénom_"+str(i)] = ""
                par_circo_union.at[index,"Nom_"+str(i)] = ""
                par_circo_union.at[index,"Nuance_"+str(i)] = ""
                par_circo_union.at[index,"Voix_"+str(i)] = 0
                par_circo_union.at[index,"Part_inscrits_"+str(i)] = 0.0
                par_circo_union.at[index,"Part_exprimes_"+str(i)] = 0.0
        if not(id_n1 == "UDG" or id_n2 == "UDG"):
            par_circo_union.at[index,"Voix_gauche"] = 0
            par_circo_union.at[index,"Part_inscrits_gauche"] = 0.0
            par_circo_union.at[index,"Part_exprimes_gauche"] = 0.0    
        par_circo_union.at[index,"nb_cand_T2_sup_125"] = "-1"
            
    # si y'en a plus que deux, on vire ceux qui ont moins de 12.5 des inscrits:
    if par_circo_union.at[index,"nb_cand_T2_sup_125"] >= 2:
        for i in range(27):
            i = i+1
            if par_circo_union.at[index,"Part_inscrits_"+str(i)] <= 12.5:
                par_circo_union.at[index,"Prénom_"+str(i)] = ""
                par_circo_union.at[index,"Nom_"+str(i)] = ""
                par_circo_union.at[index,"Nuance_"+str(i)] = ""
                par_circo_union.at[index,"Voix_"+str(i)] = 0
                par_circo_union.at[index,"Part_inscrits_"+str(i)] = 0.0
                par_circo_union.at[index,"Part_exprimes_"+str(i)] = 0.0
        if par_circo_union.at[index,"Part_inscrits_gauche"] <= 12.5:
            par_circo_union.at[index,"Voix_gauche"] = 0
            par_circo_union.at[index,"Part_inscrits_gauche"] = 0.0
            par_circo_union.at[index,"Part_exprimes_gauche"] = 0.0
    
del score_du_n1
del score_du_n2
del id_n1
del id_n2
#%% # bloc à faire tourner sans modif

# reconstruction un tableau plus propre à 3 colonnes
par_circo_union_2 = 0
par_circo_union_2 = par_circo_union[["Code du département", "Libellé du département", "Code de la circonscription", "Libellé de la circonscription", 'Inscrits', 'Abstentions', 'Votants', 'Blancs', 'Nuls', 'Exprimés', 'Voix_centre', 'Voix_droite', 'Voix_ext_droite', 'Voix_gauche', 'Part_inscrits_gauche', 'Part_exprimes_gauche', 'nb_cand_T2_sup_125']]

for index, ligne in par_circo_union.iterrows():
    num_col_a_remplir = 1
    for i in range(27):
        i = i+1
        if not(par_circo_union.at[index,"Nom_"+str(i)] == ""):
            par_circo_union_2.at[index,"Prénom_"+str(num_col_a_remplir)] = par_circo_union.at[index,"Prénom_"+str(i)]
            par_circo_union_2.at[index,"Nom_"+str(num_col_a_remplir)] = par_circo_union.at[index,"Nom_"+str(i)]
            par_circo_union_2.at[index,"Nuance_"+str(num_col_a_remplir)] = par_circo_union.at[index,"Nuance_"+str(i)]
            par_circo_union_2.at[index,"Voix_"+str(num_col_a_remplir)] = par_circo_union.at[index,"Voix_"+str(i)]
            par_circo_union_2.at[index,"Part_exprimes_"+str(num_col_a_remplir)] = par_circo_union.at[index,"Part_exprimes_"+str(i)]     
            num_col_a_remplir +=1
del num_col_a_remplir
#%%

#### MODIFIER ICI LES TAUX DE REPORT DES VOIX ENTRE centre, droite et ext droite
tx_ed_d = 0.5 # taux de report des voix d'ext droite sur un candidat de droite
tx_ed_c = 0 # etc, avec ed = ext droite, d = droite, c = centre
tx_d_c  = 0.5
tx_d_ed = 0.5
tx_c_d  = 0.5
tx_c_ed = 0

# calcul du nombre de circos où on est au second tour

par_circo_union_3 = par_circo_union_2[par_circo_union_2["Voix_gauche"] != 0]
print("on est au second tour dans", len(par_circo_union_3), "circos")
 
par_circo_union_3.loc[:,["gagnant"]] = ""

# 
for index, ligne in par_circo_union_3.iterrows():
    if par_circo_union_3.at[index,"nb_cand_T2_sup_125"] >3:
        print("il y a une quadrangulaire !")
        
    if par_circo_union_3.at[index,"nb_cand_T2_sup_125"] == 3:
        # cas gauche vs LREM/MDM vs LR
        if (ligne["Nuance_1"] in bloc_centre and ligne["Nuance_2"] in bloc_droite) or (ligne["Nuance_1"] in bloc_droite and ligne["Nuance_2"] in bloc_centre):
            #print("circo UDG/LREM/LR", index)
            for i in range(2):
                i = i+1
                if ligne["Nuance_"+str(i)] in bloc_centre: # le centriste ne récupère que les voix du centre
                    par_circo_union_3.at[index,"Voix_"+str(i)] = ligne["Voix_centre"]
                elif ligne["Nuance_"+str(i)] in bloc_droite: # le LR récupère une partie des voix de l'ext droite
                    par_circo_union_3.at[index,"Voix_"+str(i)] = ligne["Voix_droite"] + tx_ed_d * ligne["Voix_ext_droite"]

        # cas gauche vs LREM/MDM vs FN
        elif (ligne["Nuance_1"] in bloc_centre and ligne["Nuance_2"] in bloc_ext_droite) or (ligne["Nuance_1"] in bloc_ext_droite and ligne["Nuance_2"] in bloc_centre):
            #print("circo UDG/LREM/FN", index)
            for i in range(2):
                i = i+1
                if ligne["Nuance_"+str(i)] in bloc_centre: # le centriste récupère une partie des voix de la droite
                    par_circo_union_3.at[index,"Voix_"+str(i)] = ligne["Voix_centre"] + tx_d_c * ligne["Voix_droite"]
                elif ligne["Nuance_"+str(i)] in bloc_droite: # le faf récupère une partie des voix de la droite
                    par_circo_union_3.at[index,"Voix_"+str(i)] = ligne["Voix_ext_droite"] + tx_d_ed * ligne["Voix_droite"]
        else:
            print("on est pas dans les cas existants, circo n°", index)
        

        
    if par_circo_union_3.at[index,"nb_cand_T2_sup_125"] == 2: 
        # REG, DIV pas traités
        if ligne["Nuance_1"] in bloc_centre:
            par_circo_union_3.at[index,"Voix_1"] = ligne["Voix_centre"]            + tx_d_c * ligne["Voix_droite"]   + tx_ed_c * ligne["Voix_ext_droite"]    
        elif ligne["Nuance_1"] in bloc_droite:
            par_circo_union_3.at[index,"Voix_1"] = tx_c_d * ligne["Voix_centre"]   + ligne["Voix_droite"]            + tx_ed_d * ligne["Voix_ext_droite"]    
        elif ligne["Nuance_1"] in bloc_ext_droite:
            par_circo_union_3.at[index,"Voix_1"] = tx_c_ed * ligne["Voix_centre"]  + tx_d_ed * ligne["Voix_droite"]  + ligne["Voix_ext_droite"]
    
    # maintenant on calcule le vainqueur
    aaa = []
    for i in range(27):
        i=i+1
        try:
            aaa = [*aaa, par_circo_union_3.at[index,"Voix_"+str(i)]]
        except:
            pass
    aaa = [*aaa, par_circo_union_3.at[index,"Voix_gauche"]]

    nb_voix_gagnant = max(aaa)
    del aaa
    if nb_voix_gagnant == par_circo_union_3.at[index,"Voix_gauche"]:
        par_circo_union_3.at[index,"gagnant"] = "UDG"
    else:
        for i in range(3):
            i = i+1
            try:
                if nb_voix_gagnant == par_circo_union_3.at[index,"Voix_"+str(i)]:
                    par_circo_union_3.at[index,"gagnant"] = ligne["Nuance_1"]
            except Exception as e:
                pass
                # print(e)


print("On gagne", len(par_circo_union_3[par_circo_union_3["gagnant"] == "UDG"]), "circos, à ajouter aux", nb_circo_enlevées, "circos retirées car déjà gagnées")

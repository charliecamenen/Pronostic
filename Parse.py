import sys

import requests
import pandas as pd
from bs4 import BeautifulSoup as bf
import datetime
import csv

from Butteur import Butteur
from Carton import Carton
from Changement import Changement
from CollectionEquipe import CollectionEquipe
from Composition import Composition
from Equipe import Equipe


class Parse:

    def __init__(self, url):
        self.url = url
        self.reponse = requests.get(url)
        self.soup_page = bf(self.reponse.text, 'lxml')
        self.collection_equipe = CollectionEquipe()
        self.lst_compet = ['France : Ligue 1', 'France : Ligue 2','Angleterre : Premier League', 'Angleterre : League Championship','Espagne : Liga BBVA', 'Italie : Serie A', 'Allemagne : Bundesliga', 'Portugal : Liga Sagres','Belgique : Pro League', 'Pays-Bas : Eredivisie']
        self.lst_index = []

    def jourSemDate(self,date_string):
        # Split la chaine
        lst_date = date_string.split(' ')
        # liste des mois
        lst_mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre',
                    'novembre', 'décembre']
        # parcour de la liste
        for i in range(len(lst_mois)):
            # Si le mois correspond a l'indice
            if lst_date[2] == lst_mois[i]:
                # On créé la date avec cet indice
                date = datetime.datetime(int(lst_date[3]), i + 1, int(lst_date[1]))
                break

        return [lst_date[0], date]

    def calculAnneeSaison(self,date):
        # annee actuelle
        annee = int(datetime.datetime.today().strftime("%G"))
        # si la date n'est pas comprise entre deux date

        # si l'année est 2020
        if int(date.strftime("%G")) == 2020:
            while not (datetime.datetime(annee, 8, 15) < date):
                # Alors on décrement pour chercher la saison d'avant
                annee = annee - 1
        else:
            while not (datetime.datetime(annee, 7, 1) < date):
                # Alors on décrement pour chercher la saison d'avant
                annee = annee - 1

        return str(annee) + '/' + str(int(annee) + 1)

    # Connection a une page html
    def connect(self,url):
        # Ouverture du lien du match
        reponse = requests.get(url)

        # Tant que la reponse n'est pas ok
        while not reponse.ok:
            # On retente la connection
            reponse = requests.get(url)

        # ON récuperre le code surce HTML
        page = bf(reponse.text, 'lxml')
        return page

    def loadCsv(self, file):
        # Initialisation de la liste de liens
        compet_link_list = []

        # Ouverture du fichier des championnats intéressants
        with open(file) as file_champ_inter:
            # On stock dans une liste
            liste = csv.reader(file_champ_inter, delimiter=',')

            # On créé la liste de liens
            for row in liste:
                compet_link_list.append(row[0])

        return compet_link_list


    def parseAllSite(self):
        global lst_compo_ext, lst_compo_dom, lst_carton_dom, lst_changement_dom, lst_changement_ext, lst_carton_ext, lst_butteurs_ext, lst_butteurs_dom, score_mt

        cpt = 0

        # Pour chaque championnat
        for link in self.loadCsv("C:/Users/ccame/Desktop/Pronostic/championnat_interessant.csv"):
            print(link)

            # ON récuperre le code source HTML
            soup_page_compet = self.connect(link)

            # Nom de competition et du pays
            nom_compet = soup_page_compet.find('div', class_='panel-heading livescore_head').find('div', class_='lienCompetition').text

            # div des resultats
            resultat_page = soup_page_compet.find('div', class_='objselect')

            # Liste des journées
            journees = resultat_page.findAll('option')

            # Pour chaque journées
            for journee in journees:

                #Pour limiter le nombre de match pour les test
                #if (cpt > 200):break

                # ON récuperre le code source HTML
                soup_page_resultat = self.connect(self.url + str(journee['value']))

                # Liste des matchs
                matchs = soup_page_resultat.find('div', class_='panel-body').findAll('tr')

                # Parcour de la liste de matchs
                for match in matchs:

                    # On réccupere l'ID du match
                    try:
                        id_match = match['data-matchid']
                    except:
                        id_match = ''

                    # Colonne du match
                    data_match = match.findAll('td')

                    # Si le match contient des informations
                    if (data_match != []):

                        # Heure du match
                        heure = data_match[0].text

                        # Parcour des span de resultat de match
                        resulat_match_span = data_match[2].findAll('span')

                        # Si le match est terminé
                        if (data_match[1].text[5] == 'T'):

                            # Split du score des deux equipes
                            score = resulat_match_span[2].text.split('-')

                            # Statu du match
                            statut_match = 'termine'

                            # Equipe domicile
                            lst_but_domicile = [resulat_match_span[0].text, score[0].strip()]

                            # equipe exterieur
                            lst_but_exterieur = [resulat_match_span[3].text, score[1].strip()]

                            # Si l'équipe a domicile a plus de buts
                            if (int(score[0].strip()) > int(score[1].strip())):
                                # Alors l'équipe a domicile gagne
                                resultat_dom = 'g'
                                resultat_ext = 'p'
                            # Si l'equipe a l'exterieur a plus de buts
                            elif (int(score[0].strip()) < int(score[1].strip())):
                                # Alors l'equipe a l'exterieur gagne
                                resultat_dom = 'p'
                                resultat_ext = 'g'
                            # Sinon
                            else:
                                # Match nul
                                resultat_dom = 'n'
                                resultat_ext = 'n'

                        else:
                            # Statut du match
                            statut_match = 'a venir'
                            # Données vide pour les résultats
                            lst_but_domicile = [resulat_match_span[0].text, '']
                            lst_but_exterieur = [resulat_match_span[4].text, '']
                            # Resultat vide pour l'instant
                            resultat_ext = ''
                            resultat_dom = ''

                        # Ouverture du lien du match
                        soup_page_match = self.connect(self.url + str(data_match[2].find('a')['href']))

                        # Date du match
                        lst_date = self.jourSemDate(soup_page_match.find('div', class_='col-xs-12 text-center header').find('a').text)

                        # Année de la saison
                        saison = self.calculAnneeSaison(lst_date[1])

                        #Chargement des infos sur le match (cartons, buts, changements)
                        div_ajax_2 = soup_page_match.find('div', id='ajax-match-detail-2')

                        # Si cette div existe
                        if (div_ajax_2 != None and div_ajax_2.text != ''):

                            #Si le score MT existe
                            if (div_ajax_2.find('table', id='match_evenement_score') != None):
                                # Alors on réccupere le score a la mt
                                div_mt = div_ajax_2.find('table', id='match_evenement_score').find('tr').findAll('td')
                                score_mt = div_mt[1].text.split('-')

                            #Si les evennements du matchs existent
                            if (div_ajax_2.find('table', id='match_evenement') != None):

                                # Liste des evennement du  match
                                list_event = div_ajax_2.find('table', id='match_evenement').findAll('tr')

                                #Liste vide des différents évennement
                                lst_butteurs_dom = []
                                lst_butteurs_ext = []
                                lst_carton_dom = []
                                lst_carton_ext = []
                                lst_changement_dom = []
                                lst_changement_ext = []
                                dict_entre_sortie = {'entree': '', 'sortie': '', 'minute': ''}

                                # Pour chaque evenement du match
                                for event in list_event:

                                    # SI c'est pas une pub a la con
                                    if (len(event.findAll('td', class_='bg-danger promo')) == 0):

                                        # Liste des colonnes de l'evennement
                                        detail_event_list = event.findAll('td')

                                        # Si l'evenement concerne l'équipe 1
                                        if (detail_event_list[0].find('a') != None):

                                            # si c'est un but
                                            if (detail_event_list[0].find('span')['class'][2] == 'ico_evenement1'):
                                                lst_butteurs_dom.append(Butteur(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'",''),'jeu'))

                                            # si c'est un but sur péno
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement2'):
                                                lst_butteurs_dom.append(Butteur(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'", ''),'penalty'))

                                            # si c'est un Ppenlty raté
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement6'):
                                                lst_butteurs_dom.append(Butteur(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'",''),'penalty_fail'))

                                            # si c'est un CSC
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement7'):
                                                lst_butteurs_dom.append(Butteur(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'",''),'csc'))

                                            # Si c'est un carton jaune
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement4'):
                                                lst_carton_dom.append(Carton(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'", ''),'jaune1'))

                                            # si c'est un deuxieme carton jaune
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement5'):
                                                lst_carton_dom.append(Carton(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'", ''),'jaune2'))

                                            # Si c'est un carton rouge
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement3'):
                                                lst_carton_dom.append(Carton(detail_event_list[0].find('a').text,detail_event_list[1].text.replace("'", ''),'rouge'))

                                            # Si c'est une sortie de joueur
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement81'):
                                                # Nom du joueur de sortie
                                                dict_entre_sortie['sortie'] = detail_event_list[0].find('a').text
                                                # si le joueur entree est deja défini
                                                if (dict_entre_sortie['entree'] != ''):
                                                    # Alors on ajoute le dictionnaire à la liste
                                                    lst_changement_dom.append(Changement(dict_entre_sortie['entree'], dict_entre_sortie['sortie'], detail_event_list[1].text.replace("'",'')))
                                                    # on réinitialise le dict
                                                    dict_entre_sortie = {'entree': '', 'sortie': '', 'minute': ''}

                                            # si c'est une entrée de joueur
                                            elif (detail_event_list[0].find('span')['class'][2] == 'ico_evenement91'):
                                                # Nom du joueur entrant
                                                dict_entre_sortie['entree'] = detail_event_list[0].find('a').text
                                                # si le joueur sortie est deja défini
                                                if (dict_entre_sortie['sortie'] != ''):
                                                    # Alors on ajoute le dictionnaire à la liste
                                                    lst_changement_dom.append(Changement(dict_entre_sortie['entree'],dict_entre_sortie['sortie'],detail_event_list[1].text.replace("'", '')))
                                                    # on réinitialise le dict
                                                    dict_entre_sortie = {'entree': '', 'sortie': '', 'minute': ''}


                                        # si elle concerne l'equipe 2
                                        elif (detail_event_list[2].find('a') != None):

                                            # si c'est un but
                                            if (detail_event_list[2].find('span')['class'][2] == 'ico_evenement1'):
                                                lst_butteurs_ext.append(Butteur(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'",''),'jeu'))

                                            # si c'est un but sur péno
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement2'):
                                                lst_butteurs_ext.append(Butteur(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'",''),'penalty'))

                                            # si c'est un Ppenlty raté
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement6'):
                                                lst_butteurs_ext.append(Butteur(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'",''),'penalty_fail'))

                                            # si c'est un CSC
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement7'):
                                                lst_butteurs_ext.append(Butteur(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'", ''),'csc'))

                                            # Si c'est un carton jaune
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement4'):
                                                lst_carton_ext.append(Carton(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'", ''),'jaune1'))

                                            # si c'est un deuxieme carton jaune
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement5'):
                                                lst_carton_ext.append(Carton(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'", ''),'jaune2'))

                                            # Si c'est un carton rouge
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement3'):
                                                lst_carton_ext.append(Carton(detail_event_list[2].find('a').text,detail_event_list[1].text.replace("'", ''),'rouge'))

                                            # Si c'est une sortie de joueur
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement82'):
                                                # Nom du joueur de sortie
                                                dict_entre_sortie['sortie'] = detail_event_list[2].find('a').text
                                                # si le joueur entree est deja défini
                                                if (dict_entre_sortie['entree'] != ''):
                                                    # Alors on ajoute le dictionnaire à la liste
                                                    lst_changement_ext.append(Changement(dict_entre_sortie['entree'],dict_entre_sortie['sortie'],detail_event_list[1].text.replace("'", '')))
                                                    # on réinitialise le dict
                                                    dict_entre_sortie = {'entree': '', 'sortie': '', 'minute': ''}

                                            # si c'est une entrée de joueur
                                            elif (detail_event_list[2].find('span')['class'][2] == 'ico_evenement92'):
                                                # Nom du joueur entrant
                                                dict_entre_sortie['entree'] = detail_event_list[2].find('a').text
                                                # si le joueur sortie est deja défini
                                                if (dict_entre_sortie['sortie'] != ''):
                                                    # Alors on ajoute le dictionnaire à la liste
                                                    lst_changement_ext.append(Changement(dict_entre_sortie['entree'],dict_entre_sortie['sortie'],detail_event_list[1].text.replace("'", '')))
                                                    # on réinitialise le dict
                                                    dict_entre_sortie = {'entree': '', 'sortie': '', 'minute': ''}

                            else:
                                # On créé des listes vide a ajouter dans la data complete
                                lst_carton_dom = []
                                lst_carton_ext = []
                                lst_changement_dom = []
                                lst_changement_ext = []
                                lst_butteurs_dom = []
                                lst_butteurs_ext = []

                        #Chargement de la compo des équipes
                        div_compo = soup_page_match.find('div', id='ajax-match-detail-3').find('div', class_='panel panel-info MEDpanelcomposition')
                        #Si la compoexiste
                        if (div_compo != None):

                            # Acces aux compos des deux equipes
                            equipes = div_compo.findAll('td')

                            # Tout les noms
                            joueurs_dom = equipes[0].findAll('a')
                            joueurs_ext = equipes[1].findAll('a')

                            # tout les statuts
                            statut_dom = equipes[0].findAll('span')
                            statut_ext = equipes[1].findAll('span')

                            # Liste des données de chaque joueurs
                            lst_compo_dom = []
                            lst_compo_ext = []

                            #Compos des joueurs et leur statuts
                            for i in range(len(joueurs_ext)): lst_compo_ext.append(Composition(joueurs_ext[i].text, statut_ext[i]['title']))
                            for i in range(len(joueurs_dom)):lst_compo_dom.append(Composition(joueurs_dom[i].text, statut_dom[i]['title']))

                        #Instanciation des équipes domicile et extérieur
                        equipe_dom = Equipe(id_match, lst_date[0],lst_date[1],heure,statut_match,'dom',saison,nom_compet,resultat_dom, lst_but_domicile[0], lst_but_domicile[1] , lst_compo_dom , lst_carton_dom , lst_changement_dom, lst_butteurs_dom , int(score_mt[0].strip()))
                        equipe_ext = Equipe(id_match, lst_date[0],lst_date[1],heure,statut_match,'ext',saison,nom_compet,resultat_ext, lst_but_exterieur[0], lst_but_exterieur[1] , lst_compo_ext,  lst_carton_ext , lst_changement_ext , lst_butteurs_ext, int(score_mt[1].strip()))

                        #equipe_dom.afficher()
                        #equipe_ext.afficher()

                        #Ajout de ces équipe a la collection
                        self.collection_equipe.add(equipe_dom.toList())
                        self.collection_equipe.add(equipe_ext.toList())

                        cpt +=1

    def createInputOutputFile(self):
        print('Traitement...')
        #Converti la liste en dataframe
        global ratio_vic, ratio_class, ratio_def, ratio_nul, ratio_bp, ratio_bc, num_journee
        self.df = self.collection_equipe.toDataFrame()
        #Nettoie le dataframe
        self.df = CollectionEquipe.cleanDataFrame(self.df)

        #Liste des données pour la création du df
        lst_data = []

        # Liste des saisons
        lst_saison = self.df['saison'].unique()

        # Pour chaque saison
        for saison in lst_saison:

            #Mise a jour du classement
            self.majClassement(saison)

            # Dataframe de la saison, trié par équipe et date
            df_trie = self.df.loc[self.df['saison'] == saison].sort_values(by=['equipe', 'date'])
            # Liste des indexs
            self.lst_index = df_trie.index.tolist()
            # Première equipe
            equipe = df_trie.loc[self.lst_index[0], 'equipe']
            # Nombre de matchs de l'équipe
            nb_match_equipe = 0
            # Liste des joueurs de l'équipe
            lst_joueurs_equipe = []
            lst_ratio_joueurs = []


            # Pur chaque ligne
            for i in range(len(self.lst_index)):

                # Initialisation des match next et last
                nb_jour_next = 7
                nb_jour_last = 7
                lst_compet_next = [0, 0, 0]
                lst_compet_last = [0, 0, 0]

                # si l'équipe est différente la meme
                if (df_trie.loc[self.lst_index[i], 'equipe'] != equipe):
                    # On ctualise l'équipe
                    equipe = df_trie.loc[self.lst_index[i], 'equipe']
                    # Liste des joueurs de l'équipe
                    lst_joueurs_equipe = []
                    #L'équipe est a 0 matchs
                    nb_match_equipe = 0

                # Si c'est un match de championnat
                if (df_trie.loc[self.lst_index[i], 'competition'] in self.lst_compet):

                    # Dataframe de la competition pour calculer le nombre d'équipe pour le ratio classement
                    compet_df = df_trie.loc[df_trie['competition'] == df_trie.loc[self.lst_index[i], 'competition']]

                    # Classement ratio
                    ratio_class = float(df_trie.loc[self.lst_index[i], 'classement'] / len(compet_df['equipe'].unique()))
                    # Bp ratio
                    ratio_bp = float(df_trie.loc[self.lst_index[i], 'bp'] / df_trie.loc[self.lst_index[i], 'journee'])
                    # Bc Ratio
                    ratio_bc = float(df_trie.loc[self.lst_index[i], 'bc'] / df_trie.loc[self.lst_index[i], 'journee'])
                    # victoire ratio
                    ratio_vic = float(df_trie.loc[self.lst_index[i], 'gagne'] / df_trie.loc[self.lst_index[i], 'journee'])
                    # defaite ratio
                    ratio_def = float(df_trie.loc[self.lst_index[i], 'perdu'] / df_trie.loc[self.lst_index[i], 'journee'])
                    # Nul ratio
                    ratio_nul = float(df_trie.loc[self.lst_index[i], 'nul'] / df_trie.loc[self.lst_index[i], 'journee'])
                    # Numerod e journee
                    num_journee = df_trie.loc[self.lst_index[i], 'journee']

                # Si on est pas au premier match
                if (nb_match_equipe > 0):
                    # Nombre de jour depuis le dernier match
                    nb_jour_last = int((df_trie.loc[self.lst_index[i], 'date'] - df_trie.loc[self.lst_index[i - 1], 'date']).days)
                    # Comptet du dernier match
                    lst_compet_last = self.trouveTypeCompet(df_trie.loc[self.lst_index[i - 1], 'competition'])

                #Si on est pas au dernier match
                if (i < len(self.lst_index)-1):
                    if (df_trie.loc[self.lst_index[i+1], 'equipe'] == equipe):
                        # Nombre de jour jusqu'au prochain match
                        nb_jour_next = int((df_trie.loc[self.lst_index[i + 1], 'date'] - df_trie.loc[self.lst_index[i], 'date']).days)
                        # Compet du prochain match
                        lst_compet_next = self.trouveTypeCompet(df_trie.loc[self.lst_index[i - 1], 'competition'])

                nb_match_equipe += 1
                # Mise a jour des stats de l'équipe
                lst_joueurs_equipe = self.majStatEquipe(lst_joueurs_equipe, df_trie.loc[self.lst_index[i], 'compo'],
                                                        df_trie.loc[self.lst_index[i], 'butteur'],
                                                        df_trie.loc[self.lst_index[i], 'resultat'])
                lst_ratio_joueurs = self.ratioJoueur(lst_joueurs_equipe, df_trie.loc[self.lst_index[i], 'compo'])

                input_data = [df_trie.loc[self.lst_index[i], 'id_match']]
                input_data += [ratio_class, ratio_vic, ratio_def, ratio_nul, ratio_bp, ratio_bc, num_journee]
                input_data += self.domExt(df_trie.loc[self.lst_index[i], 'dom_ext'])
                input_data += [nb_jour_last]
                input_data += lst_compet_last
                input_data += [nb_jour_next]
                input_data += lst_compet_next
                input_data += lst_ratio_joueurs
                #print(input_data)

                if (nb_match_equipe > 5):
                    #Mise a jour des dernier resultat de l'équipe
                    input_data += self.lastResultat(df_trie, i)
                    lst_data.append(input_data)

                input_data += df_trie.loc[self.lst_index[i], 'resultat']

        headers = ['id_match', "ratio_class", "ratio_vic", "ratio_def", "ratio_nul", "ratio_bp", "ratio_bc", "num_journee",
                   "dom","ext" ,"nb_jour_last", "championnat_last", "europe_last", "coupe_last", "nb_jour_next", "championnat_next",
                   "europe_next", "coupe_next", "J1_but" ,"J1_vic","J1_match", "J2_but" ,"J2_vic","J2_match","J3_but" ,"J3_vic","J3_match",
                   "J4_but" ,"J4_vic","J4_match","J5_but" ,"J5_vic","J5_match","J6_but" ,"J6_vic","J6_match","J7_but" ,"J7_vic","J7_match",
                   "J8_but" ,"J8_vic","J8_match","J9_but" ,"J9_vic","J9_match","J10_but" ,"J10_vic","J10_match","J11_but" ,"J11_vic","J11_match","hist1",
                   "hist2","hist3","hist4","hist5","output" ]
        df = pd.DataFrame(lst_data,columns =headers)
        #print(df.head(3))

        dom_df = df.loc[df["dom"] == 1]
        ext_df = df.loc[df["ext"] == 1]
        df_final = pd.merge(dom_df, ext_df, on="id_match")

        return df_final

    def lastResultat(self, df_trie, indice):
        nb_match_hist = 5
        lst_match_hist = []
        for i in range(indice-1,indice - nb_match_hist -1,-1):
            #Info du match (2 equipes)
            match = df_trie.loc[df_trie['id_match'] == df_trie.loc[self.lst_index[i], 'id_match'], ['buts','equipe']]
            #Soustraction des deux valeur sur ce match
            diff_hist = int(match.loc[match['equipe'] == df_trie.loc[self.lst_index[i], 'equipe'], 'buts']) - int(match.loc[match['equipe'] != df_trie.loc[self.lst_index[i], 'equipe'], 'buts'])
            lst_match_hist.append(diff_hist)
        return lst_match_hist

    def majClassement(self, saison):

        # Pour chaque competition
        for compet in self.lst_compet:
            # On les données triées par date de la saison en question
            df_trie = self.df.loc[(self.df['saison'] == saison) & (self.df['statut_match'] == 'termine') & (
                        self.df['competition'] == compet)].sort_values(by='date')

            if not df_trie.empty:
                # parcour des equipes
                for equipe in df_trie['equipe'].unique():
                    #print(equipe)
                    # Compteur de journée
                    cpt_journee = 1
                    cpt_pts = 0
                    cpt_bp = 0
                    cpt_bc = 0
                    cpt_j = 0
                    cpt_g = 0
                    cpt_n = 0
                    cpt_p = 0

                    # Df pour l'équipe trié par journée
                    df_equipe = df_trie.loc[df_trie['equipe'] == equipe].sort_values(by='journee')

                    # Mise a jour des données de classement
                    for row in df_equipe.index.tolist():

                        # On modifie la valeur du vrai df en fonction de l'id
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'journee'] = cpt_journee
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'pts'] = cpt_pts
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'bp'] = cpt_bp
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'bc'] = cpt_bc
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'diff'] = cpt_bp - cpt_bc
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'gagne'] = cpt_g
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'nul'] = cpt_n
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'perdu'] = cpt_p
                        self.df.loc[(self.df['id_match'] == df_trie.loc[row, 'id_match']) & (self.df['equipe'] == equipe), 'joue'] = cpt_j

                        # !!!! On modifie les données après le match !!!!
                        # C'est pour ca qu'on le fait apres la modif de la base !!!

                        # On incrémente le compteur
                        cpt_journee += 1

                        # incrémentation des points
                        if (df_trie.loc[row, 'resultat'] == 'g'):
                            # incrémentation des pts
                            cpt_pts += 3
                            # Incrémentation des match gagné
                            cpt_g += 1
                        elif (df_trie.loc[row, 'resultat'] == 'p'):
                            # incrémentation des matchs perdu
                            cpt_p += 1
                        else:
                            # incrémentation des pts
                            cpt_pts += 1
                            # incrémentation des match nuls
                            cpt_n += 1

                        #print("test : ",df_trie.loc[row, 'buts'])
                        # Incrémentation des buts pour
                        cpt_bp += int(df_trie.loc[row, 'buts'])
                        # Incrémentation des buts contre
                        cpt_bc += int(df_trie.loc[(df_trie['id_match'] == df_trie.loc[row, 'id_match']) & (
                                    df_trie['equipe'] != equipe)]['buts'])
                        # Incrémentation des match joué
                        cpt_j += 1

                for journee in self.df.loc[(self.df['saison'] == saison) & (self.df['statut_match'] == 'termine') & (self.df['competition'] == compet)]['journee'].unique():
                    # Classement a la journée actuelle
                    classement = self.df.loc[
                        (self.df['saison'] == saison) & (self.df['competition'] == compet) & (self.df['statut_match'] == 'termine') & (
                                    self.df['journee'] == journee)].sort_values(by=['pts', 'diff', 'bp'],
                                                                           ascending=[False, False, False])
                    # Compteur de classement
                    cpt_class = 1
                    # Mise a jour du classement actuel
                    for i in classement.index.tolist():
                        # On attribue un numero de classement
                        self.df.loc[i, 'classement'] = cpt_class
                        # On incrémente le classement
                        cpt_class += 1

    def ratioJoueur(self,lst_joueurs, lst_compo):
        lst_ratio = []
        for joueur in lst_joueurs:
            for compo in lst_compo:
                if (joueur['nom'] == compo.joueur and compo.statut == 'Titulaire'):
                    lst_ratio.append(float(joueur['nb_buts'] / joueur['nb_matchs']))
                    lst_ratio.append(float(joueur['nb_victoire'] / joueur['nb_matchs']))
                    lst_ratio.append(joueur['nb_matchs'])
        return lst_ratio

    #liste stat existante sur les joueur des précédent matchs
    #Liste des joueur de ce match la (Type compo)
    #Liste des buts de ce match la
    #résultat du match (Gagné ou non)
    def majStatEquipe(self,lst_actuelle, lst_nouvelle, lst_buts, resultat):

        # Membre deja présent
        lst_actuelle_membre = []

        # Mise a jour des membres deja présents
        for membre in lst_actuelle:
            # On ajoute tout les joueurs actuel
            lst_actuelle_membre.append(list(membre.values())[0])

        # Pour chaque joueur de la compo
        for joueur in lst_nouvelle:

            # Si il ne fait pas partie de la liste des joueurs
            if (joueur.joueur not in lst_actuelle_membre):
                # On ajoute le joueur a la liste
                lst_actuelle.append({'nom': joueur.joueur, 'nb_matchs': 0, 'nb_buts': 0, 'nb_victoire': 0})

            # Parcour de la liste actuel
            for i in range(len(lst_actuelle)):
                # Si le joueur correspond a la liste actuelle
                if (lst_actuelle[i]['nom'] == joueur.joueur):

                    # Parcour des buts
                    for but in lst_buts:
                        # Si le joueur a marqué un but
                        if (but.joueur == lst_actuelle[i]['nom']):
                            # Alors on incrémente son nombre de buts
                            lst_actuelle[i]['nb_buts'] += 1

                    # Si le match est remporté
                    if (resultat == 'g'):
                        lst_actuelle[i]['nb_victoire'] += 1

                    # Ajout d'un match au joueur en question
                    lst_actuelle[i]['nb_matchs'] += 1

        return lst_actuelle

    #retourne une liste de taille 3 [championnat, coupe, europe]
    def trouveTypeCompet(self,compet):
        lst_champ = ['France : Ligue 1', 'France : Ligue 2','Angleterre : Premier League', 'Angleterre : League Championship','Espagne : Liga BBVA', 'Italie : Serie A','Allemagne : Bundesliga', 'Portugal : Liga Sagres','Belgique : Pro League', 'Pays-Bas : Eredivisie']
        lst_coupe = ['France : Coupe de France', 'Espagne : Coupe du Roi',"Allemagne : Coupe d'Allemagne", 'Angleterre : League Cup','Angleterre : FA Cup', 'Italie : Coppa Italia']
        lst_europe = ['Europe : Ligue des champions UEFA', 'Europe : UEFA Europa League']
        if (compet in lst_champ):return [1, 0, 0]
        elif (compet in lst_coupe):return [0, 0, 1]
        elif (compet in lst_europe):return [0, 1, 0]
        else:return [0, 0, 0]

    def domExt(self,chaine):
        if(chaine == 'dom'):return [1,0]
        elif(chaine == 'ext'):return [0,1]




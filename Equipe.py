# -*- coding: utf-8 -*-
from Butteur import Butteur
from Carton import Carton
from Changement import Changement
from Composition import Composition


class Equipe:

    def __init__(self, id_match, jour_semaine, date, heure, statut_match,
                 dom_ext, saison, competition, resultat, equipe, buts,
                 lst_compo, lst_cartons, lst_changement, lst_butteur, buts_mt):
        self.id_match = id_match
        self.jour_semaine = jour_semaine
        self.date = date
        self.heure = heure
        self.statut_match = statut_match
        self.dom_ext = dom_ext
        self.saison = saison
        self.journee = 0
        self.competition = competition
        self.resultat = resultat
        self.equipe = equipe
        self.buts = buts
        self.classement = 0
        self.pts = 0
        self.joue = 0
        self.gagne = 0
        self.nul = 0
        self.perdu = 0
        self.bp = 0
        self.bc = 0
        self.diff = 0
        self.compo = lst_compo
        self.carton = lst_cartons
        self.changement = lst_changement
        self.butteur = lst_butteur
        self.buts_mt = buts_mt

    def afficher(self):
        print(self.id_match,self.jour_semaine,self.date,self.heure,self.statut_match,self.dom_ext,self.saison,
              self.journee,self.competition,self.resultat,self.equipe,
              self.buts,self.classement,self.pts,self.joue,self.gagne,
              self.nul,self.perdu,self.bp,self.bc,self.diff,self.compo,
              self.carton,self.changement,self.butteur,self.buts_mt)

    def toList(self):
        return [self.id_match,self.jour_semaine,self.date,self.heure,self.statut_match,self.dom_ext,self.saison,self.journee,self.competition,self.resultat,self.equipe,self.buts,self.classement,self.pts,self.joue,self.gagne,self.nul,self.perdu,self.bp,self.bc,self.diff,self.compo,self.carton,self.changement,self.butteur,self.buts_mt]
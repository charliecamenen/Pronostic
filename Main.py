# -*- coding: utf-8 -*-
from Equipe import Equipe 
import requests
import pandas as pd
from bs4 import BeautifulSoup as bf
from Parse import Parse


def main():
    #Création de l'objet qui parse le site web
    parse = Parse("https://www.matchendirect.fr/")
    #On parse tout le site
    parse.parseAllSite()
    #Création du fichier de sortie
    df_data = parse.createInputOutputFile()
    #Enregistrement en CSV
    df_data.to_csv('data.csv', index=False, encoding="utf-8-sig")
    print('tete')

main()
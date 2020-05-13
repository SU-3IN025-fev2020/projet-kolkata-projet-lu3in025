#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:35:59 2020

@author: aïssata
"""

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

# ---- ---- ---- ---- ---- ----
# Classe Node qui permettra d'enregistrer le chemin à prendre pour chaque joueur
# ---- ---- ---- ---- ---- ----

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0
        
    def get_position(self):
        return self.position
    
    def get_parent(self):
        return self.parent
    
    def get_h(self):
        return self.h
    
    def get_g(self):
        return self.g
    
    def get_f(self):
        return self.f
    
    def affiche_node(self):
        print('Noeud : \nposition : ',self.position,'\nparent : ',self.parent)
    
# ---- ---- ---- ---- ---- ----
# --- Distance de Manhattan ---
# ---- ---- ---- ---- ---- ----

def dist(p1,p2):
    x1,y1 = p1
    x2,y2 = p2
    return abs(x2-x1) + abs(y2-y1)
    
# ---- ---- ---- ---- ---- ----
# ----         A *         ----
# ---- ---- ---- ---- ---- ----
    
def Astar(pos_initiale, pos_finale, wallStates):
    """ Cette fonction effectue l'algorithme A* """
    
    node_init = Node(0,pos_initiale)
    node_init.g =  dist(pos_initiale,pos_initiale)
    node_init.h = dist(pos_initiale,pos_finale)
    node_init.f = node_init.get_g() + node_init.get_h()
    frontiere = [(node_init,node_init.get_f(), node_init.get_position())]
    
    reserve = {}        
    
    node_end = None

    while frontiere != []:
        # recupere l'élément ayant la valeur f la plus petite
        index_min = frontiere.index(min(frontiere, key=lambda item:item[1]))
        etat = frontiere.pop(index_min)
        current_node = etat[0]
        # position courante
        xc,yc = etat[2] 
        # position finale trouvé
        if (xc,yc) == pos_finale: 
            node_end = current_node
            break
        # on passe si la case est accessible 
        if xc >=0 and yc>=0 and xc < 20 and yc<20:
            reserve[current_node.get_position()] = []
        # enregistrement des différentes position
        direction = [(0,1),(0,-1),(1,0),(-1,0)]
        for new_pos in direction:
            next_x = xc+new_pos[0]
            next_y = yc+new_pos[1]
            pos = (next_x, next_y)
            if pos not in reserve and pos not in wallStates and next_x >=0 and next_y>=0 and next_x < 20 and next_y<20 :
                node = Node(current_node,pos)
                node.h = dist(pos,pos_finale)
                node.g = dist(pos,pos_initiale)
                node.f = node.get_g()+node.get_h()
                frontiere.append((node,node.get_f(),pos))
                reserve[current_node.get_position()].append(node)
        
    parcours = []
    node = node_end
    while node.get_parent() != 0 : 
        parcours.append(node.get_position())
        node = current_node.get_parent()
        current_node = node
    parcours.append(node.get_position())
    # la liste parcours contient le plus cours chemin pour aller au restaurant du joueur
    
    return parcours

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----
    
game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player

def main(Strategies=['uniforme','têtu','videoupresque', 'loop'], it=5):# par defaut

    iterations = it 
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])

    init()
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    #print("lignes", nbLignes)
    #print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    #print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    #print ("Goal states:", goalStates)
    nbRestaus = len(goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises
    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in (wallStates+goalStates)] 

    posPlayers = initStates
    restau=[0]*nbPlayers
    
    #-------------------------------
    # initialisation de la liste des joueurs présents dans chaque restaurant
    #-------------------------------
    
    ListeRestau = [[] for i in range(nbRestaus)]
    
    #-------------------------------
    # initialisation de la liste contenant le nombre de gain de chaque joueur
    #-------------------------------
    
    gain = [0]*nbPlayers
    
    #-------------------------------
    # initialisation du dictionnaire qui contiendra le score moyen pour chaque stategie
    #-------------------------------
    
    score = {s: 0 for s in Strategies}
    
    #-------------------------------
    # initialisation du dictionnaire qui contiendra le produit de chaque joueur pour chaque stategie
    #-------------------------------
    
    produit = {s : 1 for s in Strategies}
    
    #-------------------------------
    # Choix de la stratégie
    #-------------------------------
    # uniforme : choix du restau de façon uniforme
    # têtu : une fois que le restau à été choisi, le joueur ira toujours dans celui ci
    # videoupresque : le joueur choix le restaurant ayant eu très peu(ou pas du tout) de fréquentation 
    stPlayers = []
    deja_pris = ""
    # Repartition des differentes stratégies de manière égale 
    # on verifie si la nombre de stratégie est un multiple du nombre de joueur 
    # si c'est le cas alors on aura un nombre exacte de joueur par stratégie
    # sinon on effectue de la même chose que dans le cas précédent mais 
    # on rajoutera le reste de manière égale
    
    if nbPlayers % len(Strategies) == 0:
        place = {s:nbPlayers//len(Strategies) for s in Strategies}
    else:
        place = {s:nbPlayers//len(Strategies) for s in Strategies}
        for i in range(nbPlayers % len(Strategies)):
            # ici, pour ne pas rajouter tous le reste des places à une seule stratégie
            # on verifie à chaque fois si on est déja tombé sur la stratégie
            choix = random.choice(Strategies)
            while deja_pris == choix: 
                deja_pris = choix
                choix = random.choice(Strategies)
            place[choix] += 1
            
    nbJoueurPerStrat = {s : 0 for s in Strategies} # permet de savoir le nombre de joueur par stratégie
    
    # ici on attribut une stratégie a chaque joueur en fonction des places restantes par stratégie
    for j in range(nbPlayers):
        s = random.choice(Strategies)
        while place[s] == 0:
            s = random.choice(Strategies)
        stPlayers.append(s)
        place[s] -= 1
        nbJoueurPerStrat[stPlayers[j]] += 1
    
    #-------------------------------
    # Taux de fréquentation
    #-------------------------------
    
    taux = {i:{j:0 for j in range(nbRestaus)} for i in range(iterations)}
    #print(taux)
    # Clé : itération
    # valeur : dictionnaire qui associe
            #  chaque clé correspond au numéro du restaurant 
            # ,à une valeur qui correspond au nombre de personne présente
    
    #-------------------------------
    # Score moyen par stratégie
    #-------------------------------
    
    stats_score = {s : [] for s in Strategies}
    # Clé : stratégie
    # valeur : liste contenant le score moyen de cette stratégie à chaque itération
    
    #-------------------------------
    # Produit de chaque joueur par stratégie
    #-------------------------------
    
    stats_produit = {s : [] for s in Strategies}
    # Clé : stratégie
    # valeur : liste contenant le produit de chaque joueur de cette stratégie à chaque itération
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
    for it in range(iterations):
        
        #-------------------------------
        # Placement aleatoire des joueurs, en évitant les obstacles
        #-------------------------------
        
        for j in range(nbPlayers):
            x,y = random.choice(allowedStates)
            players[j].set_rowcol(x,y)
            game.mainiteration()
            posPlayers[j]=(x,y)
        
        #-------------------------------
        # initialisation de la liste des joueurs présents dans chaque restaurant
        #-------------------------------
            
        ListeRestau = [[] for i in range(nbRestaus)]
        
        for jo in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            pos_initiale=posPlayers[j]
            
            #-------------------------------
            # chaque joueur choisit un restaurant
            #-------------------------------
            
            if it == 0:
                c = random.randint(0,nbRestaus-1)
                restau[jo]=c # le joueur j choisi le restaurant c
                pos_finale = goalStates[c]
                
            else:
                
                if stPlayers[jo] == 'uniforme':
                    c = random.randint(0,nbRestaus-1)
                    restau[jo]=c # le joueur j choisit le restaurant c
                    pos_finale = goalStates[restau[jo]]

                if stPlayers[jo] == 'têtu':
                    pos_finale = goalStates[restau[jo]] # le joueur j choisit toujours le même restau
                    
                if stPlayers[jo] == 'videoupresque':
                    rest = sorted(taux[it-1].items(),key=lambda t:t[1])[0][0]
                    restau[jo] = rest # le joueur j choisit le restau le moins fréquenté au tour precedent
                    pos_finale = goalStates[restau[jo]]

                    
            #-------------------------------
            # Taux de fréquentation
            #-------------------------------

            taux[it][restau[jo]] +=1

            #-------------------------------
            # Construction du plus court chemin avec A*
            #-------------------------------
            
            parcours = Astar(pos_initiale, pos_finale, wallStates)
            
            #-------------------------------
            # Parcours du plus court chemin 
            #-------------------------------
            
            for k in parcours[::-1]:
               row,col = k
               players[jo].set_rowcol(row,col)
               game.mainiteration()
            ListeRestau[restau[jo]].append(jo)
            
        #-------------------------------
        # Affectation des gains 
        #-------------------------------
        
        # tous les joueurs sont arrivés à destination 
        print("Occupation des restaurants à l'itération ", it, ":",ListeRestau)
        for j in ListeRestau:
            # le restaurant ne possède qu'un seul joueur
            if len(j) == 1:
                gain[j[0]]+= 1
            if len(j) > 1:
                # le restaurant possède plusieurs joueurs donc choix aléatoire d'un joueur
                i = random.choice(j)
                gain[i]+=1
                
        # pour chaque stratégie, on enregistre le score moyen en fonction des gains cumulés
        for k in range(len(gain)):
            score[stPlayers[k]] += gain[k]
        for s,v in score.items():
            stats_score[s].append(v//nbJoueurPerStrat[s])
        # pour chaque stratégie, on enregistre le produit des score de chaque joueur
        for k in range(len(gain)):
            produit[stPlayers[k]] *= gain[k]
        for s,v in produit.items(): 
            stats_produit[s].append(v)
            # remise à 1 des valeurs pour eviter les produits nuls
            produit[s] = 1
       

    print("Taux de fréquentation : ",taux)
    
    pygame.quit()
    # retourner le produit des scores de chaque joueur et le score moyen pour chaque stratégie 
    return stats_score, stats_produit, gain

#main()
    



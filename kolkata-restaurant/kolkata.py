#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:35:59 2020

@author: aissata
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
    
def main():

    #for arg in sys.argv:
    iterations = 5 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
    nbRestaus = len(goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises
    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in wallStates and (x,y) not in goalStates] 

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
    # Choix de la stratégie
    #-------------------------------
    
    Strategies = ['uniforme','têtu']
    stPlayers = []
    for j in range(nbPlayers):
        stPlayers.append(random.choice(Strategies))
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
    
    for i in range(iterations):
        
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
        
        for j in range(nbPlayers): # on fait bouger chaque joueur séquentiellement

            pos_initiale=posPlayers[j]
            
            #-------------------------------
            # chaque joueur choisit un restaurant
            #-------------------------------
            
            # pour la premier tour, tous les joueurs choisissent un restau
            # mais au fur et à mesure que l'on passe les itérations,
            # on verra que les joueurs ayant choisi la stratégie têtu
            # choisiront toujours le même restaurant
            
            
            if i == 0 or stPlayers[j] == 'uniforme':
                if i > 0:
                    print("joueur ",j," à choisi la stratégie(uniforme) :",stPlayers[j])
                c = random.randint(0,nbRestaus-1)
                restau[j]=c # le joueur j choisi le restaurant c
                pos_finale = goalStates[c]
                print(pos_finale)
                
            if stPlayers[j] == 'têtu':
                print("joueur ",j," à choisi la stratégie(têtu) :",stPlayers[j])
                pos_finale = goalStates[restau[j]]
                print(pos_finale)
            #-------------------------------
            # Construction du plus court chemin avec A*
            #-------------------------------
            
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
            
            #-------------------------------
            # Parcours du plus court chemin 
            #-------------------------------
            
            for k in parcours[::-1]:
               row,col = k
               players[j].set_rowcol(row,col)
               game.mainiteration()
            ListeRestau[restau[j]].append(j)
            
        #-------------------------------
        # Affectation des gains 
        #-------------------------------
        # tous les joueurs sont arrivés à destination 
        print(ListeRestau)
        for j in ListeRestau:
            # le restaurant ne possède qu'un seul joueur
            if len(j) == 1:
                gain[j[0]]+= 1
            if len(j) > 1:
                # le restaurant ne possède qu'un seul joueur donc choix aléatoire d'un joueur
                i = random.choice(j)
                gain[i]+=1
                
    #-------------------------------
    # Affichage des gains 
    #-------------------------------
    uni = 1
    tetu = 1
    for i in range(len(gain)):
        print("Gain du joueur ",i," : ",gain[i],"/",iterations)
        if stPlayers[i] == 'têtu':
            tetu*=gain[i]
        if stPlayers[i] == 'uniforme':
            uni*=gain[i]    
    print("Produit des scores pour la stratégie uniforme : ",uni)
    print("Produit des scores pour la stratégie têtu : ",tetu)
    
    pygame.quit()
    
        
    
   

if __name__ == '__main__':
    main()
    



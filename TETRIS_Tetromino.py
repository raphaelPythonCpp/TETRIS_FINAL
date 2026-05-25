import pygame
import random as rd
from math import sqrt

class Tetromino(object):
    def __init__(self, jeu, type, entrainement=False):
        self.jeu = jeu
        self.entrainement = entrainement
        self.type = type
        self.orientation = 0
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.couleur = self.jeu.dicoCouleursPieces[self.type]
        self.x = self.jeu.nbColonnes//2 - 1
        self.y = -min(dy for dx,dy in self.matrice)
        if not self.entrainement:
            self.deltaTemps = 0
            self.tempsAvant = pygame.time.get_ticks()
            self.bouge = True
            self.yOmbre = 0

    def reset(self, grille):
        if self.orientation != 0:
            self.orientation = 0
            self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.x = int(self.jeu.nbColonnes/2 - max(dx for dx,dy in self.matrice)/2)
        self.y = -min(dy for dx,dy in self.matrice)
        if not self.entrainement:
            self.tempsAvant = pygame.time.get_ticks()
            self.deltaTemps = self.jeu.deltaTemps #ms
            self.bouge = True
            self.yOmbre = 0

        if self.jeu.tester_chevauchement(grille, self.x, self.y, self.orientation, self.type):
            return True
        return False

    def bouger(self, grille):
        if not self.bouge :
            return
        if pygame.time.get_ticks() >= self.tempsAvant+self.deltaTemps:
            self.tempsAvant = pygame.time.get_ticks()
            self.descendre(grille)

    def descendre(self, grille):
        if self.jeu.tester_chevauchement(grille, self.x, self.y+1, self.orientation, self.type):
            self.fixer(grille, tester_lignes=True, reel=True)
        else :
            self.y += 1

    def fixer(self, grille, tester_lignes=True, reel=True, fScore=None):
        self.bouge = False
        self.yOmbre = None
        """self.jeu.afficher()
        pygame.time.delay(500)"""
        self.jeu.mettre_dans_grille(grille, self.x, self.y, self.orientation, self.type, self.couleur, coin=False, reel=reel)
        if tester_lignes:
            grille[:] = self.jeu.tester_lignes(grille, reel=reel, fScore=fScore)
        if reel:
            self.jeu.changer_nb_coups(deltaCoups=1)
            self.jeu.calculer_sommeNbBlocs(ajout=4) #ATTENTION A modifier si tetromino plus seulement de 4 pièces
            self.jeu.generer_piece()
        self.jeu.changer_grille(delta=1)
        self.jeu.deltaTemps = self.jeu.deltaTempsFin - self.jeu.deltaTempsFin*sqrt(self.jeu.nbLignesSupprimees) / (sqrt(self.jeu.nbCoups) + self.jeu.deltaTempsMilieu)
        self.deltaTemps = self.jeu.deltaTemps

    def tourner(self, grille, changement):
        self.orientation = (self.orientation + changement)%4
        self.matrice = self.jeu.dicoMatricesPieces[(self.type, self.orientation)]
        self.predire_ombre(grille)

    def deplacer(self, grille, dx):
        self.x += dx
        self.predire_ombre(grille)

    def predire_ombre(self, grille):
        self.yOmbre = self.y
        while not self.jeu.tester_chevauchement(grille, self.x, self.yOmbre+1, self.orientation, self.type):
            self.yOmbre += 1
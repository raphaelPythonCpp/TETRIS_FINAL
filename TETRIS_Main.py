import pygame
from TETRIS_Menus import Menus
from math import floor

pygame.init()
pygame.mixer.init()

wFenetre, hFenetre = 900, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS vFinale")
nbColonnes, nbLignes = 7, 12

horloge = pygame.time.Clock()
nomPolice, taillePolice, grasPolice, italiquePolice = "Arial", 20, True, False
lAttributsPolice = (nomPolice, taillePolice, grasPolice, italiquePolice)
police = pygame.font.SysFont(nomPolice, taillePolice, bold=grasPolice, italic=italiquePolice)

game_infini = False
charger_reseau = True
evaluation = False

env = Menus(fenetre=fenetre, lAttributsPolice=lAttributsPolice, horloge=horloge,
              nbColonnes=nbColonnes, nbLignes=nbLignes,
              visuel=True, audio=True, nbFramesAffichage=10, lNbNoeuds=None,
              algorithme=True, entrainementGreedy=False, entrainementGenetique=False, entrainementNES=False, entrainementDRL=False,
              gameInfini=game_infini, charger_reseau=charger_reseau, evaluation=evaluation)

env.menuHome.actif = True
env.boucle()

pygame.quit()

"""
+ faire un algo troll qui fait de la merde jusqu'à genre hMax = nbLignes-4, et après il lance un bon algo
avec ça on peut mettre des noms genre \"C'est luther qui joue\" (<=> random) puis \"C'est Raphaël qui joue\" (bot brillant)

"""
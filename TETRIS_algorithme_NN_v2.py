from collections import deque
from copy import deepcopy
from datetime import datetime
import torch
import pygame

dxy = [(1,0), (-1,0), (0,1)]
dxyo = [(1,0,0), (-1,0,0), (0,1,0), (0,0,1)]

class Algorithme(object):
    def __init__(self, jeu, lNbNoeuds):
        self.jeu = jeu
        #Graphiques
        self.dtAlgo = 0 #ms
        self.tAlgo = None
        self.nbCoups = 3 #{1 : piece, 2 : piece+nextPiece, 3 : piece+holdPiece}
        self.nbCoupsMax = 3
        #Calcul score
        self.modele = self.creer_reseau(lNbNoeuds)
        self.lScoresMax = [self.jeu.nbLignes, self.jeu.nbLignes, self.jeu.nbColonnes*self.jeu.nbLignes, self.jeu.nbColonnes*(self.jeu.nbLignes-1), self.jeu.nbLignes*(self.jeu.nbColonnes-1), 4, self.jeu.nbColonnes*(self.jeu.nbLignes*(self.jeu.nbLignes+1)//2)]
        self.nbInput = lNbNoeuds[0]
        assert len(self.lScoresMax) == self.nbInput
        #Positions prédites
        self.lPositionsPieces = []
        self.visuelPositions = False
        self.iPosition = 0
        self.dtPositionsInit = 100 #ms
        self.tPositionsAvant = pygame.time.get_ticks()

    def reset(self):
        #Positions prédites
        self.visuelPositions = False
        self.lPositionsPieces = []
        self.iPosition = 0
        self.tPositionsAvant = pygame.time.get_ticks()

    def changer_mode(self):
        if not self.jeu.modeAlgo:
            self.tAlgo = pygame.time.get_ticks()
        self.jeu.modeAlgo = not self.jeu.modeAlgo

    def calculer_toutes_positions(self):
        if self.nbCoups == 1:
            self.lPositionsPieces = self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece)
        elif self.nbCoups == 2 :
            if self.jeu.nextPiece.reset(self.jeu.grille):
                self.jeu.finJeu = True
                return
            self.lPositionsPieces = self.calculer_toutes_positions_2_coups(self.jeu.grille, self.jeu.piece, self.jeu.nextPiece)
        elif self.nbCoups == 3:
            if self.jeu.holdPiece is None:
                self.jeu.mettre_piece_hold()
            if self.jeu.holdPiece.reset(self.jeu.grille):
                self.jeu.finJeu = True
                return
            self.lPositionsPieces = [self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece), self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.holdPiece)]
        self.changer_visuel_positions()

    def calculer_toutes_positions_2_coups(self, grille, piece1, piece2):
        #BFS sur les 2 pièces puis merge des solutions sans overlap de p1 et p2
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        xOffsetG, xOffsetD, yOffsetH = 2, 2, 1

        #Partie1 : Piece normale
        grillePositions = [[0b0000 for x in range(nbColonnes+xOffsetG+xOffsetD)] for y in range(nbLignes+yOffsetH)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite | + 1 ligne en haut
        xInit1, yInit1, oInit1, tInit1 = piece1.x, piece1.y, piece1.orientation, piece1.type
        grillePositions[yInit1+yOffsetH][xInit1+xOffsetG] |= (1 << oInit1)
        file = deque([(xInit1+xOffsetG, yInit1+yOffsetH, oInit1)])
        lMatrices1 = [self.jeu.dicoMatricesPieces[(tInit1, o)] for o in range(4)]
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-xOffsetG, y2-yOffsetH, o2, tInit1, lMatrices1[o2]) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2] |= (1 << o2)
                    file.append((x2,y2,o2))
        lPositions1 = []
        for y in range(nbLignes):
            for x in range(nbColonnes+xOffsetG+xOffsetD):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-xOffsetG, y-yOffsetH+1, o, tInit1, lMatrices1[o]):
                            lPositions1.append((x-xOffsetG,y-yOffsetH,o,tInit1))

        #Partie2 : Piece suiviante
        lPositions2 = []
        grillePositions = [[0b0000 for x in range(nbColonnes+xOffsetG+xOffsetD)] for y in range(nbLignes+yOffsetH)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite | + 1 ligne en haut
        xInit2, yInit2, oInit2, tInit2 = piece2.x, piece2.y, piece2.orientation, piece2.type
        grillePositions[yInit2+yOffsetH][xInit2+xOffsetG] |= (1 << oInit2)
        file = deque([(xInit2+xOffsetG, yInit2+yOffsetH, oInit2)])
        lMatrices2 = [self.jeu.dicoMatricesPieces[(tInit2, i)] for i in range(4)]
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-xOffsetG, y2-yOffsetH, o2, tInit2, lMatrices2[o2]) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2]|= (1 << o2)
                    file.append((x2,y2,o2))
        for y in range(nbLignes+yOffsetH):
            for x in range(nbColonnes+xOffsetG+xOffsetD):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-xOffsetG, y-yOffsetH+1, o, tInit2, lMatrices2[o]):
                            lPositions2.append((x-xOffsetG,y-yOffsetH,o,tInit2))

        #Merge des 2 BFS
        lPositionsFinales = []
        for x1,y1,o1,t1 in lPositions1:
            self.jeu.mettre_dans_grille(grille, x1, y1, o1, t1, (0,0,0), False)
            for x2,y2,o2,t2 in lPositions2:
                if not self.jeu.tester_chevauchement(grille, x2, y2, o2, t2, lMatrices2[o2]):
                    lPositionsFinales.append((x1,y1,o1,t1,x2,y2,o2,t2))
            self.jeu.enlever_de_grille(grille, x1, y1, o1, t1, None, False)
        #lPositionsFinales.sort()
        return lPositionsFinales

    def calculer_toutes_positions_1_coup(self, grille, piece):
        #BFS sur la piece
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        xOffsetG, xOffsetD, yOffsetH = 2, 2, 1
        grillePositions = [[0b0000 for x in range(nbColonnes+xOffsetG+xOffsetD)] for y in range(nbLignes+yOffsetH)]  #[Est, Nord, Ouest, Sud] | +2 colonnes à gauche | + 2 colonnes à droite | + 1 ligne en haut
        xInit, yInit, oInit, tInit = piece.x, piece.y, piece.orientation, piece.type
        grillePositions[yInit+yOffsetH][xInit+xOffsetG] |= (1 << oInit)
        file = deque([(xInit+xOffsetG, yInit+yOffsetH, oInit)])
        lMatrices = [self.jeu.dicoMatricesPieces[(tInit, i)] for i in range(4)]
        while file:
            x,y,o = file.popleft()
            for dx,dy,do in dxyo :
                x2 = x+dx
                y2 = y+dy
                o2 = (o+do)%4
                if not self.jeu.tester_chevauchement(grille, x2-xOffsetG, y2-yOffsetH, o2, tInit, lMatrices[o2]) and not ((grillePositions[y2][x2] >> o2) & 1):
                    grillePositions[y2][x2] |= (1 << o2)
                    file.append((x2,y2,o2))
        lPositions = []
        for y in range(nbLignes+yOffsetH):
            for x in range(nbColonnes+xOffsetG+xOffsetD):
                for o in range(4):
                    if (grillePositions[y][x] >> o) & 1:
                        if self.jeu.tester_chevauchement(grille, x-xOffsetG, y-yOffsetH+1, o, tInit, lMatrices[o]):
                            lPositions.append((x-xOffsetG,y-yOffsetH,o,tInit))
        #keep que les solutions valides
        lPositionsFinales = lPositions
        #lPositionsFinales.sort()
        return lPositionsFinales

    def hauteur_max_grille(self, grille):
        #Retourne l'indice de la ligne la plus haute avec un bloc
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None:
                    return nbLignes-y
        return 0

    def hauteur_max_piece(self, x, y, o, t, nbLignesGrille):
        matrice = self.jeu.dicoMatricesPieces[(t, o)]
        dyMin = float("inf")
        for dx, dy in matrice:
            dyMin = min(dy, dyMin)
        return nbLignesGrille - (y + dyMin) if dyMin < float("inf") else None #None volontaire

    def somme_hauteurs_grille(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        sommeHauteurs = 0
        for x in range(nbColonnes):
            for y in range(nbLignes):
                if grille[y][x] is not None:
                    sommeHauteurs += (nbLignes-y)
                    break
            """else :
                sommeHauteurs += 0"""
        return sommeHauteurs

    def nb_trous_cube(self, grille):
        #cube 1*1 qui fait une BFS
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        grilleVus = [[False]*nbColonnes for _ in range(nbLignes)]
        file = deque([])
        for x in range(nbColonnes):
            if grille[0][x] is None:
                file.append((x, 0))
                grilleVus[0][x] = True
        while file:
            x,y = file.popleft()
            for dx,dy in dxy:
                x2 = x+dx
                y2 = y+dy
                if (0 <= x2 < nbColonnes) and (0 <= y2 < nbLignes) and (grille[y2][x2] is None) and (not grilleVus[y2][x2]):
                    grilleVus[y2][x2] = True
                    file.append((x2,y2))
        nbTrous = 0
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if (not grilleVus[y][x]) and (grille[y][x] is None):
                    nbTrous += 1
        return nbTrous

    def nb_trous_normal(self, grille):
        nbTrous = 0
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for x in range(nbColonnes):
            est_trou = False
            for y in range(nbLignes):
                if grille[y][x] is not None:
                    est_trou = True
                elif est_trou:
                    nbTrous += 1
        return nbTrous

    def irregularites(self, grille):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        nbIrregularites = 0
        yAvant = None
        for x in range(nbColonnes):
            y = -1
            while y+1 < nbLignes and grille[y+1][x] is None:
                y += 1
            if yAvant is None:
                yAvant = y
            nbIrregularites += abs(y-yAvant)
            yAvant = y
        return nbIrregularites

    def nb_lignes(self, grille):
        nbLignesASupprimer = sum(1 for ligne in grille if all(case is not None for case in ligne))
        return nbLignesASupprimer #self.jeu.dicoScores[nbLignesASupprimer]

    def calculer_meilleure_position_2_coups(self, grille, lPositions, modele=None):
        if not lPositions:
            return (None,None,None,None,None,None,None,None), -float("inf")
        if modele is None:
            modele = self.modele
        listeLCar = [None]*len(lPositions)
        for iP,(x1,y1,o1,t1,x2,y2,o2,t2) in enumerate(lPositions):
            lCar1,grilleTemp = self.caracteristiques(grille,x1,y1,o1,t1,in_place=False)
            lCar2,_ = self.caracteristiques(grilleTemp, x2, y2, o2, t2,in_place=True)
            listeLCar[iP] = [(car1+car2)/2 for car1, car2 in zip(lCar1, lCar2)]

        lInput = torch.tensor(listeLCar, dtype=torch.float32)
        with torch.no_grad():
            lScores = modele(lInput).squeeze(-1)
        iMax = torch.argmax(lScores).item()
        return lPositions[iMax], lScores[iMax]

    def calculer_meilleure_position_1_coup(self, grille, lPositions, modele=None):
        if not lPositions:
            return (None,None,None,None), -float("inf")
        if modele is None:
            modele = self.modele
        listeLCar = [None]*len(lPositions)
        for iP,(x,y,o,t) in enumerate(lPositions):
            listeLCar[iP], _ = self.caracteristiques(grille,x,y,o,t,in_place=True)
        
        lInput = torch.tensor(listeLCar, dtype=torch.float32)
        with torch.no_grad():
            lScores = modele(lInput).squeeze(-1)
        iMax = torch.argmax(lScores).item()
        return lPositions[iMax], lScores[iMax]

    def caracteristiques(self, grille0, X, Y, O, T, in_place=True):
        grille = grille0 if in_place else [ligne.copy() for ligne in grille0]
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        self.jeu.mettre_dans_grille(grille, X, Y, O, T, (0,0,0), coin=False)
        nbL = self.nb_lignes(grille)
        if nbL > 0:
            grilleTemp = self.jeu.tester_lignes(grille, reel=False, fScore=None)
        else :
            grilleTemp = grille
        hMaxG, sumHG, nbTN, I = 0, 0, 0, 0
        yMaxAvant = 0
        lY = [None]*nbColonnes
        for x in range(nbColonnes):
            yMax = 0
            nbTrous = 0
            est_trou = False
            for y in range(nbLignes):
                if grilleTemp[y][x] is not None:
                    if yMax == 0 :
                        yMax = nbLignes -y
                    hMaxG = max(hMaxG, nbLignes-y)
                else :
                    if not est_trou :
                        if y > 0 and grilleTemp[y-1][x] is not None:
                            est_trou = True
                            nbTrous = 1
                    else :
                        nbTrous += 1
            I += abs(yMaxAvant - yMax) if x > 0 else 0
            yMaxAvant = yMax
            nbTN += nbTrous
            sumHG += yMax
            lY[x] = yMax
        sommePuits = 0 + ((lY[1]-lY[0])*(lY[1]-lY[0]+1)//2 if lY[1] > lY[0] else 0) + ((lY[-2]-lY[-1])*(lY[-2]-lY[-1]+1)//2 if lY[-2] > lY[-1] else 0)
        for x in range(1, nbColonnes-1):
            hMinVoisins = min(lY[x-1], lY[x+1])
            ecart = hMinVoisins-lY[x]
            if ecart > 0:
                sommePuits += ecart*(ecart+1)//2
        hMaxP = self.hauteur_max_piece(X, Y, O, T, nbLignes)
        score = [hMaxG, hMaxP, sumHG, nbTN, I, nbL, sommePuits]
        scoreNormalise = [score[iS]/self.lScoresMax[iS] for iS in range(len(score))]
        self.jeu.enlever_de_grille(grille, X, Y, O, T, None, coin=False)
        #scoreNormalise = [scoreNormalise[2], scoreNormalise[6]]
        return scoreNormalise, grilleTemp

    def appliquer_position(self):
        if self.nbCoups == 1:
            self.lPositionsPieces = self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece)
            self.jouer_1_coup(self.jeu.grille, self.lPositionsPieces, self.jeu.piece)
        elif self.nbCoups == 2 :
            if self.jeu.nextPiece.reset(self.jeu.grille):
                self.jeu.finJeu = True
                return
            self.lPositionsPieces = self.calculer_toutes_positions_2_coups(self.jeu.grille, self.jeu.piece, self.jeu.nextPiece)
            self.jouer_2_coups(self.jeu.grille, self.lPositionsPieces, self.jeu.piece, self.jeu.nextPiece)
        elif self.nbCoups == 3 :
            if self.jeu.holdPiece is None:
                self.jeu.mettre_piece_hold()
            if self.jeu.holdPiece.reset(self.jeu.grille):
                self.jeu.finJeu = True
                return
            self.lPositionsPieces = [self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.piece), self.calculer_toutes_positions_1_coup(self.jeu.grille, self.jeu.holdPiece)]
            self.jouer_3_coups(self.jeu.grille, self.lPositionsPieces, self.jeu.piece, self.jeu.holdPiece)

    def appliquer_position_2_coups(self, grille, piece1, position1, piece2, position2, reel=True, fScore=None):
        #Piece 1
        x1,y1,o1,t1 = position1
        piece1.x = x1
        piece1.y = y1
        piece1.orientation = o1
        piece1.type = t1
        piece1.matrice = self.jeu.dicoMatricesPieces[(t1,o1)]
        piece1.fixer(grille, reel=reel, fScore=fScore)
        #Piece 2
        x2,y2,o2,t2 = position2
        piece2.x = x2
        piece2.y = y2
        piece2.orientation = o2
        piece2.type = t2
        piece2.matrice = self.jeu.dicoMatricesPieces[(t2,o2)]
        piece2.fixer(grille, reel=reel, fScore=fScore)

    def appliquer_position_1_coup(self, grille, piece, position, reel=True, fScore=None):
        x,y,o,t = position
        piece.x = x
        piece.y = y
        piece.orientation = o
        piece.type = t
        piece.matrice = self.jeu.dicoMatricesPieces[(t,o)]
        if reel :
            piece.couleur = self.jeu.dicoCouleursPieces[t]
        piece.fixer(grille, reel=reel, fScore=fScore)

    def jouer_1_coup(self, grille, lPositionsPieces, piece, jeu=None, modele=None, reel=True, fScore=None):
        meilleurePosition, meilleurScore = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces, modele)
        if any([arg is None for arg in meilleurePosition]):
            jeu = jeu if jeu is not None else self.jeu
            jeu.finJeu = True
            return
        self.appliquer_position_1_coup(grille, piece, meilleurePosition, reel, fScore=fScore)

    def jouer_2_coups(self, grille, lPositionsPieces, piece1, piece2):
        meilleurePosition, meilleurScore = self.calculer_meilleure_position_2_coups(grille, lPositionsPieces)
        if any([arg is None for arg in meilleurePosition]):
            self.jeu.finJeu = True
            return
        self.appliquer_position_2_coups(grille, piece1, meilleurePosition[:4], piece2, meilleurePosition[4:])

    def jouer_3_coups(self, grille, lPositionsPieces, piece, holdPiece, jeu=None, modele=None, reel=True, fScore=None):
        jeu = jeu if jeu is not None else self.jeu
        meilleurePositionPiece, scorePiece = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces[0], modele)
        meilleurePositionHold, scoreHold = self.calculer_meilleure_position_1_coup(grille, lPositionsPieces[1], modele)
        if scorePiece >= scoreHold:
            if any([arg is None for arg in meilleurePositionPiece]):
                jeu.finJeu = True
                return
            self.appliquer_position_1_coup(grille, piece, meilleurePositionPiece, reel, fScore=fScore)
        else :
            if any([arg is None for arg in meilleurePositionHold]):
                jeu.finJeu = True
                return
            jeu.mettre_piece_hold()
            self.appliquer_position_1_coup(grille, holdPiece, meilleurePositionHold, reel, fScore=fScore)

    def boucle_jeu(self):
        if not self.jeu.modeAlgo :
            return
        if self.dtAlgo > 0 and self.tAlgo+self.dtAlgo > pygame.time.get_ticks() :
            return
        self.tAlgo = pygame.time.get_ticks()
        self.appliquer_position()
        #self.jeu.tester_clavier_appuie(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))

    def changer_nb_coups(self, ajout):
        self.nbCoups = (self.nbCoups-1+ajout) % self.nbCoupsMax + 1
        self.jeu.texteNbCoupsAlgo = self.jeu.police.render(f"NbCoups Algo : {self.nbCoups}", False, self.jeu.couleurTextes)

    def afficher_toutes_positions(self):
        if not self.visuelPositions:
            return
        if self.nbCoups == 1:
            if self.iPosition >= len(self.lPositionsPieces):
                self.changer_visuel_positions()
                return
            x,y,o,t = self.lPositionsPieces[self.iPosition]
            self.jeu.mettre_dans_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        elif self.nbCoups == 2:
            if self.iPosition >= len(self.lPositionsPieces):
                self.changer_visuel_positions()
                return
            x1,y1,o1,t1,x2,y2,o2,t2 = self.lPositionsPieces[self.iPosition]
            self.jeu.mettre_dans_grille(self.jeu.grille, x1, y1, o1, t1, (0,0,0), coin=False)
            self.jeu.mettre_dans_grille(self.jeu.grille, x2, y2, o2, t2, (0,0,0), coin=False)
        elif self.nbCoups == 3:
            if self.iPosition >= len(self.lPositionsPieces[0])+len(self.lPositionsPieces[1]):
                self.changer_visuel_positions()
                return
            elif self.iPosition < len(self.lPositionsPieces[0]):
                x,y,o,t = self.lPositionsPieces[0][self.iPosition]
            else :
                x,y,o,t = self.lPositionsPieces[1][self.iPosition-len(self.lPositionsPieces[0])]
            self.jeu.mettre_dans_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)

    def desafficher_toutes_positions(self):
        if not self.visuelPositions:
            return
        if self.nbCoups == 1:
            x,y,o,t = self.lPositionsPieces[self.iPosition]
            self.jeu.enlever_de_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        elif self.nbCoups == 2:
            x1,y1,o1,t1,x2,y2,o2,t2 = self.lPositionsPieces[self.iPosition]
            self.jeu.enlever_de_grille(self.jeu.grille, x1, y1, o1, t1, (0,0,0), coin=False)
            self.jeu.enlever_de_grille(self.jeu.grille, x2, y2, o2, t2, (0,0,0), coin=False)
        elif self.nbCoups == 3:
            if self.iPosition < len(self.lPositionsPieces[0]):
                x,y,o,t = self.lPositionsPieces[0][self.iPosition]
            else :
                x,y,o,t = self.lPositionsPieces[1][self.iPosition-len(self.lPositionsPieces[0])]
            self.jeu.enlever_de_grille(self.jeu.grille, x, y, o, t, (0,0,0), coin=False)
        if pygame.time.get_ticks() >= self.tPositionsAvant + self.dtPositionsInit:
            self.tPositionsAvant = pygame.time.get_ticks()
            self.iPosition += 1

    def changer_visuel_positions(self):
        if self.visuelPositions:
            self.jeu.piece.bouge = True
            self.jeu.piece.tempsAvant = pygame.time.get_ticks()
        else :
            self.jeu.piece.bouge = False
            self.iPosition = 0
            self.tPositionsAvant = pygame.time.get_ticks()
        self.visuelPositions = not self.visuelPositions

    def creer_reseau(self, lNbNoeuds):
        lCouchesTorch = []
        for i in range(1, len(lNbNoeuds)):
            nbN1, nbN2 = lNbNoeuds[i-1], lNbNoeuds[i]
            lCouchesTorch.append(torch.nn.Linear(nbN1, nbN2))
            if i+1 < len(lNbNoeuds):
                lCouchesTorch.append(torch.nn.LeakyReLU(0.01))
        return torch.nn.Sequential(*lCouchesTorch)

    def charger_dico_reseau_sans_tensor(self, dicoReseau):
        dicoReseau2 = {k : torch.tensor(v, dtype=torch.float32) for k,v in dicoReseau.items()}
        self.modele.load_state_dict(dicoReseau2)

    def evaluation_algo(self, nbParties, modele, affichage, visuel, fonctionAvancement=None):
        tAvant = datetime.now()
        sommeScores, sommeNbCoups = 0,0
        scoreAvant, nbCoupsAvant = 0, 0
        visuelAvant = self.jeu.visuel
        self.jeu.visuel = visuel
        modeleAvant = self.modele
        self.modele = modele
        if nbParties < 1:
            return
        if affichage:
            print('\n\n')
        for iP in range(1, nbParties+1):
            if self.jeu.quitterProgramme :
                continue
            if affichage:
                print("\033[F\033[F", end="")
                print(' '*80 + '\r' + f"Résultats précédents : Score {scoreAvant} || Nb Coups : {nbCoupsAvant}")
                print(' '*80 + '\r' + f"Evaluation Algorithme : Partie {iP} ({(iP)/nbParties*100:.2f}%)", flush=True)
            if fonctionAvancement is not None:
                fonctionAvancement(100*iP/nbParties)
            self.jeu.jouer(modeAlgo=True)
            scoreAvant, nbCoupsAvant = self.jeu.score, self.jeu.nbCoups
            sommeScores += scoreAvant
            sommeNbCoups += nbCoupsAvant
        self.jeu.visuel = visuelAvant
        self.modele = modeleAvant
        scoreMoyen = sommeScores/nbParties
        nbCoupsMoyen = sommeNbCoups/nbParties
        t = datetime.now()
        if affichage:
            print(f"Résultats Finaux : ScoreMoyen = {scoreMoyen:.2f} || NbCoupsMoyen = {sommeNbCoups/nbParties:.2f}")
            print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")
        return (scoreMoyen,nbCoupsMoyen)



"""Faire max(score1 + max(score2)) pour chaque score1"""
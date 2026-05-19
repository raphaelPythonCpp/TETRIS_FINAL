import torch
from TETRIS_TETROMINO_v4 import*

class Individu_NN(torch.nn.Module):
    def __init__(self, jeu, algoEntrainement, algo, lNbNoeuds, dicoReseau, nbLignes, nbColonnes, iIndividu=None):
        super().__init__()
        
        self.jeu = jeu
        self.algoEntrainement = algoEntrainement
        self.algo = algo
        self.nbCoups = 0
        self.iIndividu = iIndividu
        
        self.lNbNoeuds = lNbNoeuds
        lCouchesTorch = []
        for i in range(1, len(lNbNoeuds)):
            nbN1, nbN2 = lNbNoeuds[i-1], lNbNoeuds[i]
            lCouchesTorch.append(torch.nn.Linear(nbN1, nbN2))
            if i+1 < len(lNbNoeuds):
                lCouchesTorch.append(torch.nn.LeakyReLU(0.01))
        self.modele = torch.nn.Sequential(*lCouchesTorch)
        self.dicoReseau = dicoReseau
        self.modele.load_state_dict(self.dicoReseau)
        self.score = 0
        self.finJeu = False
        #Grille
        self.nbLignes, self.nbColonnes = nbLignes, nbColonnes
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        #Pieces
        self.lPositionsPieces = []
        self.piece = None
        self.holdPiece = None
        self.reset()

    def reset(self):
        self.nbCoups = 0
        self.score = 0
        self.finJeu = False
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        self.lPositionsPieces = []
        self.holdPiece = None
        self.piece = None
        self.generer_piece()

    def generer_piece(self):
        if self.algoEntrainement.modeCoups == 3 and self.holdPiece is None : #au début
            self.holdPiece = Tetromino(self.jeu, self.algoEntrainement.lProchainesPieces[self.nbCoups], entrainement=True)
            self.holdPiece.reset(self.grille)
        prochainType = self.algoEntrainement.lProchainesPieces[self.nbCoups+1]
        if self.piece is None:
            self.piece = Tetromino(self.jeu, prochainType, entrainement=True)
        else :
            self.piece.type = prochainType
            self.piece.orientation = 0
            self.piece.matrice = self.jeu.dicoMatricesPieces[(prochainType, 0)]
            self.piece.couleur = self.jeu.dicoCouleursPieces[prochainType]
        if self.piece.reset(self.grille):
            self.finJeu = True

    def calculer_toutes_positions(self):
        if self.finJeu:
            return
        if self.algoEntrainement.modeCoups == 1 :
            self.lPositionsPieces = self.algo.calculer_toutes_positions_1_coup(self.grille, self.piece)
        elif self.algoEntrainement.modeCoups == 2:
            raise KeyError("Mode coups 2 pas implémenté !")
            self.lPositionsPieces = [self.algo.calculer_toutes_positions_2_coups(self.grille, self.piece, self.holdPiece), self.algo.calculer_toutes_positions_2_coups(self.grille, self.piece, self.holdPiece)] #ATTENTION : mettre nextPiece au lieu de holdPiece quand cela sera implémenté
        elif self.algoEntrainement.modeCoups == 3:
            self.lPositionsPieces = [self.algo.calculer_toutes_positions_1_coup(self.grille, self.piece), self.algo.calculer_toutes_positions_1_coup(self.grille, self.holdPiece)]

    def jouer_coup(self):
        if self.algoEntrainement.modeCoups == 1 :
            self.algo.jouer_1_coup(self.grille, self.lPositionsPieces, self.piece, jeu=self, modele=self.modele, reel=False, fScore=self.changer_score)
        elif self.algoEntrainement.modeCoups == 2:
            raise KeyError("Mode coups 2 pas implémenté !")
            self.algo.joueur_2_coups(self.grille, self.lPositionsPieces, self.piece, self.holdPiece, jeu=self, modele=self.modele, reel=False, fScore=self.changer_score)
        elif self.algoEntrainement.modeCoups == 3:
            self.algo.jouer_3_coups(self.grille, self.lPositionsPieces, self.piece, self.holdPiece, jeu=self, modele=self.modele, reel=False, fScore=self.changer_score)

    def jouer(self, calculerPositions=True, jouerCoup=True):
        if calculerPositions:
            self.calculer_toutes_positions()
        if jouerCoup:
            self.jouer_coup()
        self.nbCoups += 1
        if self.finJeu :
            return
        self.generer_piece()

    def appliquer_position(self, position):
        if self.finJeu:
            return
        if self.algoEntrainement.modeCoups == 1 :
            self.algo.appliquer_position_1_coup(self.grille, self.piece, position, reel=False, fScore=self.changer_score)
        elif self.algoEntrainement.modeCoups == 2:
            raise KeyError("Mode coups 2 pas implémenté !")
            self.algo.appliquer_position_2_coups(self.grille, self.piece, position[:4], self.nextPiece, position[:4])
        elif self.algoEntrainement.modeCoups == 3: #ATTENTION on suppose que le swap a été fait si nécessaire
            self.algo.appliquer_position_1_coup(self.grille, self.piece, position, reel=False, fScore=self.changer_score)

    def changer_score(self, gain):
        self.score += gain

    def mettre_piece_hold(self):
        if self.holdPiece is None:
            self.holdPiece = self.piece
            self.generer_piece()
        else :
            self.holdPiece, self.piece = self.piece, self.holdPiece
            if self.piece.reset(self.grille):
                self.finJeu = True

    def forward(self, lInput):
        return self.modele(lInput)
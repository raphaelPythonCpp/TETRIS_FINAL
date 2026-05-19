from random import uniform, shuffle, randint
from math import floor, ceil, sqrt
from datetime import datetime
from copy import deepcopy
import torch
from TETRIS_TETROMINO_v4 import*
from TETRIS_INDIVIDU_NN_v1 import*

class Algorithme_Genetique(object):
    def __init__(self, jeu, algo, lNbNoeuds, tauxSurvivant, tauxRandom, nbLignes, nbColonnes, modeCoups):
        self.jeu = jeu
        self.algo = algo
        self.visuelEntrainement = False
        
        self.nbGenerations = int(input("nbGenerations : "))
        self.nbParties = int(input("nbParties : "))
        self.lNbNoeuds = lNbNoeuds #ex : [(7, 8), (8, 1)] <=> 7 -> 8 -> ReLU -> 1

        self.nbLignes = nbLignes
        self.nbColonnes = nbColonnes
        
        self.tauxMutationInit = 0.15
        self.tauxMutationFin = 0.001
        self.tauxMutation = self.tauxMutationInit
        self.decrementationTM = (self.tauxMutationInit - self.tauxMutationFin) / max(self.nbGenerations - 1, 1) #(0.1 / self.tauxMutation) ** (1/self.nbGenerations)
        
        self.modeCoups = modeCoups
        #lProchainesPieces
        self.tauxPartiesRandomInit = 0.20
        self.tauxPartiesRandomFin = 0.80
        self.tauxPartiesRandom = self.tauxPartiesRandomInit
        self.augmentationTauxPartiesRandom = (self.tauxPartiesRandomFin - self.tauxPartiesRandomInit) / max(self.nbGenerations - 1, 1)
        self.nbPartiesMemes = round(self.nbParties * (1 - self.tauxPartiesRandom))
        self.nbPartiesRandom = self.nbParties - self.nbPartiesMemes
        self.listeLProchainesPieces = []
        for iP in range(self.nbPartiesMemes):
            self.listeLProchainesPieces.append(self.generer_pieces_partie())
        self.lProchainesPieces = self.listeLProchainesPieces[0]
        #Individus
        self.tauxSurvivant = tauxSurvivant #en pour 1 (ex : 0.2)
        self.tauxRandom = tauxRandom
        self.nbIndividus = int(input("nbIndividus : "))
        self.nbIndividusRechercheInit = int(input("nbIndividusRechercheInit : "))
        self.nbIndividusSurvivants = max(1, floor(self.nbIndividus * self.tauxSurvivant))
        self.nbIndividusRandom = floor(self.nbIndividus * self.tauxRandom)
        self.nbIndividusAModifier = ceil((self.nbIndividus - (self.nbIndividusSurvivants+self.nbIndividusRandom)) / self.nbIndividusSurvivants)
        self.lIndividus = []

    def reset(self):
        pass
    
    def entrainement(self):
        tAvant = datetime.now()
        sauvegardeFichiers = True
        lScoresRI, lNbCoupsRI, lDicoReseauRI, lDicoReseauERI = self.recherche_initiale(self.nbIndividus)
        lScores = [None for iG in range(self.nbGenerations)]
        lNbCoups = [None for iG in range(self.nbGenerations)]
        lDicoReseau = [self.lNbNoeuds] + [None for iG in range(self.nbGenerations)]
        lDicoReseau[1] = lDicoReseauRI[0][1]
        listeLDicoReseau = [lDicoReseauRI] + [None for iG in range(self.nbGenerations)]
        self.lIndividus = []
        for i in range(self.nbIndividus):
            self.lIndividus.append(Individu_NN(self.jeu, self, self.algo, self.lNbNoeuds, lDicoReseauERI[i], self.nbLignes, self.nbColonnes, i))
        for iG in range(self.nbGenerations):
            lRes = [[iI,0,0] for iI in range(self.nbIndividus)]
            for iP in range(self.nbParties):
                print('\r' + ' '*100 + f"\rEntrainement GA : Génération {iG+1} ({(iG+1)/self.nbGenerations*100:.2f}%) || Partie {iP+1} ({(iP+1)/self.nbParties*100:.2f}%) || tM : {self.tauxMutation:.2f} || tPR : {self.tauxPartiesRandom:.2f} ({self.nbPartiesRandom}/{self.nbParties})", end="", flush=True)                
                self.partie_entrainement(iP, lRes)

            self.lIndividus, lScores[iG], lNbCoups[iG], lDicoReseauPartie, _ = self.analyse_partie(lRes, self.lIndividus, self.nbParties, True)
            lDicoReseau[iG+1] = lDicoReseauPartie[0][1]
            listeLDicoReseau[iG+1] = lDicoReseauPartie

            iIndividuAM = self.nbIndividusSurvivants
            for iS in range(self.nbIndividusSurvivants):
                dicoReseau1 = self.lIndividus[iS].modele.state_dict()
                for _ in range(self.nbIndividusAModifier):
                    #iS2 = (iS+randint(0, self.nbIndividusSurvivants-1))%self.nbIndividusSurvivants
                    #dicoReseau2 = self.lIndividus[iS2].modele.state_dict()
                    if iIndividuAM < self.nbIndividus:
                        self.lIndividus[iIndividuAM].modele.load_state_dict(self.generer_dico_reseau_mutation(dicoReseau1, ecartMax=self.tauxMutation))
                        #self.lIndividus[iIndividuAM].modele.load_state_dict(self.generer_dico_reseau_crossover(dicoReseau1, dicoReseau2, lRes[iS][1], lRes[iS2][1], ecartMax=self.tauxMutation))
                        iIndividuAM += 1
            for iR in range(self.nbIndividusRandom):
                self.lIndividus[-(iR+1)].modele.load_state_dict(self.generer_reseau(self.lNbNoeuds, True, True))
            
            self.tauxMutation -= self.decrementationTM
            self.tauxPartiesRandom += self.augmentationTauxPartiesRandom
            self.nbPartiesMemes = round(self.nbParties * (1 - self.tauxPartiesRandom))
            self.nbPartiesRandom = self.nbParties - self.nbPartiesMemes
            
            if sauvegardeFichiers:
                with open("lScores_GA_NN.txt", "w") as fichier:
                    fichier.write(str(lScores))
                with open("lNbCoups_GA_NN.txt", "w") as fichier:
                    fichier.write(str(lNbCoups))
                with open("lDicoReseau_GA_NN.txt", "w") as fichier:
                    fichier.write(str(lDicoReseau))
                with open("listeLDicoReseau_GA_NN.txt", "w") as fichier:
                    fichier.write(str(listeLDicoReseau))
        dicoReseauFinal = {k: v.detach().cpu().numpy().tolist() for k, v in self.lIndividus[0].modele.state_dict().items()}
        #print(dicoReseauFinal)
        self.algo.modele.load_state_dict(self.lIndividus[0].modele.state_dict())
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")

    def partie_entrainement(self, iP, lRes):
        nbIndividusRestants = self.nbIndividus
        self.lProchainesPieces = self.listeLProchainesPieces[iP] if iP < self.nbPartiesMemes else self.generer_pieces_partie()
        for individu in self.lIndividus:
            individu.reset()
        nbCoups = 0
        while nbIndividusRestants > 0 and nbCoups < self.jeu.nbCoupsMax:
            nbCoups += 1
            for i, individu in enumerate(self.lIndividus):
                if individu.finJeu :
                    continue
                individu.jouer()
                """if individu.finJeu : #mort
                    nbIndividusRestants -= 1"""
                if self.visuelEntrainement :
                    self.jeu.fenetre.fill((0,0,0))
                    self.jeu.afficher_grille(individu.grille, self.jeu.tailleCase, self.jeu.xDebutCases, self.jeu.yDebutCases, piece=individu.piece, ombre=False, coin=False)
                    self.jeu.fenetre.blit(self.jeu.police.render(f"Score : {individu.score}", False, self.jeu.couleurTextes), (0, 0))
                    self.jeu.fenetre.blit(self.jeu.police.render(f"Individu : {i}", False, self.jeu.couleurTextes), (0, 30))
                    pygame.display.flip()
                    pygame.time.delay(50)
            nbIndividusRestants = sum(not individu.finJeu for individu in self.lIndividus)
        for iI, individu in enumerate(self.lIndividus):
            lRes[iI][1] += individu.score
            lRes[iI][2] += individu.nbCoups

    def analyse_partie(self, lRes, lIndividus, nbParties, affichage):
        lRes.sort(key=lambda res : res[1], reverse=True)
        if affichage:
            print('\n',*[(round(scoreM/nbParties), round(nbCoupsM/nbParties)) for iI, scoreM, nbCoupsM in lRes])
        lIndividus2 = [lIndividus[iI] for iI, _, _ in lRes]
        lScores2 = tuple((individu.iIndividu, round(res[1]/nbParties)) for individu, res in zip(lIndividus2, lRes))
        lNbCoups2 = tuple((individu.iIndividu, round(res[2]/nbParties)) for individu, res in zip(lIndividus2, lRes))
        lDicoReseau2 = [(individu.iIndividu, {k:v.detach().cpu().numpy().tolist() for k, v in individu.modele.state_dict().items()}) for individu in lIndividus2]
        lDicoReseauExploitable2 = [individu.modele.state_dict() for individu in lIndividus2]
        return lIndividus2, lScores2, lNbCoups2, lDicoReseau2, lDicoReseauExploitable2

    def recherche_initiale(self, nbIndividusApres):
        tAvant = datetime.now()
        self.lIndividus = []
        for i in range(self.nbIndividusRechercheInit):
            self.lIndividus.append(Individu_NN(self.jeu, self, self.algo, self.lNbNoeuds, self.generer_reseau(self.lNbNoeuds, True, True), self.nbLignes, self.nbColonnes, i))
        lRes = [[iI,0,0] for iI in range(self.nbIndividusRechercheInit)]
        
        for iP in range(self.nbParties):
            print('\r' + ' '*100 + f"\rRecherche Initiale GA : Partie {iP+1} ({(iP+1)/self.nbParties*100:.2f}%) || tPR : {self.tauxPartiesRandom:.2f}", end="", flush=True)                
            self.partie_entrainement(iP, lRes)

        self.lIndividus, lScores, lNbCoups, lDicoReseau, lDicoReseauExploitable = self.analyse_partie(lRes, self.lIndividus, self.nbParties, affichage=False)
        t = datetime.now()
        print(f"\n{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")
        with open("recherche_initiale_GA_NN.txt", "w") as fichier:
            fichier.write(str([self.nbIndividusRechercheInit, self.lNbNoeuds, lScores, lNbCoups]))
        return lScores[:nbIndividusApres], lNbCoups[:nbIndividusApres], lDicoReseau[:nbIndividusApres], lDicoReseauExploitable[:nbIndividusApres]

    def generer_pieces_partie(self):
        lProchainesPieces = []
        nbBags = ceil((self.jeu.nbCoupsMax+2)/len(self.jeu.lTypePieces)) if self.jeu.nbCoupsMax <= 1e4 else int(1e4)
        for i in range(nbBags):
            l = self.jeu.lTypePieces.copy()
            shuffle(l)
            lProchainesPieces.extend(l)
        return lProchainesPieces

    def generer_reseau(self, lNbNoeuds, poids, biais):
        dico = {}
        iC = 0
        for i in range(1, len(lNbNoeuds)):
            nbN1, nbN2 = lNbNoeuds[i-1], lNbNoeuds[i]
            if poids :
                limite = sqrt(6 / (nbN1 + nbN2))
                dico[f"{iC}.weight"] = torch.empty(nbN2, nbN1).uniform_(-1, +1)
            if biais:
                limite = sqrt(6 / (nbN1 + nbN2))
                dico[f"{iC}.bias"] = torch.empty(nbN2).uniform_(0, 0.01)
            iC += 2 #à cause du ReLU entre 
        return dico
    
    def generer_dico_reseau_mutation(self, dicoReseau1, ecartMax):
        #dicoReseau2 = {k : v + v*(torch.rand_like(v)*2 - 1)*ecartMax + (torch.rand_like(v)*2 - 1)*ecartMax for k,v in dicoReseau1.items()}
        dicoReseau2 = {k : v + v*torch.randn_like(v)*ecartMax + torch.randn_like(v)*ecartMax for k,v in dicoReseau1.items()}
        #dicoReseau2 = {k : v + v*(torch.rand_like(v)*2 - 1)*ecartMax + (torch.rand_like(v)*2 - 1)*ecartMax for k,v in dicoReseau1.items()}
        #dicoReseau2 = {k : v * (1+torch.randn_like(v)) for k,v in dicoReseau1.items()}
        return dicoReseau2
                   
    
    def generer_dico_reseau_crossover(self, dicoReseau1, dicoReseau2, score1, score2, ecartMax):
        dicoReseau3 = {}
        for (k1,v1),(k2,v2) in zip(dicoReseau1.items(), dicoReseau2.items()):
            assert k1 == k2 and v1.shape == v2.shape
            alpha = max(0.1, min(0.9, score1 / (score1+score2+1e-10)))
            masque = torch.rand_like(v1) < alpha if len(v1.shape) == 1 else (torch.rand(v1.shape[0], 1) < alpha).expand_as(v1)
            bruit = (torch.rand_like(v1)*2 -1) * ecartMax
            v3 = torch.where(masque, v1, v2) + bruit
            dicoReseau3[k1] = v3
        return dicoReseau3
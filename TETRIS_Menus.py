import pygame
from collections import deque
import numpy as np
import random as rd
from math import floor, ceil, sqrt
import datetime
from TETRIS_Tetromino import*

class Menus(object):
    def __init__(self, fenetre, lAttributsPolice, horloge, nbColonnes, nbLignes, visuel, audio, nbFramesAffichage, lNbNoeuds, algorithme, entrainementGreedy, entrainementGenetique, entrainementNES, entrainementDRL, gameInfini, charger_reseau, evaluation):
        self.horloge = horloge
        self.fenetre = fenetre

        self.actif = False

        self.dossier = "MENUS"
        self.dossierInput = "IMAGES_BASE"
        self.dossierOutput = "IMAGES_UTILES"

        self.wF, self.hF = self.fenetre.get_size()

        dicoNomsFichiersChiffres = {**{str(i) : f"{i}.png" for i in range(10)}, **{chr(65+i) : f"{chr(65+i)}.png" for i in range(26)}, '.' : "point.png", ',' : "virgule.png", ' ' : "espace.png", '-' : "moins.png"}
        self.generateurTexte = Generateur_Texte(self, lAttributsPolice, f"{self.dossier}\\{self.dossierInput}", "CARACTERES_TEXTE", f"{self.dossier}\\{self.dossierOutput}", dicoNomsFichiersChiffres, transparence=True, enregistrement=False)
        self.modeTexte = "POLICE" #ou "IMAGES"

        self.wBoutons = 50
        self.lPositionsBoutons = [[(5+i*1.1*self.wBoutons, 5) for i in range(10)], [(self.wF-(self.wBoutons+5+i*1.1*self.wBoutons), 5) for i in range(10)]]
        
        self.couleurTextes = (0,0,0)

        self.menuBoutique = Menu_Boutique(self)
        self.menuPersonnalisation = Menu_Personnalisation(self)
        self.menuJeu = Menu_Jeu(menus=self, lAttributsPolice=lAttributsPolice, horloge=self.horloge, nbColonnes=nbColonnes, nbLignes=nbLignes, visuel=visuel, nbFramesAffichage=nbFramesAffichage, lNbNoeuds=lNbNoeuds, algorithme=algorithme, entrainementGreedy=entrainementGreedy, entrainementGenetique=entrainementGenetique, entrainementNES=entrainementNES, entrainementDRL=entrainementDRL, gameInfini=gameInfini, charger_reseau=charger_reseau)
        self.menuDidactique = Menu_didactique(self, ["hauteur max grille", "hauteur max piece", "somme hauteurs", "nb trous normaux", "score irregularites", "nb lignes", "score puits"], 50, avecTorch=self.menuJeu.algorithme) #ATTENTION : pas le bon nom de fichier
        self.menuHome = Menu_home(self)
        self.menuGameOver = Menu_Game_Over(self)
        self.menuParametres = Menu_Parametres(self)
        self.menuCreation = Menu_Creation_Pieces(self, self.menuJeu.tailleMaxPieces)
        self.menuInfo = Menu_Info(self)
        self.menuEstimation = Menu_Estimation(self)
        self.menuClassement = Menu_Classement(self, nbScores=10)
        self.lMenus = [self.menuJeu, self.menuHome, self.menuDidactique, self.menuGameOver, self.menuParametres, self.menuCreation, self.menuInfo, self.menuEstimation, self.menuClassement, self.menuBoutique, self.menuPersonnalisation]

        self.lFonds = ["background_1.jpg", "background_2.jpeg", "background_3.jpg"]
        self.iFond = 0
        self.aImFond = 40
        self.changer_fond()

        self.audio = audio
        if self.audio :
            self.cheminMusiques = "MENUS\\MUSIQUES"
            self.lAlbums = [["musique_raphael_120.mpeg", "musique_raphael_180.mpeg", "musique_raphael_240.mpeg"], ["musique_joshua_90.mp3", "musique_joshua_120.mp3", "musique_joshua_180.mp3"]]
            self.iAlbum = 0 #0R 1J 2L ?
            self.musique = True
            self.volumeMusique = 0.1
            self.changer_musique()
            self.lSonsClique = [pygame.mixer.Sound(f"{self.cheminMusiques}\\{nom}") for nom in ["clique_1.mp3", "clique_2.mp3", "clique_3.mp3", "clique_4.mp3", "clique_5.mp3"]]
            self.iSonClique = 0
            self.sonCroc = pygame.mixer.Sound(f"{self.cheminMusiques}\\son_croc.mp3")
            self.sonSwap = pygame.mixer.Sound(f"{self.cheminMusiques}\\son_swap.mp3")
            self.sonMouvement = pygame.mixer.Sound(f"{self.cheminMusiques}\\son_mouvement.mp3")
            self.sonCollision = pygame.mixer.Sound(f"{self.cheminMusiques}\\son_collision.mp3")
            self.lSons = self.lSonsClique + [self.sonCroc, self.sonSwap, self.sonMouvement, self.sonCollision]
            self.son = True

        self.couleurTextes = self.menuPersonnalisation.qcuCouleurTextes.lCarres[self.menuPersonnalisation.qcuCouleurTextes.iCarre].get_at((0,0))[:3]

        if evaluation and self.menuJeu.algorithme:
            self.menuJeu.algo.evaluation_algo(nbParties=int(input("nbParties Evaluation : ")), modele=self.menuJeu.algo.modele, affichage=True, visuel=False)
        

    def boucle(self):
        self.actif = True
        while self.actif :
            self.horloge.tick(60)
            lEvents = []
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.actif = False
                    break
                else:
                    lEvents.append(event)
            self.gerer_souris(lEvents)
            self.afficher()

    def afficher(self):
        self.fenetre.fill((0,0,0))

        for menu in self.lMenus:
            if menu.actif :
                menu.afficher()

        pygame.display.flip()

    def gerer_souris(self, eventActif):
        for menu in self.lMenus:
            if menu.actif :
                menu.gerer_souris(eventActif)

    def modifier_dimensions(self, image, w=None, h=None):
        wI, hI = image.get_size()
        facteur = 1 if (w is None and h is None) else min(w/wI, h/hI) if (w is not None and h is not None) else w/wI if (w is not None) else h/hI
        dimensions2 = (int(wI * facteur), int(hI * facteur))
        image2 = pygame.transform.smoothscale(image, dimensions2)
        return image2, dimensions2

    def ouvrir_image(self, dossier1, dossier2, nom, dossier3=None, w=None, h=None, transparence=False, enregistrement=False):
        chemin = f"{dossier1}\\{dossier2}\\{nom}"
        image = pygame.image.load(chemin).convert_alpha() if transparence else pygame.image.load(chemin).convert()
        image, dimensions = self.modifier_dimensions(image, w, h)
        if enregistrement:
            try :
                pygame.image.save(image, f"{dossier1}\\{dossier3}\\{nom}")
            except :
                print(f"Erreur lors de l'enregistrement de {nom} dans {dossier1}\\{dossier3}")
        return image, dimensions

    def extraire_tous_boutons(self, dossier1, dossier2, dossier3, nom, lNomsBoutons):
        imageAsset, (wA, hA) = self.ouvrir_image(dossier1, dossier2, nom, dossier3=None, h=None, transparence=True, enregistrement=False)
        vu = [[imageAsset.get_at((x,y))[3] == 0 for x in range(wA)] for y in range(hA)]
        lDXY = [(x,y) for x in range(-1,2) for y in range(-1,2) if x != 0 or y != 0]
        lRectangles = []
        for Y in range(hA):
            for X in range(wA):
                if vu[Y][X]:
                    continue
                vu[Y][X] = True
                file = deque([(X,Y)])
                xMin,xMax,yMin,yMax = X,X,Y,Y
                while file:
                    x,y = file.popleft()
                    for dx,dy in lDXY:
                        x2, y2 = x+dx, y+dy
                        if (0 <= x2 < wA) and (0 <= y2 < hA) and not vu[y2][x2]:
                            vu[y2][x2] = True
                            file.append((x2,y2))
                            xMin = min(xMin, x2)
                            xMax = max(xMax, x2)
                            yMin = min(yMin, y2)
                            yMax = max(yMax, y2)
                lRectangles.append((xMin, yMin, xMax-xMin+1, yMax-yMin+1))
        for rectangle, nomBouton in zip(lRectangles, lNomsBoutons):
            bouton = imageAsset.subsurface(rectangle).copy()
            pygame.image.save(bouton, f"{dossier1}\\{dossier3}\\{nomBouton}.png")

    def changer_couleur(self, image, facteur):
        image2 = image.copy()
        rgb = pygame.surfarray.pixels3d(image2)
        #alpha = pygame.surfarray.pixels_alpha(image2)
        rgb[:] = np.clip(rgb * facteur, 0, 255)
        return image2

    def changer_musique(self):
        if not self.audio:
            return
        pygame.mixer.music.load(f"{self.cheminMusiques}\\{self.lAlbums[self.iAlbum][self.menuHome.iNiveau]}")
        pygame.mixer.music.set_volume(self.volumeMusique)
        if self.musique :
            pygame.mixer.music.play(-1)

    def changer_fond(self):
        for menu in self.lMenus:
            menu.imFond = Image(self, menu, self.dossier, f"{self.dossierInput}\\IMAGES", self.dossierOutput, self.lFonds[self.iFond], None, self.hF, (0, 0), False, True)
        self.changer_transparence_fond()

    def changer_transparence_fond(self):
        for menu in self.lMenus:
            menu.imFond.image.set_alpha(self.aImFond)






class Menu_home(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteHome = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_home.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteHome.position = ((self.menus.wF-self.texteHome.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonQuitter = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "quitter_1.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonJouer2 = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "jouer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonMenuDidactique = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "journal.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][2], True, False)
        self.boutonMenuParametres = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "options.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonMenuCreation = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "inventaire.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][1], True, False)
        self.boutonMenuInfo = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "info.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][3], True, False)
        self.boutonMenuEstimation = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "amis.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][4], True, False)
        self.boutonMenuClassement = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "succes.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][5], True, False)
        self.boutonMenuBoutique = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "boutique.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)
        self.boutonMenuPersonnalisation = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "coffre.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][2], True, False)

        wBoutonsNiveau = 150
        xInitBoutonsNiveau = self.menus.wF/2 - 3/2*1.1*wBoutonsNiveau
        lPositionsBoutonsNiveau = [(xInitBoutonsNiveau+i*1.1*wBoutonsNiveau, 480) for i in range(3)]
        lPositionsImFormeNiveau = [(xBN, yBN + wBoutonsNiveau/2) for xBN, yBN in lPositionsBoutonsNiveau]
        self.boutonEasy = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "easy.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[0], True, False)
        self.imFormeEasy = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "easy_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[0], True, False)
        self.imGrilleEasy = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "grille_I_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleEasy.position = (lPositionsBoutonsNiveau[0][0], lPositionsBoutonsNiveau[0][1]-80-self.imGrilleEasy.dimensions[1]/2)
        self.boutonMedium = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "medium.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[1], True, False)
        self.imFormeMedium = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "medium_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[1], True, False)
        self.imGrilleMedium = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "grille_T_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleMedium.position = (lPositionsBoutonsNiveau[1][0], lPositionsBoutonsNiveau[1][1]-80-self.imGrilleMedium.dimensions[1]/2)
        self.boutonHard = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "hard.png", wBoutonsNiveau, None, lPositionsBoutonsNiveau[2], True, False)
        self.imFormeHard = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "hard_forme.png", wBoutonsNiveau, None, lPositionsImFormeNiveau[2], True, False)
        self.imGrilleHard = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "grille_X_blanc.png", wBoutonsNiveau, None, None, True, False)
        self.imGrilleHard.position = (lPositionsBoutonsNiveau[2][0], lPositionsBoutonsNiveau[2][1]-80-self.imGrilleHard.dimensions[1]/2)

        self.lNiveaux = [("Easy", self.imFormeEasy), ("Medium", self.imFormeMedium), ("Hard", self.imFormeHard)]
        self.iNiveau = 0
        self.niveau = self.lNiveaux[self.iNiveau]

        self.boutonJouer = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "logo_3.png", None, 0.44*self.menus.hF, None, True, False)
        self.boutonJouer.image.position = (self.menus.wF/2 - self.boutonJouer.image.dimensions[0]/2, self.menus.hF/2+30-self.boutonJouer.image.dimensions[1])

        self.lImages = [self.imGrilleEasy, self.imGrilleMedium, self.imGrilleHard, self.texteHome]
        self.lBoutons = [self.boutonMenuDidactique, self.boutonEasy, self.boutonMedium, self.boutonHard, self.boutonJouer, self.boutonMenuParametres, self.boutonMenuCreation, self.boutonMenuInfo, self.boutonMenuEstimation, self.boutonMenuClassement, self.boutonMenuBoutique, self.boutonMenuPersonnalisation]
        self.lElements = self.lImages + self.lBoutons

    def reset(self):
        #self.changer_mode_texte()
        pass

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.niveau[1].afficher(self.menus.fenetre)

        lTouchesPressees = pygame.key.get_pressed()
        if self.boutonQuitter.hover and not lTouchesPressees[pygame.K_q] :
            self.boutonJouer2.afficher(self.menus.fenetre)
        else :
            self.boutonQuitter.afficher(self.menus.fenetre)

    def gerer_souris(self, lEvents):
        lTouchesPressees = pygame.key.get_pressed()
        if self.boutonQuitter.gerer_souris() and lTouchesPressees[pygame.K_q]:
            self.actif = False
            self.menus.actif = False
        if self.boutonJouer2.gerer_souris() and not lTouchesPressees[pygame.K_q]:
            self.actif = False
            self.menus.menuJeu.actif = True
            self.menus.menuJeu.modeGrille = self.iNiveau
            self.menus.menuJeu.reset()
        if self.boutonMenuDidactique.gerer_souris():
            self.actif = False
            self.menus.menuDidactique.actif = True
            self.menus.menuDidactique.reset()
        if self.boutonMenuParametres.gerer_souris():
            self.actif = False
            self.menus.menuParametres.actif = True
            self.menus.menuParametres.reset()
        if self.boutonMenuCreation.gerer_souris():
            self.actif = False
            self.menus.menuCreation.actif = True
            self.menus.menuCreation.reset()
        if self.boutonMenuInfo.gerer_souris():
            self.actif = False
            self.menus.menuInfo.actif = True
            self.menus.menuInfo.reset()
        if self.boutonMenuEstimation.gerer_souris():
            self.actif = False
            self.menus.menuEstimation.actif = True
            self.menus.menuEstimation.reset()
        if self.boutonMenuClassement.gerer_souris():
            self.actif = False
            self.menus.menuClassement.actif = True
            self.menus.menuClassement.reset()
        if self.boutonMenuBoutique.gerer_souris():
            self.actif = False
            self.menus.menuBoutique.actif = True
            self.menus.menuBoutique.reset()
        if self.boutonMenuPersonnalisation.gerer_souris():
            self.actif = False
            self.menus.menuPersonnalisation.actif = True
            self.menus.menuPersonnalisation.reset()

        if self.boutonEasy.gerer_souris():
            self.iNiveau = 0
            self.niveau = self.lNiveaux[self.iNiveau]
            self.menus.changer_musique()
        if self.boutonMedium.gerer_souris():
            self.iNiveau = 1
            self.niveau = self.lNiveaux[self.iNiveau]
            self.menus.changer_musique()
        if self.boutonHard.gerer_souris():
            self.iNiveau = 2
            self.niveau = self.lNiveaux[self.iNiveau]
            self.menus.changer_musique()
        if self.boutonJouer.gerer_souris():
            self.actif = False
            self.menus.menuJeu.actif = True
            self.menus.menuJeu.modeGrille = self.iNiveau
            self.menus.menuJeu.reset()






class Menu_Parametres(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteParametres = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_parametres.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteParametres.position = ((self.menus.wF-self.texteParametres.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)
        self.boutonMusiqueOn = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "musique.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonMusiqueOff = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "musique_off.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonSonOn = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "son.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][1], True, False)
        self.boutonSonOff = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "silencieux.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][1], True, False)
        self.boutonFond = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer_image.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][2], True, False)
        self.boutonMusique = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer_musique.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][3], True, False)
        self.boutonSon = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer_son.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][4], True, False)

        self.sliderMusique = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="volume Musique", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_vert.png", nomForme="forme_verte.png", rectangleFond=(0.025*self.menus.wF, 0.15*self.menus.hF, 0.95*self.menus.wF, 0.2*self.menus.hF), caracteristiquesTexte=(0.3, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=16, iValeur=3, couleurFond=(255,0,255,180), couleurTexte=(0,0,0,128), interactif=True)
        self.sliderSon = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="volume Son Clic", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_vert.png", nomForme="forme_verte.png", rectangleFond=(0.025*self.menus.wF, 0.45*self.menus.hF, 0.95*self.menus.wF, 0.2*self.menus.hF), caracteristiquesTexte=(0.3, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=16, iValeur=3, couleurFond=(255,0,255,180), couleurTexte=(0,0,0,128), interactif=True)
        self.sliderLuminosite = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Luminosite fond", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_orange.png", nomForme="forme_orange.png", rectangleFond=(0.025*self.menus.wF, 0.75*self.menus.hF, 0.95*self.menus.wF, 0.2*self.menus.hF), caracteristiquesTexte=(0.3, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=16, iValeur=3, couleurFond=(128,128,128,180), couleurTexte=(0,0,0,128), interactif=True)


        self.lImages = [self.texteParametres]
        self.lBoutons = [self.boutonHome, self.boutonEcriture, self.boutonFond, self.boutonMusique, self.boutonSon]
        self.lSliders = [self.sliderMusique, self.sliderSon, self.sliderLuminosite]
        self.lElements = self.lImages + self.lBoutons + self.lSliders

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        if self.menus.audio:
            if self.menus.musique :
                self.boutonMusiqueOn.afficher(self.menus.fenetre)
            else:
                self.boutonMusiqueOff.afficher(self.menus.fenetre)
            if self.menus.son:
                self.boutonSonOn.afficher(self.menus.fenetre)
            else :
                self.boutonSonOff.afficher(self.menus.fenetre)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()
        if self.boutonFond.gerer_souris():
            self.menus.iFond = (self.menus.iFond+1)%len(self.menus.lFonds)
            self.menus.changer_fond()
        if self.boutonMusique.gerer_souris() and self.menus.audio:
            self.menus.iAlbum = (self.menus.iAlbum+1)%len(self.menus.lAlbums)
            self.menus.changer_musique()
        if self.boutonSon.gerer_souris() and self.menus.audio:
            self.menus.iSonClique = (self.menus.iSonClique+1)%len(self.menus.lSonsClique)

        if self.menus.audio :
            if self.menus.musique :
                if self.boutonMusiqueOn.gerer_souris():
                    self.menus.musique = False
                    self.menus.changer_musique()
            else:
                if self.boutonMusiqueOff.gerer_souris() and self.menus.audio:
                    self.menus.musique = True
                    self.menus.changer_musique()
            if self.menus.son:
                if self.boutonSonOn.gerer_souris() and self.menus.audio:
                    self.menus.son = False
            else :
                if self.boutonSonOff.gerer_souris() and self.menus.audio:
                    self.menus.son = True

        for slider in self.lSliders:
            changement = slider.gerer_souris()
            if changement:
                if slider == self.sliderMusique and self.menus.audio:
                    self.menus.volumeMusique = self.sliderMusique.valeur/100
                    pygame.mixer.music.set_volume(self.menus.volumeMusique)
                elif slider == self.sliderSon and self.menus.audio:
                    self.menus.lSons[self.menus.iSonClique].set_volume(self.sliderSon.valeur/100)
                elif slider == self.sliderLuminosite:
                    self.menus.aImFond = int(255 * self.sliderLuminosite.valeur/100)
                    self.menus.changer_transparence_fond()
        
    def changer_mode_texte(self):
        for slider in self.lSliders:
            slider.changer_mode_texte()






class Menu_Creation_Pieces(object):
    def __init__(self, menus, nbCases):
        self.menus = menus

        self.actif = False

        self.nbCases = nbCases
        self.grille = [[False]*self.nbCases for _ in range(self.nbCases)]
        self.tailleCases = min(self.menus.wF*0.8, self.menus.hF*0.8)/self.nbCases
        self.xMin, self.yMin = self.menus.wF/2-self.nbCases/2*self.tailleCases, max(self.menus.hF/2-self.nbCases/2*self.tailleCases, 0.15*self.menus.hF)
        self.xMax, self.yMax = self.xMin+self.nbCases*self.tailleCases, self.yMin+self.nbCases*self.tailleCases

        self.prefixeNoms = "PieceAjoutee"
        self.lDXY = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteCreation = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_creation.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteCreation.position = ((self.menus.wF-self.texteCreation.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonSauvegarder = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "sauvegarder.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonSupprimer = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "quitter_3.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][1], True, False)
        self.boutonReset = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][2], True, False)


        self.lImages = [self.texteCreation]
        self.lBoutons = [self.boutonHome, self.boutonSauvegarder, self.boutonSupprimer, self.boutonReset]
        self.lElements = self.lImages + self.lBoutons

        with open("dicoMatricesPiecesJolies.txt") as fichier:
            self.dicoMatricesPieces = eval(fichier.read())

    def reset(self):
        pass
        #self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.menus.menuJeu.afficher_grille(self.grille, self.tailleCases, self.xMin, self.yMin, orientation=0, piece=None, ombre=False, coin=False)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
            self.menus.menuJeu.charger_matrices(self.dicoMatricesPieces)
            sTypePieces = set()
            for k,o in self.menus.menuJeu.dicoMatricesPieces.keys():
                if k not in sTypePieces:
                    sTypePieces.add(k)
            self.menus.menuJeu.lTypePieces = list(sTypePieces)
        if self.boutonSauvegarder.gerer_souris():
            self.ajouter_piece(self.grille)
        if self.boutonSupprimer.gerer_souris():
            self.supprimer_toutes_pieces()
        if self.boutonReset.gerer_souris():
            self.grille = [[False]*self.nbCases for _ in range(self.nbCases)]
        for event in lEvents:
            if event.type == pygame.MOUSEBUTTONDOWN:
                xS, yS = event.pos
                if self.xMin <= xS <= self.xMax and self.yMin <= yS <= self.yMax:
                    iX = int((xS-self.xMin)/self.tailleCases)
                    iY = int((yS-self.yMin)/self.tailleCases)
                    self.grille[iY][iX] = not self.grille[iY][iX]

    def ajouter_piece(self, grille):
        grille_valide = True
        grilleVu = [[False]*len(grille[0]) for _ in range(len(grille))]
        BFS_faite = False
        for y in range(len(grille)):
            for x in range(len(grille[y])):
                if not grille[y][x] or grilleVu[y][x]:
                    continue
                if BFS_faite:
                    grille_valide = False
                else :
                    grilleVu = self.bfs(grille, grilleVu, x, y, self.lDXY)
                    BFS_faite = True
        if not grille_valide:
            print("piece non valide")
            return
        nom = f"{self.prefixeNoms}_{len(self.dicoMatricesPieces)//4}"
        grilleBin = [[1 if case else 0 for case in ligne] for ligne in grille]
        for o in range(4):
            self.dicoMatricesPieces[(nom, o)] = grilleBin.copy()
            grilleBin = list(list(reversed(ligne)) for ligne in zip(*grilleBin))
        self.menus.menuJeu.dicoCouleursPieces[nom] = (rd.randint(0,255), rd.randint(0,255), rd.randint(0,255))
        self.grille = [[False]*self.nbCases for _ in range(self.nbCases)]

    def supprimer_toutes_pieces(self):
        self.dicoMatricesPieces = {(nom,o):matrice for (nom,o),matrice in self.dicoMatricesPieces.items() if not nom.startswith(self.prefixeNoms)}
        self.menus.menuJeu.dicoCouleursPieces = {nom:couleur for nom,couleur in self.menus.menuJeu.dicoCouleursPieces.items() if not nom.startswith(self.prefixeNoms)}

    def bfs(self, grille, grilleVu, x0, y0, lDXY):
        nbLignes, nbColonnes = len(grille), len(grille[0])
        file = deque([(x0,y0)])
        grilleVu[y0][x0] = True
        while file:
            x,y = file.popleft()
            for dx,dy in lDXY:
                x2 = x+dx
                y2 = y+dy
                if (0 <= x2 < nbColonnes) and (0 <= y2 < nbLignes) and grille[y2][x2] and not (grilleVu[y2][x2]):
                    grilleVu[y2][x2] = True
                    file.append((x2,y2))
        return grilleVu





class Menu_Info(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteInfo = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_info.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteInfo.position = ((self.menus.wF-self.texteInfo.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)

        self.lImages = [self.texteInfo]
        self.lBoutons = [self.boutonHome, self.boutonEcriture]
        self.lElements = self.lImages + self.lBoutons

        self.changer_mode_texte()

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.menus.fenetre.blit(self.texte1, self.positionTexte1)
        self.menus.fenetre.blit(self.texte2, self.positionTexte2)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()

    def changer_mode_texte(self):
        self.texte1 = self.menus.generateurTexte.creer_surface_texte(f"Pour voir comment jouer, lire le fichier README.txt du dossier", 0.9*self.menus.wF, 0.3*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexte1 = (self.menus.wF/2-self.texte1.get_width()/2, 0.3*self.menus.hF)
        self.texte2 = self.menus.generateurTexte.creer_surface_texte(f"Il est egalement possible de visionner le diaporama de presentation presentation-projet-tetris.pdf", 0.9*self.menus.wF, 0.3*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexte2 = (self.menus.wF/2-self.texte2.get_width()/2, self.positionTexte1[1]+self.texte1.get_height()+0.1*self.menus.hF)





class Menu_Estimation(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.boutonEstimation = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_estimation.png", None, 0.08*self.menus.hF, None, True, False)
        self.boutonEstimation.image.position = ((self.menus.wF-self.boutonEstimation.image.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonJusteTemps = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_juste_temps.png", None, 0.08*self.menus.hF, None, True, False)
        self.boutonJusteTemps.image.position = ((self.menus.wF-self.boutonJusteTemps.image.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonParticipation = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_participation.png", None, 0.08*self.menus.hF, None, True, False)
        self.boutonParticipation.image.position = ((self.menus.wF-self.boutonParticipation.image.dimensions[0])/2, 0.01*self.menus.hF)
        self.lBoutonsTitre = [self.boutonEstimation, self.boutonJusteTemps, self.boutonParticipation]
        self.iBoutonsTitre = 0
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)
        self.boutonValider = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "confirmer_2.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonReset = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][1], True, False)

        self.trouve = False
        self.sliderR = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage de Participation de R", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_vert.png", nomForme="forme_verte.png", rectangleFond=(0.025*self.menus.wF, 0.15*self.menus.hF, 0.95*self.menus.wF, 0.15*self.menus.hF), caracteristiquesTexte=(0.45, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(0,255,0,180), couleurTexte=(0,0,0,128), interactif=True)
        self.sliderJ = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage de Participation de J", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_bleu.png", nomForme="forme_bleue.png", rectangleFond=(0.025*self.menus.wF, 0.35*self.menus.hF, 0.95*self.menus.wF, 0.15*self.menus.hF), caracteristiquesTexte=(0.45, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(0,0,255,180), couleurTexte=(0,0,0,128), interactif=True)
        self.sliderL = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage de Participation de L", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_violet.png", nomForme="forme_violette.png", rectangleFond=(0.025*self.menus.wF, 0.55*self.menus.hF, 0.95*self.menus.wF, 0.15*self.menus.hF), caracteristiquesTexte=(0.45, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(255,0,255,180), couleurTexte=(0,0,0,128), interactif=True)
        self.sliderAccuracy = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage Accuracy", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_rouge.png", nomForme="forme_rouge.png", rectangleFond=(0.025*self.menus.wF, 0.75*self.menus.hF, 0.95*self.menus.wF, 0.15*self.menus.hF), caracteristiquesTexte=(0.45, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(255,0,0,180), couleurTexte=(0,0,0,128), interactif=False)

        self.lValeursATrouver = [0.85, 0.15, 0]

        self.lImages = []
        self.lBoutons = [self.boutonHome, self.boutonEcriture, self.boutonValider, self.boutonReset]
        self.lSliders = [self.sliderR, self.sliderJ, self.sliderL, self.sliderAccuracy]
        self.lElements = self.lImages + self.lBoutons

        self.calculer_accuracy()
        self.changer_mode_texte()

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        self.lBoutonsTitre[self.iBoutonsTitre].afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        if self.trouve:
            for texte, positionTexte in zip(self.lTextes, self.lPositionTextes):
                self.menus.fenetre.blit(texte, positionTexte)
        else :
            for slider in self.lSliders:
                slider.afficher(self.menus.fenetre)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.lBoutonsTitre[self.iBoutonsTitre].gerer_souris():
            self.iBoutonsTitre = (self.iBoutonsTitre+1)%len(self.lBoutonsTitre)
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()
        if self.boutonValider.gerer_souris() and self.accuracy == 1:
            self.trouve = not self.trouve
            if not self.trouve:
                for slider in self.lSliders[:3] :
                    slider.iValeur = 0
                    slider.maj_valeur()
        if self.boutonReset.gerer_souris() and not self.trouve:
            for slider in self.lSliders[:3] :
                slider.iValeur = 0
                slider.maj_valeur()
        
        changement = False
        for slider in self.lSliders:
            changement |= slider.gerer_souris()
        if changement :
            self.calculer_accuracy()

    def changer_mode_texte(self):
        lNoms = [f"Au depart, la repartition etait plutot equitable", f"Au milieu de projet, seul R travaillait", f"A la fin du projet, seuls R et J travaillaient", f"L n a meme pas daigne faire sa partie de musique, alors qu il pouvait", f"Donc seul lui doit etre penalise"]
        yDebut = 0.2
        hTextes = (1-yDebut)*self.menus.hF / len(lNoms)
        self.lTextes, self.lPositionTextes = [], []
        for i,nom in enumerate(lNoms):
            self.lTextes.append(self.menus.generateurTexte.creer_surface_texte(nom, 0.9*self.menus.wF, hTextes, 0.05, self.menus.couleurTextes))
            self.lPositionTextes.append((self.menus.wF/2-self.lTextes[-1].get_width()/2, yDebut*self.menus.hF + hTextes*i))
        self.lTextes.append(self.menus.generateurTexte.creer_surface_texte("btw ceci peut s apparenter a une descente de gradient, ou GD, donc c est aussi didactique", 0.9*self.menus.wF, 0.05*self.menus.hF, 0.05, self.menus.couleurTextes))
        self.lPositionTextes.append((self.menus.wF/2-self.lTextes[-1].get_width()/2, self.menus.hF-self.lTextes[-1].get_height()))
        for slider in self.lSliders:
            slider.changer_mode_texte()

    def calculer_accuracy(self):
        self.accuracy = 1 - sum(abs(slider.valeur/100 - valeurATrouver) for slider,valeurATrouver in zip(self.lSliders[:3], self.lValeursATrouver)) / len(self.lValeursATrouver)
        self.sliderAccuracy.changer_valeur(100*self.accuracy, reel=False)





class Menu_Classement(object):
    def __init__(self, menus, nbScores):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteClassement = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_perdu.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteClassement.position = ((self.menus.wF-self.texteClassement.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)

        self.nbScores = nbScores
        self.lSliders = []
        yMinSliders = 0.13
        dySliders = (1-yMinSliders) / self.nbScores
        hSliders = dySliders * 0.9
        for i in range(self.nbScores):
            self.lSliders.append(Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom=f"Score {i}", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_rouge.png", nomForme="forme_rouge.png", rectangleFond=(0.32*self.menus.wF, (yMinSliders+dySliders*i)*self.menus.hF, 0.3*self.menus.wF, hSliders*self.menus.hF), caracteristiquesTexte=(0.25, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(255,0,0,180), couleurTexte=(0,0,0,128), interactif=False))
            self.lSliders.append(Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom=f"Nb Coups {i}", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_vert.png", nomForme="forme_verte.png", rectangleFond=(0.67*self.menus.wF, (yMinSliders+dySliders*i)*self.menus.hF, 0.3*self.menus.wF, hSliders*self.menus.hF), caracteristiquesTexte=(0.25, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(0,255,0,180), couleurTexte=(0,0,0,128), interactif=False))
        self.lDates, self.lTextes = [], []

        self.lImages = [self.texteClassement]
        self.lBoutons = [self.boutonHome, self.boutonEcriture]
        self.lElements = self.lImages + self.lBoutons + self.lSliders

    def reset(self):
        with open("liste_anciens_resultats_jeu.txt", 'r') as fichier:
            lDicoRes = eval('['+','.join(fichier.readlines())+']')
        lDicoRes.sort(key=lambda dico:dico["score"], reverse=True)
        lDicoRes = lDicoRes[:min(self.nbScores, len(lDicoRes))]
        scoreMax = max(dicoRes["score"] for dicoRes in lDicoRes)
        nbCoupsMax = max(dicoRes["nbCoups"] for dicoRes in lDicoRes)
        self.lDates = []
        for i, dicoRes in enumerate(lDicoRes):
            self.lDates.append(f"{dicoRes['date'].day} - {dicoRes['date'].month} - {dicoRes['date'].year}")
            score, nbCoups = dicoRes["score"], dicoRes["nbCoups"]
            nbLignesMax = (4*nbCoupsMax)//self.menus.menuJeu.nbColonnes
            #scoreMax = nbLignesMax//4 * self.menus.menuJeu.dicoScores[4] + self.menus.menuJeu.dicoScores[nbLignesMax%4]
            self.lSliders[2*i].changer_valeur(100* score / scoreMax)
            self.lSliders[2*i+1].changer_valeur(100* nbCoups / nbCoupsMax)
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        for texte,positionTexte in self.lTextes:
            self.menus.fenetre.blit(texte, positionTexte)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()
        for slider in self.lSliders:
            slider.gerer_souris()

    def changer_mode_texte(self):
        self.lTextes = []
        for i,date in enumerate(self.lDates):
            texte = self.menus.generateurTexte.creer_surface_texte(date, 0.3*self.menus.wF, self.lSliders[2*i].hFond, 0.05, self.menus.couleurTextes)
            positionTexte = (0.15*self.menus.wF - texte.get_width()/2, self.lSliders[2*i].yFond + self.lSliders[2*i].hFond/2 - texte.get_height()/2)
            self.lTextes.append((texte,positionTexte))
        for slider in self.lSliders:
            slider.changer_mode_texte()






class Menu_Game_Over(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.imGameOver = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "game_over_2.png", self.menus.wF, None, None, False, True)
        self.imGameOver.position = (0, self.menus.hF - self.imGameOver.dimensions[1])
        self.textePerdu = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_perdu.png", None, 0.08*self.menus.hF, None, True, False)
        self.textePerdu.position = ((self.menus.wF-self.textePerdu.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)

        self.sliderScore = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage Score", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_rouge.png", nomForme="forme_rouge.png", rectangleFond=(0.025*self.menus.wF, 0.7*self.menus.hF, 0.95*self.menus.wF, 0.1*self.menus.hF), caracteristiquesTexte=(0.25, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(255,0,0,180), couleurTexte=(0,0,0,128), interactif=False)
        self.sliderNbCoups = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Pourcentage Nb Coups", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_vert.png", nomForme="forme_verte.png", rectangleFond=(0.025*self.menus.wF, 0.85*self.menus.hF, 0.95*self.menus.wF, 0.1*self.menus.hF), caracteristiquesTexte=(0.25, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=100, nbValeurs=21, iValeur=0, couleurFond=(0,255,0,180), couleurTexte=(0,0,0,128), interactif=False)

        self.lImages = [self.imGameOver, self.textePerdu]
        self.lBoutons = [self.boutonHome, self.boutonEcriture]
        self.lSliders = [self.sliderScore, self.sliderNbCoups]
        self.lElements = self.lImages + self.lBoutons + self.lSliders

        self.date = "None"
        self.changer_mode_texte()

    def reset(self):
        with open("liste_anciens_resultats_jeu.txt", 'r') as fichier:
            dicoRes = eval(fichier.readlines()[-1])
        self.date = f"{dicoRes['date'].day} - {dicoRes['date'].month} - {dicoRes['date'].year}"
        self.score, self.nbCoups, self.nbCoupsMax = dicoRes["score"], dicoRes["nbCoups"], dicoRes["nbCoupsMax"]
        nbLignesMax = (4*self.nbCoupsMax)//self.menus.menuJeu.nbColonnes
        scoreMax = nbLignesMax//4 * self.menus.menuJeu.dicoScores[4] + self.menus.menuJeu.dicoScores[nbLignesMax%4]
        self.sliderScore.changer_valeur(round(100* self.score / scoreMax))
        self.sliderNbCoups.changer_valeur(round(100* self.nbCoups / self.nbCoupsMax))
        self.menus.menuBoutique.sliderPieces.changer_valeur(self.menus.menuBoutique.sliderPieces.valeur+self.nbCoups, reel=False)
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.menus.fenetre.blit(self.texteDate, self.positionTexteDate)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()
        for slider in self.lSliders:
            slider.gerer_souris()

    def changer_mode_texte(self):
        self.texteDate = self.menus.generateurTexte.creer_surface_texte(self.date, 0.9*self.menus.wF, 0.1*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteDate = (self.menus.wF/2 - self.texteDate.get_width()/2, 0.625*self.menus.hF - self.texteDate.get_height()/2)
        self.sliderScore.changer_mode_texte()
        self.sliderNbCoups.changer_mode_texte()
            






class Menu_Boutique(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteBoutique = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_you_loose.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteBoutique.position = ((self.menus.wF-self.texteBoutique.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)

        self.sliderPieces = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Nombre Pieces Recoltes", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_jaune.png", nomForme="forme_jaune.png", rectangleFond=(0.01*self.menus.wF, 0.22*self.menus.hF, 0.48*self.menus.wF, 0.1*self.menus.hF), caracteristiquesTexte=(0.35, 0.8, 0.05), enregistrement=False, valeurMin=0, valeurMax=10000, nbValeurs=21, iValeur=15, couleurFond=(255,255,0,180), couleurTexte=(0,0,0,128), interactif=False)
        self.sliderBoostBot = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom="Nombre Coups Boost Bot", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_violet.png", nomForme="forme_violette.png", rectangleFond=(0.51*self.menus.wF, 0.22*self.menus.hF, 0.48*self.menus.wF, 0.1*self.menus.hF), caracteristiquesTexte=(0.35, 0.8, 0.05), enregistrement=False, valeurMin=0, valeurMax=100000, nbValeurs=21, iValeur=0, couleurFond=(255,0,255,180), couleurTexte=(0,0,0,128), interactif=False)
        try:
            with open("ressources.txt", 'r') as fichier:
                nbPieces, nbBoost = eval(fichier.read())
        except:
            nbPieces, nbBoost = 0, 0
        self.sliderPieces.changer_valeur(nbPieces, reel=False)
        self.sliderBoostBot.changer_valeur(nbBoost, reel=False)
        self.lSliders = [self.sliderPieces, self.sliderBoostBot]

        hQcu = 0.15*self.menus.hF
        self.lYQcu = [0.35*self.menus.hF+i*1.1*hQcu for i in range(10)]
        self.qcuBoost = QCU(menus=self.menus, menu=self, nom="Achat de Boost bot", rectangleFond=(0.01*self.menus.wF, self.lYQcu[0], 0.75*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=0, lTypeCarres=(('Texte', (0,0,200), (255,255,0), "100"), ('Texte', (0,0,200), (255,255,0), "200"), ('Texte', (0,0,200), (255,255,0), "500"), ('Texte', (0,0,200), (255,255,0), "1000"), ('Texte', (0,0,200), (255,255,0), "5000"), ('Texte', (0,0,200), (255,255,0), "10000"), ('Texte', (0,0,200), (255,255,0), "50000"), ('Texte', (0,0,200), (255,255,0), "100000")), nbLignes=1, couleurFond=(128,128,128,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=70, interactif=True)
        self.changer_choix_boost()
        wBoutonValiderBoost = 0.9 * (self.menus.wF-(self.positionTexteRetraitBoost[0]+self.texteRetraitBoost.get_width()+0.01*self.menus.wF))
        self.boutonValiderBoost = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "confirmer_2.png", wBoutonValiderBoost, self.qcuBoost.hFond, None, True, False)
        self.boutonValiderBoost.image.position = (self.positionTexteRetraitBoost[0]+self.texteRetraitBoost.get_width()+0.01*self.menus.wF, self.qcuBoost.yFond + (self.qcuBoost.hFond-self.boutonValiderBoost.image.dimensions[1])/2)
        
        self.qcuPieces = QCU(menus=self.menus, menu=self, nom="Achat de Textures", rectangleFond=(0.01*self.menus.wF, self.lYQcu[1], 0.75*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=0, lTypeCarres=(('Texte', (0,0,200), (255,255,0), "R"), ('Texte', (0,0,200), (255,255,0), "J"), ('Texte', (0,0,200), (255,255,0), "L"), ('Texte', (0,0,200), (255,255,0), "Galaxy"), ('Texte', (0,0,200), (255,255,0), "GOAT"), ('Texte', (0,0,200), (255,255,0), "67"), ('Texte', (0,0,200), (255,255,0), "Mandon"), ('Texte', (0,0,200), (255,255,0), "Hugues")), nbLignes=1, couleurFond=(128,128,128,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=70, interactif=True)
        self.changer_choix_pieces()
        wBoutonValiderPieces = 0.9 * (self.menus.wF-(self.positionTexteRetraitPieces[0]+self.texteRetraitPieces.get_width()+0.01*self.menus.wF))
        self.boutonValiderPieces = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "confirmer_2.png", wBoutonValiderPieces, self.qcuPieces.hFond, None, True, False)
        self.boutonValiderPieces.image.position = (self.positionTexteRetraitPieces[0]+self.texteRetraitPieces.get_width()+0.01*self.menus.wF, self.qcuPieces.yFond + (self.qcuPieces.hFond-self.boutonValiderPieces.image.dimensions[1])/2)
        
        self.qcuCouleurs = QCU(menus=self.menus, menu=self, nom="Achat de Couleurs", rectangleFond=(0.01*self.menus.wF, self.lYQcu[2], 0.75*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=0, lTypeCarres=(('Texte', (255,215,0), (0,0,0), "Or"), ('Texte', (192,192,192), (0,0,0), "Argent"), ('Texte', (205,127,50), (0,0,0), "Bronze"), ('Texte', (185,242,255), (0,0,0), "Diamant"), ('Texte', (224,17,95), (0,0,0), "Rubis"), ('Texte', (15,82,186), (0,0,0), "Saphir"), ('Texte', (80,200,120), (0,0,0), "Emeraude"), ('Texte', (153,102,204), (0,0,0), "Amethyste")), nbLignes=1, couleurFond=(128,128,128,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=70, interactif=True)
        self.changer_choix_couleurs()
        wBoutonValiderCouleurs = 0.9 * (self.menus.wF-(self.positionTexteRetraitCouleurs[0]+self.texteRetraitCouleurs.get_width()+0.01*self.menus.wF))
        self.boutonValiderCouleurs = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "confirmer_2.png", wBoutonValiderCouleurs, self.qcuCouleurs.hFond, None, True, False)
        self.boutonValiderCouleurs.image.position = (self.positionTexteRetraitCouleurs[0]+self.texteRetraitCouleurs.get_width()+0.01*self.menus.wF, self.qcuCouleurs.yFond + (self.qcuCouleurs.hFond-self.boutonValiderCouleurs.image.dimensions[1])/2)

        self.qcuTextures = QCU(menus=self.menus, menu=self, nom="Achat de Textures", rectangleFond=(0.01*self.menus.wF, self.lYQcu[3], 0.75*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=0, lTypeCarres=(('Texture', 'mise_en_abyme', (0,0,200), (255,255,0), 4), ('Texture', 'mise_en_abyme', (0,0,200), (255,255,0), 5), ('Texture', 'grille', (0,0,200), (255,255,0), 3, 0.4), ('Texture', 'grille', (0,0,200), (255,255,0), 4, 0.4), ('Texture', 'rayures', (0,0,200), (255,255,0), 4, "horizontal"), ('Texture', 'rayures', (0,0,200), (255,255,0), 5, "horizontal"), ('Texture', 'rayures', (0,0,200), (255,255,0), 4, "vertical"), ('Texture', 'rayures', (0,0,200), (255,255,0), 5, "vertical")), nbLignes=1, couleurFond=(128,128,128,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=70, interactif=True)
        self.changer_choix_textures()
        wBoutonValiderTextures = 0.9 * (self.menus.wF-(self.positionTexteRetraitTextures[0]+self.texteRetraitTextures.get_width()+0.01*self.menus.wF))
        self.boutonValiderTextures = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "confirmer_2.png", wBoutonValiderTextures, self.qcuTextures.hFond, None, True, False)
        self.boutonValiderTextures.image.position = (self.positionTexteRetraitTextures[0]+self.texteRetraitTextures.get_width()+0.01*self.menus.wF, self.qcuTextures.yFond + (self.qcuTextures.hFond-self.boutonValiderTextures.image.dimensions[1])/2)


        self.lQcu = [self.qcuBoost, self.qcuPieces, self.qcuCouleurs, self.qcuTextures]

        self.lImages = [self.texteBoutique]
        self.lBoutons = [self.boutonHome, self.boutonEcriture, self.boutonValiderBoost, self.boutonValiderPieces, self.boutonValiderCouleurs, self.boutonValiderTextures]
        self.lElements = self.lImages + self.lBoutons + self.lQcu + self.lSliders

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.menus.fenetre.blit(self.texteRessources, self.positionTexteRessources)
        self.menus.fenetre.blit(self.texteRetraitBoost, self.positionTexteRetraitBoost)
        self.menus.fenetre.blit(self.texteRetraitPieces, self.positionTexteRetraitPieces)
        self.menus.fenetre.blit(self.texteRetraitCouleurs, self.positionTexteRetraitCouleurs)
        self.menus.fenetre.blit(self.texteRetraitTextures, self.positionTexteRetraitTextures)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()

        if self.boutonValiderBoost.gerer_souris() and self.retraitBoost <= self.sliderPieces.valeur and self.sliderBoostBot.valeur < self.sliderBoostBot.lValeurs[-1]:
            self.sliderPieces.changer_valeur(valeur=self.sliderPieces.valeur-self.retraitBoost)
            self.sliderBoostBot.changer_valeur(valeur=self.sliderBoostBot.valeur+int(self.qcuBoost.lTypeCarres[self.qcuBoost.iCarre][-1]))
            self.enregistrer_changements()
        if self.boutonValiderPieces.gerer_souris() and self.retraitPieces <= self.sliderPieces.valeur:
            self.sliderPieces.changer_valeur(valeur=self.sliderPieces.valeur - self.retraitPieces)
            self.qcuPieces.changement_etat_actif()
            self.enregistrer_changements()
        if self.boutonValiderCouleurs.gerer_souris() and self.retraitCouleurs <= self.sliderPieces.valeur:
            self.sliderPieces.changer_valeur(valeur=self.sliderPieces.valeur - self.retraitCouleurs)
            self.qcuCouleurs.changement_etat_actif()
            self.enregistrer_changements()
        if self.boutonValiderTextures.gerer_souris() and self.retraitTextures <= self.sliderPieces.valeur:
            self.sliderPieces.changer_valeur(valeur=self.sliderPieces.valeur - self.retraitTextures)
            self.qcuTextures.changement_etat_actif()
            self.enregistrer_changements()

        for qcu in self.lQcu:
            if qcu.gerer_souris(lEvents):
                if qcu == self.qcuBoost:
                    self.changer_choix_boost()
                elif qcu == self.qcuPieces:
                    self.changer_choix_pieces()
                elif qcu == self.qcuCouleurs:
                    self.changer_choix_couleurs()
                elif qcu == self.qcuTextures:
                    self.changer_choix_textures()

    def changer_mode_texte(self):
        self.texteRessources = self.menus.generateurTexte.creer_surface_texte(f"Ressources Accumulees", 0.45*self.menus.wF, 0.10*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteRessources = ((self.menus.wF-self.texteRessources.get_width())/2, 0.15*self.menus.hF)
        self.changer_choix_boost()
        self.changer_choix_pieces()
        self.changer_choix_couleurs()
        self.changer_choix_textures()
        for slider in self.lSliders:
            slider.changer_mode_texte()
        for qcu in self.lQcu:
            qcu.changer_mode_texte()

    def changer_choix_boost(self):
        self.retraitBoost = round(int(self.qcuBoost.lTypeCarres[self.qcuBoost.iCarre][-1]) / 10)
        self.texteRetraitBoost = self.menus.generateurTexte.creer_surface_texte(f"- {self.retraitBoost} Pieces", 0.15*self.menus.wF, self.qcuBoost.hFond, 0.05, self.menus.couleurTextes)
        self.positionTexteRetraitBoost = (self.qcuBoost.xFond+self.qcuBoost.wFond+0.01*self.menus.wF, self.qcuBoost.yFond + (self.qcuBoost.hFond-self.texteRetraitBoost.get_height())/2)
    
    def changer_choix_pieces(self):
        dicoRetraits = {"R":1000, "J":1000, "L":1000, "Galaxy":500, "GOAT":750, "67":100000, "Mandon":15000, "Hugues":0}
        piece = self.qcuPieces.lTypeCarres[self.qcuPieces.iCarre][-1]
        if piece in dicoRetraits:
            self.retraitPieces = dicoRetraits[piece]
        else:
            print(f"Retrait Impossible car {piece} pas dans dicoRetraits")
            self.retraitPieces = -1
        self.texteRetraitPieces = self.menus.generateurTexte.creer_surface_texte(f"- {self.retraitPieces} Pieces", 0.15*self.menus.wF, self.qcuPieces.hFond, 0.05, self.menus.couleurTextes)
        self.positionTexteRetraitPieces = (self.qcuPieces.xFond+self.qcuPieces.wFond+0.01*self.menus.wF, self.qcuPieces.yFond + (self.qcuPieces.hFond-self.texteRetraitPieces.get_height())/2)
    
    def changer_choix_couleurs(self):
        self.retraitCouleurs = 1000
        self.texteRetraitCouleurs = self.menus.generateurTexte.creer_surface_texte(f"- {self.retraitCouleurs} Pieces", 0.15*self.menus.wF, self.qcuCouleurs.hFond, 0.05, self.menus.couleurTextes)
        self.positionTexteRetraitCouleurs = (self.qcuCouleurs.xFond+self.qcuCouleurs.wFond+0.01*self.menus.wF, self.qcuCouleurs.yFond + (self.qcuCouleurs.hFond-self.texteRetraitCouleurs.get_height())/2)
    
    def changer_choix_textures(self):
        dicoRetraits = {"mise_en_abyme":5000, "grille":2500, "rayures":1750}
        piece = self.qcuTextures.lTypeCarres[self.qcuTextures.iCarre][1]
        if piece in dicoRetraits:
            self.retraitTextures = dicoRetraits[piece]
        else:
            print(f"Retrait Impossible car {piece} pas dans dicoRetraits")
            self.retraitTextures = -1
        self.texteRetraitTextures = self.menus.generateurTexte.creer_surface_texte(f"- {self.retraitTextures} Pieces", 0.15*self.menus.wF, self.qcuTextures.hFond, 0.05, self.menus.couleurTextes)
        self.positionTexteRetraitTextures = (self.qcuTextures.xFond+self.qcuTextures.wFond+0.01*self.menus.wF, self.qcuTextures.yFond + (self.qcuTextures.hFond-self.texteRetraitTextures.get_height())/2)
    
    def enregistrer_changements(self):
        with open("ressources.txt", 'w') as fichier:
            fichier.write(str([self.sliderPieces.valeur, self.sliderBoostBot.valeur]))
        








class Menu_Personnalisation(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.textePersonnalisation = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_you_loose.png", None, 0.08*self.menus.hF, None, True, False)
        self.textePersonnalisation.position = ((self.menus.wF-self.textePersonnalisation.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)


        hQcu = 0.16*self.menus.hF
        self.lYQcu = [0.12*self.menus.hF+i*1.1*hQcu for i in range(10)]
        self.qcuCouleurFondGrille = QCU(menus=self.menus, menu=self, nom="Couleur Fond Grille", rectangleFond=(0.025*self.menus.wF, self.lYQcu[0], 0.95*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=3, lTypeCarres=(('Couleur', (0,0,0), (255,255,255)), ('Couleur', (80,80,80), (0,0,0)), ('Couleur', (180,180,180), (0,0,0)), ('Couleur', (255,255,255), (0,0,0)), ('Couleur', (255,0,0), (0,0,0)), ('Couleur', (255,255,0), (0,0,0)), ('Couleur', (0,255,0), (0,0,0)), ('Couleur', (0,255,255), (0,0,0)), ('Couleur', (0,0,255), (0,0,0)), ('Couleur', (255,0,255), (0,0,0)),
                                                                                                                                                                                                                                                                                                                            ('Couleur', (255,215,0), (0,0,0)), ('Couleur', (192,192,192), (0,0,0)), ('Couleur', (205,127,50), (0,0,0)), ('Couleur', (185,242,255), (0,0,0)), ('Couleur', (224,17,95), (0,0,0)), ('Couleur', (15,82,186), (0,0,0)), ('Couleur', (80,200,120), (0,0,0)), ('Couleur', (153,102,204), (0,0,0))), nbLignes=2, couleurFond=(100,100,100,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=30, interactif=True)
        for i in range(10, self.qcuCouleurFondGrille.nbCarres):
            self.qcuCouleurFondGrille.changement_etat_actif(iCarre=i)
        
        self.qcuCouleurBorduresGrille = QCU(menus=self.menus, menu=self, nom="Couleur Bordures Grille", rectangleFond=(0.025*self.menus.wF, self.lYQcu[1], 0.95*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=2, lTypeCarres=(('Couleur', (0,0,0), (255,255,255)), ('Couleur', (80,80,80), (0,0,0)), ('Couleur', (180,180,180), (0,0,0)), ('Couleur', (255,255,255), (0,0,0)), ('Couleur', (255,0,0), (0,0,0)), ('Couleur', (255,255,0), (0,0,0)), ('Couleur', (0,255,0), (0,0,0)), ('Couleur', (0,255,255), (0,0,0)), ('Couleur', (0,0,255), (0,0,0)), ('Couleur', (255,0,255), (0,0,0)),
                                                                                                                                                                                                                                                                                                                            ('Couleur', (255,215,0), (0,0,0)), ('Couleur', (192,192,192), (0,0,0)), ('Couleur', (205,127,50), (0,0,0)), ('Couleur', (185,242,255), (0,0,0)), ('Couleur', (224,17,95), (0,0,0)), ('Couleur', (15,82,186), (0,0,0)), ('Couleur', (80,200,120), (0,0,0)), ('Couleur', (153,102,204), (0,0,0))), nbLignes=2, couleurFond=(100,100,100,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=30, interactif=True)
        for i in range(10, self.qcuCouleurBorduresGrille.nbCarres):
            self.qcuCouleurBorduresGrille.changement_etat_actif(iCarre=i)
        
        self.qcuCouleurTextes = QCU(menus=self.menus, menu=self, nom="Couleur Textes", rectangleFond=(0.025*self.menus.wF, self.lYQcu[2], 0.95*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=5, lTypeCarres=(('Couleur', (0,0,0), (255,255,255)), ('Couleur', (80,80,80), (0,0,0)), ('Couleur', (180,180,180), (0,0,0)), ('Couleur', (255,255,255), (0,0,0)), ('Couleur', (255,0,0), (0,0,0)), ('Couleur', (255,255,0), (0,0,0)), ('Couleur', (0,255,0), (0,0,0)), ('Couleur', (0,255,255), (0,0,0)), ('Couleur', (0,0,255), (0,0,0)), ('Couleur', (255,0,255), (0,0,0)),
                                                                                                                                                                                                                                                                                                                            ('Couleur', (255,215,0), (0,0,0)), ('Couleur', (192,192,192), (0,0,0)), ('Couleur', (205,127,50), (0,0,0)), ('Couleur', (185,242,255), (0,0,0)), ('Couleur', (224,17,95), (0,0,0)), ('Couleur', (15,82,186), (0,0,0)), ('Couleur', (80,200,120), (0,0,0)), ('Couleur', (153,102,204), (0,0,0))), nbLignes=2, couleurFond=(100,100,100,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=30, interactif=True)
        for i in range(10, self.qcuCouleurBorduresGrille.nbCarres):
            self.qcuCouleurTextes.changement_etat_actif(iCarre=i)
        
        self.qcuTexturesCases = QCU(menus=self.menus, menu=self, nom="Textures cases", rectangleFond=(0.025*self.menus.wF, self.lYQcu[3], 0.95*self.menus.wF, hQcu), caracteristiquesTexte=(0.3, 0.8, 0.05), caracteristiquesEspacements=(0.005, 0.01, 0.005), caracteristiquesCarres=(0.8, 0.01), iCarre=17, lTypeCarres=(('Texture', 'mise_en_abyme', (0,0,0), (255,255,255), 1), ('Texture', 'mise_en_abyme', (0,0,0), (255,255,255), 2), ('Texture', 'mise_en_abyme', (0,0,0), (255,255,255), 3), ('Texture', 'mise_en_abyme', (0,0,0), (255,255,255), 4), ('Texture', 'mise_en_abyme', (0,0,0), (255,255,255), 5), ('Texture', 'grille', (0,0,0), (255,255,255), 2, 0.2), ('Texture', 'grille', (0,0,0), (255,255,255), 2, 0.4), ('Texture', 'grille', (0,0,0), (255,255,255), 3, 0.4), ('Texture', 'grille', (0,0,0), (255,255,255), 4, 0.4), ('Texture', 'rayures', (0,0,0), (255,255,255), 2, "horizontal"), 
                                                                                                                                                                                                                                                                                                                         ('Texture', 'rayures', (0,0,0), (255,255,255), 3, "horizontal"), ('Texture', 'rayures', (0,0,0), (255,255,255), 4, 'horizontal'), ('Texture', 'rayures', (0,0,0), (255,255,255), 5, 'horizontal'), ('Texture', 'rayures', (0,0,0), (255,255,255), 2, "vertical"), ('Texture', 'rayures', (0,0,0), (255,255,255), 3, "vertical"), ('Texture', 'rayures', (0,0,0), (255,255,255), 4, 'vertical'), ('Texture', 'rayures', (0,0,0), (255,255,255), 5, 'vertical'), ('Texte', (150,0,0), (100,150,255), "Normal")), nbLignes=2, couleurFond=(100,100,100,128), couleurTexte=(0,0,0,128), couleurCarreChoix=(200,200,200), alphaInactif=30, interactif=True)
        for i in [3,4, 7,8, 11,12, 15,16]:
            self.qcuTexturesCases.changement_etat_actif(iCarre=i)

        self.sliderBordures = Slider(menus=self.menus, menu=self, dossier1=self.menus.dossier, dossier2=f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", dossier3=self.menus.dossierOutput, nom=f"Proportion Bordures Grille", nomCadre="cadre_barre_11.png", nomCarreNoir="carre_noir.png", nomCarreColore="carre_rouge.png", nomForme="forme_rouge.png", rectangleFond=(0.025*self.menus.wF, self.lYQcu[4], 0.95*self.menus.wF, hQcu), caracteristiquesTexte=(0.25, 0.6, 0.05), enregistrement=False, valeurMin=0, valeurMax=0.5, nbValeurs=21, iValeur=1, couleurFond=(100,100,100,128), couleurTexte=(0,0,0,128), interactif=True)

        self.lQcu = [self.qcuCouleurFondGrille, self.qcuCouleurBorduresGrille, self.qcuTexturesCases, self.qcuCouleurTextes]
        self.lSliders = [self.sliderBordures]

        self.lImages = [self.textePersonnalisation]
        self.lBoutons = [self.boutonHome, self.boutonEcriture]
        self.lElements = self.lImages + self.lBoutons + self.lQcu + self.lSliders

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.couleurTextes = self.qcuCouleurTextes.lCarres[self.qcuCouleurTextes.iCarre].get_at((0,0))[:3]
            self.menus.menuHome.reset()
            self.menus.menuJeu.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()

        for qcu in self.lQcu:
            qcu.gerer_souris(lEvents)
        for slider in self.lSliders:
            slider.gerer_souris()

    def changer_mode_texte(self):
        for qcu in self.lQcu:
            qcu.changer_mode_texte()
        for slider in self.lSliders:
            slider.changer_mode_texte()









class Menu_didactique(object):
    def __init__(self, menus, lNomsConstantes, nbParties, avecTorch):
        self.menus = menus

        self.actif = False

        self.lNomsConstantes = lNomsConstantes
        self.nbConstantes = len(self.lNomsConstantes)

        #charger toutes les images
        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texteApprentissage = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_apprentissage.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteApprentissage.position = ((self.menus.wF-self.texteApprentissage.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)
        self.boutonReset = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "changer.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[1][0], True, False)
        self.boutonPrediction = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_prediction.png", 0.4*self.menus.wF, None, None, True, False)
        self.boutonPrediction.image.position = (0.55*self.menus.wF, 0.1*self.menus.hF)

        self.lImages = [self.texteApprentissage]
        self.lBoutons = [self.boutonHome, self.boutonEcriture, self.boutonReset, self.boutonPrediction]

        aFondSliders = 180
        cMinFondSliders, cMaxFondSliders = 70, 200
        wTexteSliders, hTexteSliders, espacementTexteSliders = 0.45, 0.6, 0.05
        lCouleursSliders = [("rouge", "rouge", (cMaxFondSliders,0,0,aFondSliders), (cMinFondSliders,0,0)), ("vert", "verte", (0,cMaxFondSliders,0,aFondSliders), (0,cMinFondSliders,0)), ("bleu", "bleue", (0,0,cMaxFondSliders,aFondSliders), (0,0,cMinFondSliders)), ("jaune", "jaune", (cMaxFondSliders,cMaxFondSliders,0,aFondSliders), (cMinFondSliders,cMinFondSliders,0)), ("violet", "violette", (cMaxFondSliders,0,cMaxFondSliders,aFondSliders), (cMinFondSliders,0,cMinFondSliders)), ("orange", "orange", (cMaxFondSliders,(cMinFondSliders*0.7+0.3*cMaxFondSliders),0,aFondSliders), (cMinFondSliders,cMinFondSliders//2,0)), ("cyan", "cyan", (0,cMaxFondSliders,cMaxFondSliders,aFondSliders), (0,cMinFondSliders,cMinFondSliders))]
        lCarSliders = [(nom, "cadre_barre_11.png", "carre_noir.png", f"carre_{couleur1}.png", f"forme_{couleur2}.png", rgbaFond, rgbTexte) for nom, (couleur1, couleur2, rgbaFond, rgbTexte) in zip(lNomsConstantes, lCouleursSliders)]
        yMinSliders = 0.1*self.menus.hF#self.boutonPrediction.image.dimensions[1]*1.15
        hSlider = (self.menus.hF - yMinSliders) / len(lNomsConstantes)
        assert len(lNomsConstantes) <= len(lCouleursSliders), "Plus de constantes que de couleurs disponibles"
        self.lSliders = []
        for iS, (nom,nomCadre,nomCarreNoir,nomCarreColore,nomForme,couleurFond,couleurTexte) in enumerate(lCarSliders):
            self.lSliders.append(Slider(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", self.menus.dossierOutput, nom, nomCadre, nomCarreNoir, nomCarreColore, nomForme, (0.03*self.menus.wF, yMinSliders+iS*hSlider, 0.5*self.menus.wF, 0.9*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, -1, 1, 13, None, couleurFond, couleurTexte, True))
        self.sliderProgressionEvaluation = Slider(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ELEMENTS_SLIDERS", self.menus.dossierOutput, "Progression Evaluation", "cadre_barre_11.png", "carre_rouge.png", "carre_vert.png", "forme_jaune.png", (0.55*self.menus.wF, 0.25*self.menus.hF, 0.43*self.menus.wF, 0.5*hSlider), (wTexteSliders, hTexteSliders, espacementTexteSliders), True, 0, 100, 20, 0, (cMaxFondSliders/2, cMaxFondSliders/2, cMaxFondSliders/2, aFondSliders), (0,0,0,128), False)
        self.lSliders.append(self.sliderProgressionEvaluation)

        self.lElements = self.lImages + self.lBoutons + self.lSliders


        self.avecTorch = avecTorch
        if self.avecTorch:
            global torch
            import torch
        self.lNbNoeuds = [self.nbConstantes, 1]
        if self.menus.menuJeu.algorithme:
            self.modele = self.menus.menuJeu.algo.creer_reseau(self.lNbNoeuds)
        self.nbParties = nbParties
        self.scoreMoyen, self.nbCoupsMoyen = 0,0
        self.changer_resultats()

    def reset(self):
        self.changer_mode_texte()
        self.changer_resultats()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)
        self.menus.fenetre.blit(self.texteSM, self.positionTexteSM)
        self.menus.fenetre.blit(self.texteScoreMoyen, self.positionTexteScoreMoyen)
        self.menus.fenetre.blit(self.texteNbCM, self.positionTexteNbCM)
        self.menus.fenetre.blit(self.texteNbCoupsMoyen, self.positionTexteNbCoupsMoyen)

    def evaluation(self):
        if not self.avecTorch:
            print("Pas possible sans activer Torch")
            return
        lValeurs = [slider.valeur for slider in self.lSliders[:self.nbConstantes]]
        dicoReseau = {'0.weight' : torch.tensor(lValeurs, dtype=torch.float32).unsqueeze(0), '0.bias' : torch.zeros(1, dtype=torch.float32)}
        self.modele.load_state_dict(dicoReseau)
        self.scoreMoyen, self.nbCoupsMoyen = self.menus.menuJeu.algo.evaluation_algo(self.nbParties, self.modele, affichage=True, visuel=False, fonctionAvancement=self.lSliders[self.nbConstantes].changer_valeur)
        self.changer_resultats()

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()
        if self.boutonReset.gerer_souris():
            for slider in self.lSliders[:-1]:
                slider.iValeur = slider.nbValeurs // 2
                slider.maj_valeur()
        if self.boutonPrediction.gerer_souris():
            self.evaluation()
        for slider in self.lSliders:
            slider.gerer_souris()

    def changer_mode_texte(self):
        for slider in self.lSliders:
            slider.changer_mode_texte()
        self.changer_resultats()

    def changer_resultats(self):
        wMilieu = self.menus.wF * (1+0.5)/2
        self.texteSM = self.menus.generateurTexte.creer_surface_texte(f"Score Moyen", 0.45*self.menus.wF, 0.10*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteSM = (wMilieu-self.texteSM.get_width()/2, 0.35*self.menus.hF)
        self.texteScoreMoyen = self.menus.generateurTexte.creer_surface_texte(f"{self.scoreMoyen:.2f}", 0.4*self.menus.wF, 0.15*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteScoreMoyen = (wMilieu-self.texteScoreMoyen.get_width()/2, 0.45*self.menus.hF)
        self.texteNbCM = self.menus.generateurTexte.creer_surface_texte(f"Nb Coups Moyen", 0.4*self.menus.wF, 0.15*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteNbCM = (wMilieu-self.texteNbCM.get_width()/2, 0.65*self.menus.hF)
        self.texteNbCoupsMoyen = self.menus.generateurTexte.creer_surface_texte(f"{self.nbCoupsMoyen:.2f}", 0.4*self.menus.wF, 0.15*self.menus.hF, 0.05, self.menus.couleurTextes)
        self.positionTexteNbCoupsMoyen = (wMilieu-self.texteNbCoupsMoyen.get_width()/2, 0.75*self.menus.hF)







class Menu_Jeu(object):
    def __init__(self, menus, lAttributsPolice, horloge, nbColonnes, nbLignes, visuel, nbFramesAffichage, lNbNoeuds, algorithme, entrainementGreedy, entrainementGenetique, entrainementNES, entrainementDRL, gameInfini, charger_reseau):
        self.menus = menus
        self.horloge = horloge
        self.actif = False
        self.quitterProgramme = False
        self.finJeu = False
        self.visuel = visuel
        self.score = 0
        self.texteScore = None
        self.dicoScores = {0 : 0,
                           1 : 40,
                           2 : 100,
                           3 : 300,
                           4 : 1200}
        self.nbCoups = 0
        self.nbCoupsMax = None
        self.changer_game_nb_coups_max(gameInfini)
        self.texteNbCoups = None
        self.nbBlocs = 0
        self.sommeNbBlocs = 0
        self.calcul_sommeNbBlocs = False
        self.texteSommeNbBlocs = None
        #Graphiques
        self.lAttributsPolice = lAttributsPolice
        nomPolice, taillePolice, grasPolice, italiquePolice = self.lAttributsPolice
        self.police = pygame.font.SysFont(nomPolice, taillePolice, bold=grasPolice, italic=italiquePolice)
        self.nbFramesAffichage = nbFramesAffichage
        self.iFrameAffichage = 0
        self.wF, self.hF = pygame.display.get_surface().get_size()
        #Grille
        self.nbColonnes, self.nbLignes = nbColonnes, nbLignes
        self.lDicoModesGrille = [{"nbGrilles" : 1, "tailleCases" : self.hF*0.9 / (self.nbLignes+self.nbColonnes+2), "listeLOrientations" : [[0]]},
                                 {"nbGrilles" : 3, "tailleCases" : self.hF / (3*self.nbLignes), "listeLOrientations" : [[0,1,2], [3,0,1], [2,3,0]]},
                                 {"nbGrilles" : 4, "tailleCases" : self.hF / (3*self.nbLignes), "listeLOrientations" : [[0,1,2,3], [3,0,1,2], [2,3,0,1], [1,2,3,0]]}]
        self.lDicoModesGrille[0]["lXYDebut"] = [(self.wF/2 - nbColonnes/2 * self.lDicoModesGrille[0]["tailleCases"], self.hF/2 - (nbLignes-self.nbColonnes)/2 * self.lDicoModesGrille[0]["tailleCases"])]
        ecart = self.lDicoModesGrille[1]["tailleCases"]*self.nbColonnes/2
        self.lDXY = [(0,1), (1,0), (0,-1), (-1,0)]
        lDXYEcart = [(ecart*dx, ecart*dy) for dx,dy in [(-1,1), (1, 1), (1, -1), (-1, -1)]]
        self.lDicoModesGrille[1]["lXYDebut"] = [(self.wF/2 + dx, self.hF/2 + dy) for dx,dy in lDXYEcart]
        self.lDicoModesGrille[2]["lXYDebut"] = self.lDicoModesGrille[1]["lXYDebut"].copy()
        self.modeGrille = 0 #0-2
        self.grille = [[None]*self.nbColonnes for _ in range(self.nbLignes)]
        self.tailleMaxPieces = 5
        self.grilleNext = [[None]*self.tailleMaxPieces for _ in range(self.tailleMaxPieces)]
        self.grilleHold = [[None]*self.tailleMaxPieces for _ in range(self.tailleMaxPieces)]
        #self.limiter_grille()
        #Pieces
        self.deltaTempsFin, self.deltaTempsMilieu = 1000, 3
        with open("dicoMatricesPiecesJolies.txt", "r") as fichier:
            dicoMatricesPiecesJolies = eval(fichier.read())
        self.charger_matrices(dicoMatricesPiecesJolies)
        self.dicoCouleursPieces = {#type : couleur
                           "I" : (159, 209, 241),
                           "T" : (203, 167, 206),
                           "O" : (255, 230, 49),
                           "L" : (242, 164, 44),
                           "J" : (30, 122, 191),
                           "S" : (0, 171, 77),
                           "Z" : (216, 58, 44)}
        self.lTypePieces = ["I", "T", "O", "L", "J", "S", "Z"]
        self.lProchainesPieces = []
        self.holdPiece = None
        self.piece = None
        self.nextPiece = None
        self.holdUtilise = False
        self.lNbNoeuds = lNbNoeuds if lNbNoeuds is not None else [7, 1]#list(map(int, input("lNbNoeuds (ex : '7 8 1') : ").split())) if algorithme else None
        #algo
        self.algorithme = algorithme
        if self.algorithme :
            from TETRIS_Algorithme_NN import Algorithme
            self.algo = Algorithme(jeu=self, lNbNoeuds=self.lNbNoeuds) #toujours vrai lui
            self.modeAlgo = False
            self.texteNbCoupsAlgo = None
        self.reset()
        self.entrainementGreedy = entrainementGreedy
        if self.entrainementGreedy and self.algorithme:
            self.entrainement_greedy()
        self.entrainementGenetique = entrainementGenetique
        if not self.entrainementGenetique and charger_reseau:
            try :
                with open("lDicoReseau_GA_NN.txt") as fichier:
                    lDicoReseau = eval(fichier.read())
                iMax = max(i if dicoReseau is not None else -1 for i, dicoReseau in enumerate(lDicoReseau))
                if iMax > -1 :
                    self.algo.charger_dico_reseau_sans_tensor(lDicoReseau[iMax])
                else :
                    print("Pas de Dico Reseau disponible !")
            except:
                print("Pas du lDicoReseau_GA_NN.txt disponible ...")
        if self.entrainementGenetique and self.algorithme:
            from TETRIS_Algorithm_Genetique_NN import Algorithme_Genetique
            self.algoGenetique = Algorithme_Genetique(jeu=self, algo=self.algo, lNbNoeuds=self.lNbNoeuds, tauxSurvivant=0.1, tauxRandom=0, nbLignes=self.nbLignes, nbColonnes=self.nbColonnes, modeCoups=3) if self.entrainementGenetique else None
            self.algoGenetique.entrainement()
        self.entrainementNES = entrainementNES
        if self.entrainementNES and self.algorithme and False:
            from TETRIS_NES_v1 import Neural_Evolution_Strategies
            self.nes = Neural_Evolution_Strategies(self, self.algo, self.lNbNoeuds[0]) if self.entrainementNES else None
            self.nes.entrainement(10, 30)
        self.entrainementDRL = entrainementDRL
        if self.entrainementDRL and self.algorithme and False:
            from TETRIS_DRL_v3 import Policy_Gradient
            self.pg = Policy_Gradient(self, self.algo, 1000, 30, self.nbCoupsMax, 1, self.lNbNoeuds[0], self.nbLignes, self.nbColonnes) if self.entrainementDRL else None
            self.pg.entrainement()

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.hF, (0, 0), False, True)
        self.texteJeu = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "texte_jeu.png", None, 0.08*self.menus.hF, None, True, False)
        self.texteJeu.position = ((self.menus.wF-self.texteJeu.dimensions[0])/2, 0.01*self.menus.hF)

        self.lImages = [self.texteJeu]
        self.lBoutons = []
        self.lElements = self.lImages + self.lBoutons

        self.seuilImagesLogo = 100
        self.changer_images_logo()

        self.lTextes = (self.texteScore, self.texteNbCoups, self.texteSommeNbBlocs)
        if self.algorithme:
            self.lTextes += (self.texteNbCoupsAlgo,)


    def reset(self, modeAlgo=False):
        self.finJeu = False
        self.iFrameAffichage = 0
        self.score = 0
        self.texteScore = None
        self.nbCoups = 0
        self.nbBlocs = 0
        self.sommeNbBlocs = 0
        self.bordure = round(self.menus.menuPersonnalisation.sliderBordures.valeur,3)
        self.couleurFondGrille = self.menus.menuPersonnalisation.qcuCouleurFondGrille.lCarres[self.menus.menuPersonnalisation.qcuCouleurFondGrille.iCarre].get_at((0,0))[:3]
        self.couleurBorduresGrille = self.menus.menuPersonnalisation.qcuCouleurBorduresGrille.lCarres[self.menus.menuPersonnalisation.qcuCouleurBorduresGrille.iCarre].get_at((0,0))[:3]
        tailleCases = round(self.lDicoModesGrille[self.modeGrille]["tailleCases"] * (1-2*self.bordure))
        self.case = pygame.transform.scale(self.menus.menuPersonnalisation.qcuTexturesCases.lCarres[self.menus.menuPersonnalisation.qcuTexturesCases.iCarre], (tailleCases, tailleCases)) if self.menus.menuPersonnalisation.qcuTexturesCases.lTypeCarres[self.menus.menuPersonnalisation.qcuTexturesCases.iCarre][0] == 'Texture' else None
        #algo
        if self.algorithme:
            self.modeAlgo = modeAlgo
            self.algo.reset()
            self.nbCoupsAlgoRestants = int(self.menus.menuBoutique.sliderBoostBot.valeur)
        #Grille
        assert not (modeAlgo and self.modeGrille != 0), f"Pas possible de lancer mode grille {self.modeGrille} avec algo activé..."
        self.lGrilles = [[[None]*self.nbColonnes for _ in range(self.nbLignes)] for __ in range(self.lDicoModesGrille[self.modeGrille]["nbGrilles"])]
        self.iGrille = 0
        self.grille = self.lGrilles[self.iGrille]
        self.grilleNext = [[None]*self.tailleMaxPieces for _ in range(self.tailleMaxPieces)]
        self.grilleHold = [[None]*self.tailleMaxPieces for _ in range(self.tailleMaxPieces)]
        self.changer_grille(delta=0)
        #self.limiter_grille()
        #Pieces
        self.deltaTemps = self.deltaTempsFin
        self.nbLignesSupprimees = 0
        self.lProchainesPieces = []
        self.holdPiece = None
        self.piece = None
        self.nextPiece = None
        self.holdUtilise = False
        self.generer_piece()
        self.changer_score(gain=0)
        self.changer_nb_coups(deltaCoups=0)
        self.calculer_sommeNbBlocs(ajout=0)
        if self.algorithme:
            self.algo.changer_nb_coups(ajout=0)
        self.changer_images_logo()

    def tester_jeu(self, nbParties):
        print("Fonction plus disponible...")
        return
        for partie in range(1,nbParties+1):
            self.jouer(modeAlgo=False)
            print(f"Partie {partie} : Score {self.score} || Nb Coups : {self.nbCoups}")
            if self.quitterProgramme :
                break
            if self.menus:
                self.menus.menuGameOver.actif = True
                self.menus.boucle()    

    def gerer_souris(self, lEvents):
        if self.finJeu:
            self.actif = False
            self.menus.menuGameOver.actif = True
            with open("liste_anciens_resultats_jeu.txt","a") as fichier:
                fichier.write(str({"score":round(self.score), "nbCoups":int(self.nbCoups), "nbCoupsMax":int(self.nbCoupsMax), "date":datetime.datetime.now()}))
                fichier.write('\n')
            self.menus.menuGameOver.reset()
        if self.algorithme and self.modeAlgo and self.nbCoupsAlgoRestants > 0:
            for i in range(self.nbFramesAffichage):
                self.algo.appliquer_position()
            self.nbCoupsAlgoRestants = max(0, self.nbCoupsAlgoRestants-self.nbFramesAffichage)
        else :
            self.piece.bouger(self.grille)
            self.tester_clavier()
        for event in lEvents :
            if event.type == pygame.KEYDOWN:
                self.tester_clavier_appuie(event)

    def afficher(self):
        if not self.visuel:
            return

        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)

        if self.algorithme:
            self.algo.afficher_toutes_positions()
        tailleCases = self.lDicoModesGrille[self.modeGrille]["tailleCases"]
        xDebut0, yDebut0 = self.lDicoModesGrille[self.modeGrille]["lXYDebut"][0]
        for iG, (grille, orientation) in enumerate(zip(self.lGrilles, self.lDicoModesGrille[self.modeGrille]["listeLOrientations"][self.iGrille])):
            piece = self.piece if iG == self.iGrille else None
            xDebut, yDebut = self.lDicoModesGrille[self.modeGrille]["lXYDebut"][orientation]
            self.afficher_grille(grille, tailleCases, xDebut, yDebut, orientation=orientation, piece=piece, ombre=False, coin=False)
        self.afficher_grille(self.grilleNext, tailleCases, xDebut0+tailleCases*(self.nbColonnes+1), yDebut0+tailleCases*1, orientation=0, piece=self.nextPiece, ombre=False, coin=True)
        self.afficher_grille(self.grilleHold, tailleCases, xDebut0-tailleCases*(self.tailleMaxPieces+1), yDebut0+tailleCases*1, orientation=0, piece=self.holdPiece, ombre=False, coin=True)
        imageLogo = self.lImagesLogo[min(self.score//self.seuilImagesLogo, len(self.lImagesLogo)-1)]
        imageLogo.afficher(fenetre=self.menus.fenetre, position=(xDebut0+self.nbColonnes/2*tailleCases-imageLogo.dimensions[0]/2, yDebut0-self.nbColonnes/2*tailleCases-imageLogo.dimensions[1]/2))
        if self.algorithme:
            self.algo.desafficher_toutes_positions()

        xTexte = 10
        yTexte = 5
        for texte in (self.texteScore, self.texteNbCoups, self.texteSommeNbBlocs):
            if texte == self.texteSommeNbBlocs and not self.calcul_sommeNbBlocs:
                continue
            self.menus.fenetre.blit(texte, (xTexte, yTexte))
            w,h = texte.get_size()
            xTexte += (w + 30)

        pygame.display.update()

    def afficher_grille(self, grille, tailleCases, xDebut, yDebut, orientation, piece, ombre=False, coin=False):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        if piece is not None:
            if ombre :
                self.mettre_dans_grille(grille, piece.x, piece.yOmbre, piece.orientation, piece.type, (220,200,200), coin)
            self.mettre_dans_grille(grille, piece.x, piece.y, piece.orientation, piece.type, piece.couleur, coin)
        vx = self.lDXY[(orientation+1)%4]
        vy = self.lDXY[orientation]
        xFin = xDebut + tailleCases*(nbColonnes*vx[0] + nbLignes*vy[0])
        yFin = yDebut + tailleCases*(nbColonnes*vx[1] + nbLignes*vy[1])
        #print(orientation, vx, vy, int(xDebut), int(xFin), int(yDebut), int(yFin), (int(min(xDebut, xFin)), int(min(yDebut, yFin)), int(abs(xFin-xDebut)), int(abs(yFin-yDebut))))
        pygame.draw.rect(self.menus.fenetre, (self.couleurBorduresGrille if self.bordure > 0 else self.couleurFondGrille), (min(xDebut, xFin), min(yDebut, yFin), abs(xFin-xDebut), abs(yFin-yDebut)))
        if self.case is None or (abs(tailleCases*(1-2*self.bordure)-self.case.get_width()) < 1 and abs(tailleCases*(1-2*self.bordure)-self.case.get_height()) < 1):
            case = self.case
        else :
            case = pygame.transform.scale(self.case, (tailleCases*(1-2*self.bordure), tailleCases*(1-2*self.bordure)))
        for y in range(nbLignes):
            for x in range(nbColonnes):
                if grille[y][x] is not None and not isinstance(grille[y][x], bool):
                    r,g,b = grille[y][x]
                elif isinstance(grille[y][x], bool):
                    r,g,b = (255,0,0) if grille[y][x] else self.couleurFondGrille
                else :
                    r,g,b = self.couleurFondGrille
                v1 = vx[0] + vy[0]
                v2 = vx[1] + vy[1]
                x0 = xDebut + tailleCases*(x*vx[0] + y*vy[0] + self.bordure*v1)
                y0 = yDebut + tailleCases*(x*vx[1] + y*vy[1] + self.bordure*v2)
                x1 = x0 + tailleCases*(vx[0] + vy[0] - 2*self.bordure*v1)
                y1 = y0 + tailleCases*(vx[1] + vy[1] - 2*self.bordure*v2)
                if (r,g,b) == self.couleurFondGrille or self.case is None:
                    pygame.draw.rect(self.menus.fenetre, (r,g,b,255), (min(x0, x1), min(y0, y1), abs(x1-x0), abs(y1-y0)))
                else :
                    self.menus.fenetre.blit(case, (min(x0, x1), min(y0, y1)))
        if piece is not None:
            if ombre :
                self.enlever_de_grille(grille, piece.x, piece.yOmbre, piece.orientation, piece.type, (220,200,200), coin)
            self.enlever_de_grille(grille, piece.x, piece.y, piece.orientation, piece.type, piece.couleur, coin)

    def changer_grille(self, delta):
        self.iGrille = (self.iGrille+delta)%self.lDicoModesGrille[self.modeGrille]["nbGrilles"]
        self.grille = self.lGrilles[self.iGrille]

    def changer_score(self, gain):
        self.score += gain
        self.texteScore = self.police.render(f"Score : {self.score}", False, self.menus.couleurTextes)

    def changer_nb_coups(self, deltaCoups):
        self.nbCoups += deltaCoups
        self.texteNbCoups = self.police.render(f"Nb Coups : {self.nbCoups}", False, self.menus.couleurTextes)
        print(self.nbCoups, self.nbCoupsMax)
        if self.nbCoups >= self.nbCoupsMax :
            self.finJeu = True

    def changer_game_nb_coups_max(self, gameInfini):
        self.nbCoupsMax = 1e9 if gameInfini else int(input("nbCoupsMax : "))

    def changer_somme_nb_blocs(self, actif):
        self.calcul_sommeNbBlocs = actif

    def calculer_sommeNbBlocs(self, ajout):
        if not self.calcul_sommeNbBlocs:
            return
        self.nbBlocs += ajout
        self.sommeNbBlocs += self.nbBlocs
        self.texteSommeNbBlocs = self.police.render(f"Somme Nb Blocs : {self.sommeNbBlocs}", False, self.menus.couleurTextes)

    def limiter_grille(self):
        for x in range(self.nbColonnes):
            self.grille[self.nbLignes-1][x] = (100,100,100)
        for y in range(self.nbLignes):
            self.grille[y][0] = (100,100,100)
            self.grille[y][self.nbColonnes-1] = (100,100,100)

    def generer_piece(self):
        if len(self.lProchainesPieces) < 3:
            bag7 = self.lTypePieces.copy()
            rd.shuffle(bag7)
            self.lProchainesPieces.extend(bag7)
        if not self.nextPiece:
            self.nextPiece = Tetromino(self, self.lProchainesPieces[-1])
            self.lProchainesPieces.pop()
        self.piece = self.nextPiece
        if self.piece.reset(self.grille):
            self.finJeu = True
        self.piece.predire_ombre(self.grille)
        self.nextPiece = Tetromino(self, self.lProchainesPieces[-1])
        self.lProchainesPieces.pop()
        self.holdUtilise = False

    def mettre_piece_hold(self):
        if self.holdUtilise:
            return
        self.holdUtilise = True
        if self.holdPiece is None:
            self.holdPiece = self.piece
            self.generer_piece()
        else :
            self.holdPiece, self.piece = self.piece, self.holdPiece
            if self.piece.reset(self.grille):
                self.finJeu = True
        self.piece.predire_ombre(self.grille)

    def tester_clavier(self):
        lTouchesAppuyees = pygame.key.get_pressed()
        if lTouchesAppuyees[pygame.K_DOWN]:
            self.piece.deltaTemps = self.deltaTemps // 4
        elif self.piece.deltaTemps > 0 :
            self.piece.deltaTemps = self.deltaTemps

    def tester_clavier_appuie(self, event, reel=True):
        if event.key == pygame.K_SPACE:
            self.piece.deltaTemps = 0
            if reel and self.menus.audio and self.menus.son and not self.modeAlgo:
                self.menus.sonCollision.play()
        if event.key == pygame.K_UP:
            self.piece.tourner(self.grille, changement=1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.tourner(self.grille, changement=-1)
            elif reel and self.menus.audio and self.menus.son and not self.modeAlgo:
                self.menus.sonSwap.play()
        elif event.key == pygame.K_LEFT:
            self.piece.deplacer(self.grille, dx=-1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.deplacer(self.grille, dx=1)
            elif reel and self.menus.audio and self.menus.son and not self.modeAlgo:
                self.menus.sonMouvement.play()
        elif event.key == pygame.K_RIGHT:
            self.piece.deplacer(self.grille, dx=1)
            if self.tester_chevauchement(self.grille, self.piece.x, self.piece.y, self.piece.orientation, self.piece.type):
                self.piece.deplacer(self.grille, dx=-1)
            elif reel and self.menus.audio and self.menus.son and not self.modeAlgo:
                self.menus.sonMouvement.play()
        elif event.key == pygame.K_h:
            self.mettre_piece_hold()
        elif event.key == pygame.K_p and self.algorithme: #positions
            self.algo.calculer_toutes_positions()
        elif event.key == pygame.K_a and self.algorithme and self.nbCoupsAlgoRestants > 0: #appliquer position algo
            self.algo.appliquer_position()
            self.nbCoupsAlgoRestants -= 1
        elif event.key == pygame.K_b and self.algorithme: #bot algo
            self.algo.changer_mode()
        elif event.key == pygame.K_c and self.algorithme: #nbCoups algo
            self.algo.changer_nb_coups(ajout=1)

    def tester_lignes(self, grille, reel=False, fScore=None):
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        """dp = [0]*(nbLignes+1) #nbLignes à supprimer <= y
        for y in range(nbLignes-1, -1, -1):
            dp[y] = dp[y+1]
            if all(grille[y][x] is not None for x in range(nbColonnes)):
                dp[y] += 1
        nbLignesASupprimer = dp[0]
        if nbLignesASupprimer > 0:
            for y in range(nbLignes-1, -1, -1):
                if dp[y] == 0 :
                    continue
                elif y-dp[y] >= 0:
                    grille[y] = grille[y-dp[y]].copy()
                else :
                    grille[y] = [None]*nbColonnes"""
        grilleLignesPasCompletes = [ligne for ligne in grille if any(case is None for case in ligne)]
        nbLignesASupprimer = nbLignes-len(grilleLignesPasCompletes)
        if nbLignesASupprimer == 0:
            return grille
        grille2 = [[None]*nbColonnes for _ in range(nbLignesASupprimer)] + grilleLignesPasCompletes
        if reel :
            self.changer_score(gain=self.dicoScores[nbLignesASupprimer])
            self.calculer_sommeNbBlocs(ajout=-nbColonnes*nbLignesASupprimer)
            if self.menus.audio and self.menus.son and not self.modeAlgo:
                self.menus.sonCroc.play()
            self.nbLignesSupprimees += nbLignesASupprimer
        elif fScore is not None:
            fScore(gain=self.dicoScores[nbLignesASupprimer])
        return grille2

    def supprimer_ligne(self, grille, Y):
        for y in range(Y, 0, -1):
            grille[y] = grille[y-1].copy()
        for x in range(self.nbColonnes):
            grille[0][x] = None

    def tester_chevauchement(self, grille, X, Y, O, T, M=None):
        matrice = self.dicoMatricesPieces[(T, O)] if M is None else M
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if not(0 <= X+dx < nbColonnes) or not(0 <= Y+dy < nbLignes) or (grille[Y+dy][X+dx] is not None):
                return True
        return False

    def mettre_dans_grille(self, grille, X, Y, O, T, C, coin, reel=True):
        matrice = self.dicoMatricesPieces[(T, O)]
        C = C if reel else False
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if coin and (dx < nbColonnes) and (dy < nbLignes):
                grille[dy][dx] = C
            elif (0 <= X+dx < nbColonnes) and (0 <= Y+dy < nbLignes):
                grille[Y+dy][X+dx] = C

    def enlever_de_grille(self, grille, X, Y, O, T, C, coin):
        matrice = self.dicoMatricesPieces[(T, O)]
        nbLignes = len(grille)
        nbColonnes = len(grille[0])
        for dx, dy in matrice:
            if coin and (dx < nbColonnes) and (dy < nbLignes):
                grille[dy][dx] = None
            elif (0 <= X+dx < nbColonnes) and (0 <= Y+dy < nbLignes):
                grille[Y+dy][X+dx] = None

    def entrainement_greedy(self):
        self.visuel = False
        self.changer_game_nb_coups_max(False)
        self.changer_somme_nb_blocs(False)
        nbParties = 10
        lConstantes = [0] * self.algo.nbConstantes
        #lConstantes = [0, 0, 0, 0.5, 0.5, 0.5]
        pasConstantes = 1
        nbCombinaisons = floor(1/pasConstantes + 1)**len(lConstantes)
        iCombinaison = 0
        dicoRes = {}
        while lConstantes[0] <= 1 and not self.quitterProgramme:
            iCombinaison += 1
            print(f"lConstantes = {lConstantes} || {iCombinaison} / {nbCombinaisons} ({round(iCombinaison/nbCombinaisons, 2) * 100}%)")
            self.algo.lConstantes = lConstantes
            sommeScores = 0
            sommeNbCoups = 0
            sommeSommeSommeNbBlocs = 0
            for i in range(nbParties):
                self.jouer(modeAlgo=True)
                #print(f"Partie {i+1} : Score {self.score}")
                sommeScores += self.score
                sommeNbCoups += self.nbCoups
                sommeSommeSommeNbBlocs += self.sommeNbBlocs
                if self.quitterProgramme :
                    break
            moyenneScores = sommeScores / nbParties
            moyenneNbCoups = sommeNbCoups / nbParties
            moyenneSommeSommeNbBlocs = sommeSommeSommeNbBlocs / nbParties
            print(f"==> scoreMoyen = {moyenneScores}")
            print(f"==> nbCoupsMoyen = {moyenneNbCoups}")
            print(f"==> moyenneSommeSommeNbBlocs = {moyenneSommeSommeNbBlocs}")
            dicoRes[tuple(lConstantes)] = (moyenneScores, moyenneNbCoups, moyenneSommeSommeNbBlocs)
            #Changement lConstantes
            iC = len(lConstantes)-1
            lConstantes[iC] += pasConstantes
            while iC > 0 and lConstantes[iC] > 1:
                lConstantes[iC] = 0
                iC -= 1
                lConstantes[iC] += pasConstantes
            if self.quitterProgramme :
                break
        with open("dico_comparatif_lConstantes.txt", "w") as fichier:
            fichier.write(str(dicoRes))

    def changer_images_logo(self):
        if not self.menus:
            print("Pas possible d'afficher des logos sans activer les menus")
            return
        self.tailleLogo = (self.nbColonnes-1)*self.lDicoModesGrille[self.modeGrille]["tailleCases"]
        self.lImagesLogo = [Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, nom, self.tailleLogo, self.tailleLogo, None, True, False) for nom in ("logo_jeu_1.png", "logo_jeu_2.png", "logo_jeu_3.png", "logo_jeu_4.png", "logo_jeu_5.png", "logo_jeu_6.png", "logo_jeu_7.png", "logo_jeu_8.png", "logo_jeu_9.png", "logo_jeu_10.png")]

    def charger_matrices(self, dicoMatrices):
        self.dicoMatricesPieces = {}
        for (T, O), matrice in dicoMatrices.items():
            lCoordonnees = []
            for dy in range(len(matrice)):
                for dx in range(len(matrice[dy])):
                    if matrice[dy][dx] == 1:
                        lCoordonnees.append((dx, dy))
            self.dicoMatricesPieces[(T, O)] = tuple(lCoordonnees)







class Slider(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, nomCadre, nomCarreNoir, nomCarreColore, nomForme, rectangleFond, caracteristiquesTexte, enregistrement, valeurMin, valeurMax, nbValeurs, iValeur, couleurFond, couleurTexte, interactif):
        self.menus = menus
        self.menu = menu
        self.interactif = interactif

        self.hover = False
        self.couleurFond, self.couleurTexte = couleurFond, couleurTexte
        self.xFond, self.yFond, self.wFond, self.hFond = rectangleFond
        self.fond = pygame.Surface((self.wFond, self.hFond), pygame.SRCALPHA)
        self.borderRadiusFond = round(min(self.fond.get_size())*0.3)

        wT, hT, eT = caracteristiquesTexte
        self.wCarres = round((1-wT-0.2)*self.wFond / (nbValeurs-1))
        self.imCadre = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCadre, w=round(self.wCarres*(nbValeurs-1)), h=None, position=((wT+0.1)*self.wFond, 0.45*self.hFond), transparence=False, enregistrement=enregistrement)
        self.imCarreNoir = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCarreNoir, self.wCarres, None, None, False, enregistrement)
        self.imCarreColore = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomCarreColore, self.wCarres, None, None, False, enregistrement)
        hForme = round(0.7*self.wCarres)
        self.imForme = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nomForme, None, hForme, None, True, enregistrement)
        self.xDebutCarres = round(self.imCadre.position[0]+self.imCadre.dimensions[0]/2 - (nbValeurs-1)/2*self.wCarres)
        self.yDebutCarres = round(self.imCadre.position[1])

        self.nbValeurs = nbValeurs
        self.iValeur = self.nbValeurs//2 if iValeur is None else iValeur
        self.valeurMin, self.valeurMax = valeurMin, valeurMax
        self.deltaValeur = (self.valeurMax - self.valeurMin) / (self.nbValeurs-1)
        self.lValeurs = [float(f"{self.valeurMin+i*self.deltaValeur:.2f}") for i in range(self.nbValeurs)]
        self.valeur = self.lValeurs[self.iValeur]
        self.lPositionsCarres = [(self.xDebutCarres+i*self.wCarres, self.yDebutCarres) for i in range(self.nbValeurs)]
        self.lPositionsForme = [(xC-self.imForme.dimensions[0]/2-(self.wCarres-self.imCarreNoir.dimensions[0])/2, yC+0.5*(self.wCarres-self.imForme.dimensions[1])) for i,(xC,yC) in enumerate(self.lPositionsCarres)]
        self.lPositionsCarres.pop()

        self.nom = nom
        self.caracteristiquesTexte = caracteristiquesTexte
        self.changer_mode_texte()

        self.bouge = False
        self.xSA, self.ySA = None,None

    def afficher(self, fenetre):
        self.fond.fill((0,0,0,0))
        couleurFond = self.couleurFond[:3]+(255,) if self.hover else self.couleurFond
        pygame.draw.rect(self.fond, couleurFond, self.fond.get_rect())#, border_radius=self.borderRadiusFond)
        couleurBordFond = tuple(map(lambda x : min(255, round(x*0.5)), (couleurFond[:3]))) + (couleurFond[3],) if self.bouge else couleurFond
        pygame.draw.rect(self.fond, couleurBordFond, self.fond.get_rect())#, border_radius=self.borderRadiusFond, width=round(self.hFond/15))
        #Barre
        #self.imCadre.afficher(self.fond)
        for iV in range(self.nbValeurs-1):
            if iV < self.iValeur:
                self.imCarreColore.afficher(self.fond, self.lPositionsCarres[iV])
            else :
                self.imCarreNoir.afficher(self.fond, self.lPositionsCarres[iV])
        if self.interactif:
            if self.bouge:
                self.imForme.afficher(self.fond, (max(self.lPositionsForme[0][0], min(self.lPositionsForme[-1][0], self.xSA-self.imForme.dimensions[0]/2)), self.lPositionsForme[self.iValeur][1]))
            else :
                self.imForme.afficher(self.fond, self.lPositionsForme[self.iValeur])
        #Textes
        self.fond.blit(self.texteValeurMin, self.positionTexteVMin)
        self.fond.blit(self.texteValeurMax, self.positionTexteVMax)
        self.fond.blit(self.texteValeur, self.positionTexteV)
        self.fond.blit(self.texteNom, self.positionTexteNom)

        fenetre.blit(self.fond, (self.xFond, self.yFond))

    def changer_mode_texte(self):
        self.maj_valeur_min()
        self.maj_valeur_max()
        self.maj_valeur(changer_valeur=False)
        self.maj_nom()

    def gerer_souris(self):
        changement = False
        xS,yS = pygame.mouse.get_pos()
        xS -= self.xFond
        yS -= self.yFond
        self.hover = (0 <= xS <= self.wFond) and (0 <= yS <= self.hFond)
        if self.bouge:
            if not pygame.mouse.get_pressed()[0]:
                self.bouge = False
                self.imForme.position = self.lPositionsForme[self.iValeur]
                self.xSA, self.ySA = None,None
            elif self.interactif:
                if self.iValeur > 0 and xS <= self.lPositionsCarres[self.iValeur-1][0]:
                    self.iValeur -= 1
                    self.maj_valeur()
                    changement = True
                elif self.iValeur+1 < self.nbValeurs and xS > self.lPositionsCarres[self.iValeur][0]+self.wCarres:
                    self.iValeur += 1
                    self.maj_valeur()
                    changement = True
                self.xSA, self.ySA = xS, yS
        elif self.interactif and pygame.mouse.get_pressed()[0] and self.imForme.tester_hover(xS, yS):
            self.bouge = True
            self.xSA, self.ySA = xS, yS
        return changement

    def changer_valeur(self, valeur, reel=True):
        self.valeur = max(self.lValeurs[0], min(self.lValeurs[-1], valeur))
        iValeur = max(i if v<=valeur else -1 for i,v in enumerate(self.lValeurs))
        if iValeur != self.iValeur:
            self.iValeur = iValeur
        self.maj_valeur(changer_valeur=False)
        if reel:
            self.menus.afficher()

    def maj_valeur(self, changer_valeur=True):
        if changer_valeur:
            self.valeur = self.lValeurs[self.iValeur]
        self.texteValeur = self.menus.generateurTexte.creer_surface_texte(str(round(self.valeur,2)), 0.2*self.wFond, 0.3*self.hFond, 0.1, self.couleurTexte)
        self.positionTexteV = (self.imCadre.position[0]+(self.imCadre.dimensions[0]-self.texteValeur.get_width())/2, self.lPositionsCarres[0][1]-self.texteValeur.get_height())

    def maj_valeur_min(self):
        self.texteValeurMin = self.menus.generateurTexte.creer_surface_texte(str(self.valeurMin), 0.2*self.wFond, 0.3*self.hFond, 0.05, self.couleurTexte)
        self.positionTexteVMin = (self.imCadre.position[0]-(self.texteValeurMin.get_width()+self.imCarreNoir.image.get_width()/2), self.imCadre.position[1]+(self.wCarres-self.texteValeurMin.get_height())/2)

    def maj_valeur_max(self):
        self.texteValeurMax = self.menus.generateurTexte.creer_surface_texte(str(self.valeurMax), 0.06*self.wFond, 0.3*self.hFond, 0.05, self.couleurTexte)
        self.positionTexteVMax = (self.lPositionsCarres[-1][0]+1.2*self.wCarres, self.imCadre.position[1]+(self.wCarres-self.texteValeurMax.get_height())/2)

    def maj_nom(self):
        wT, hT, eT = self.caracteristiquesTexte
        wTexte = wT*self.wFond
        hTexte = hT*self.hFond
        self.texteNom = self.menus.generateurTexte.creer_surface_texte(self.nom, wTexte, hTexte, eT, self.couleurTexte)
        self.positionTexteNom = ((wTexte-self.texteNom.get_width())/2, (self.hFond-self.texteNom.get_height())/2)







class QCU(object):
    def __init__(self, menus, menu, nom, rectangleFond, caracteristiquesTexte, caracteristiquesEspacements, caracteristiquesCarres, iCarre, lTypeCarres, nbLignes, couleurFond, couleurTexte, couleurCarreChoix, alphaInactif, interactif):
        self.menus = menus
        self.menu = menu
        self.interactif = interactif

        self.hover = False
        self.couleurFond, self.couleurTexte, self.couleurCarreChoix, self.alphaInactif = couleurFond, couleurTexte, couleurCarreChoix, alphaInactif
        self.xFond, self.yFond, self.wFond, self.hFond = rectangleFond
        self.fond = pygame.Surface((self.wFond, self.hFond), pygame.SRCALPHA)
        self.borderRadiusFond = round(min(self.fond.get_size())*0.3)

        self.nom = nom
        self.eGaucheTexte, self.eTexteCarres, self.eCarresDroite = caracteristiquesEspacements
        self.wTexte, self.hTexte, self.eTexte = caracteristiquesTexte
        self.blocTexteNom = self.creer_rectangle_couleur(couleur=(0,0,0,100), w=self.wTexte*self.wFond, h=self.hTexte*self.hFond)
        self.positionBlocTexteNom = (self.eGaucheTexte*self.wFond, self.hFond*(1-self.hTexte)/2)
        
        self.lTypeCarres = lTypeCarres
        self.nbCarres = len(self.lTypeCarres)
        self.iCarre = iCarre
        self.nbLignes = nbLignes
        self.nbColonnes = ceil(self.nbCarres / self.nbLignes)
        self.wTotalCarres = 1-(self.wTexte+self.eGaucheTexte+self.eTexteCarres+self.eCarresDroite)
        self.hTotalCarres, self.eCarres = caracteristiquesCarres
        self.wCarres = (self.wTotalCarres - self.eCarres) / self.nbColonnes - self.eCarres
        self.hCarres = (self.hTotalCarres - self.eCarres*self.wFond/self.hFond) / self.nbLignes - self.eCarres
        self.hCarres = min(self.wCarres*self.wFond, self.hCarres*self.hFond) / self.hFond
        self.eCarres2 = (self.hTotalCarres - self.nbLignes*self.hCarres) / (self.nbLignes+1)
        xCarres = (self.eGaucheTexte+self.wTexte+self.eTexteCarres+self.eCarres)*self.wFond
        yCarres = (1 - (self.nbLignes*self.hCarres+(self.nbLignes-1)*self.eCarres2))/2 * self.hFond
        self.lPositionsCarres = []
        for y in range(self.nbLignes):
            for x in range(self.nbColonnes):
                x2 = xCarres + x*(self.wCarres+self.eCarres)*self.wFond
                y2 = yCarres + y*(self.hCarres+self.eCarres2)*self.hFond
                self.lPositionsCarres.append((x2, y2))
        self.lCarres = [self.creer_carre(typeCarre=typeCarre, w=self.hCarres*self.hFond, h=self.hCarres*self.hFond) for typeCarre in self.lTypeCarres]
        tailleBlocCarre = min(self.eCarres*self.wFond, self.eCarres2*self.hFond)
        self.blocCarre = self.creer_rectangle_couleur(couleur=(0,0,0,100), w=tailleBlocCarre, h=tailleBlocCarre)
        self.positionBlocCarre = ((self.eGaucheTexte+self.wTexte+self.eTexteCarres)*self.wFond, self.hFond*(1-self.hTotalCarres)/2)
        self.carreChoix = self.creer_rectangle_couleur(couleur=self.couleurCarreChoix, w=self.hFond*self.hCarres+self.eCarres*self.wFond, h=self.hFond*self.hCarres+self.eCarres*self.wFond)
        
        self.lCarresActifs = [True]*self.nbCarres
        self.changer_choix()

    def reset(self):
        self.changer_mode_texte()

    def afficher(self, fenetre):
        self.fond.fill((0,0,0,0))
        couleurFond = self.couleurFond[:3]+(255,) if self.hover else self.couleurFond
        pygame.draw.rect(self.fond, couleurFond, self.fond.get_rect())#, border_radius=self.borderRadiusFond)
        
        #self.fond.blit(self.blocTexteNom, self.positionBlocTexteNom)
        self.fond.blit(self.texteNom, self.positionTexteNom)
        #self.fond.blit(self.blocCarre, self.positionBlocCarre)
        self.fond.blit(self.carreChoix, self.positionCarreChoix)
        for (xC,yC),carre in zip(self.lPositionsCarres, self.lCarres):
            self.fond.blit(carre, (xC, yC))

        fenetre.blit(self.fond, (self.xFond, self.yFond))

    def gerer_souris(self, lEvents):
        xS,yS = pygame.mouse.get_pos()
        xS -= self.xFond
        yS -= self.yFond
        self.hover = (0 <= xS <= self.wFond) and (0 <= yS <= self.hFond)
        self.changement = False
        for event in lEvents:
            if event.type == pygame.MOUSEBUTTONDOWN:
                xS,yS = event.pos
                xS -= self.xFond
                yS -= self.yFond
                if (self.lPositionsCarres[0][0] <= xS <= self.lPositionsCarres[-1][0]+self.hFond*self.hCarres) and (self.lPositionsCarres[0][1] <= yS <= self.lPositionsCarres[-1][1]+self.hFond*self.hCarres):
                    for i,((xC,yC),carre) in enumerate(zip(self.lPositionsCarres, self.lCarres)):
                        if (xC <= xS <= xC+carre.get_width()) and (yC <= yS <= yC+carre.get_height() and self.lCarresActifs[i]):
                            self.iCarre = i
                            self.changement = True
        if self.changement :
            self.changer_choix()
        return self.changement
    
    def changer_choix(self):
        self.positionCarreChoix = (self.lPositionsCarres[self.iCarre][0]-self.eCarres*self.wFond/2, self.lPositionsCarres[self.iCarre][1]-self.eCarres*self.wFond/2)

    def changer_mode_texte(self):
        self.maj_nom()

    def maj_nom(self):
        self.texteNom = self.menus.generateurTexte.creer_surface_texte(self.nom, self.wTexte*self.wFond, self.hTexte*self.hFond, self.eTexte, self.couleurTexte)
        self.positionTexteNom = (((self.eGaucheTexte+self.wTexte)*self.wFond-self.texteNom.get_width())/2, (self.hFond-self.texteNom.get_height())/2)
        
    def creer_carre(self, typeCarre, w, h):
        if typeCarre[0] == 'Couleur': #('Couleur', c)
            carre = self.creer_rectangle_couleur(couleur=typeCarre[1], w=w, h=h)
        elif typeCarre[0] == 'Texte': #('Texte', cFond, cTexte, texte)
            carre = self.creer_rectangle_couleur(couleur=typeCarre[1], w=w, h=h)
            texte = self.menus.generateurTexte.creer_surface_texte(typeCarre[3], w, h, self.eTexte, typeCarre[2])
            carre.blit(texte, ((carre.get_width()-texte.get_width())/2, (carre.get_height()-texte.get_height())/2))
        elif typeCarre[0] == 'Texture':
            typeTexture =  typeCarre[1]
            c1 = typeCarre[2]
            carre = self.creer_rectangle_couleur(couleur=c1, w=w, h=h)
            if typeTexture == 'mise_en_abyme':
                _, _, _, c2, n = typeCarre
                dx = (w/2)/n
                for i in range(n):
                    w2 = w-i*2*dx
                    h2 = h-i*2*dx
                    carre2 = self.creer_rectangle_couleur(couleur=[c1,c2][i%2], w=w2, h=h2)
                    carre.blit(carre2, (i*dx, i*dx))
            elif typeTexture == "grille":
                _, _, _, c2, n, prop1 = typeCarre
                w2 = (1 - prop1) * w / n
                dx = w/n
                carre2 = self.creer_rectangle_couleur(couleur=c2, w=w2, h=w2)
                for y in range(n):
                    for x in range(n):
                        x2 = prop1*dx/2 + x*dx
                        y2 = prop1*dx/2 + y*dx
                        carre.blit(carre2, (x2, y2))
            elif typeTexture == "rayures":
                _, _, _, c2, n, orientation = typeCarre
                if orientation == "horizontal":
                    w2 = w
                    h2 = round(h/n)
                    dx, dy = 0, h2
                elif orientation == "vertical" :
                    w2 = round(w/n)
                    h2 = h
                    dx, dy = w2, 0
                carre2 = self.creer_rectangle_couleur(couleur=c2, w=w2, h=h2)
                for i in range(n):
                    if i%2 == 1:
                        carre.blit(carre2, (i*dx, i*dy))

        return carre

    def creer_rectangle_couleur(self, couleur, w, h):
        if len(couleur) == 4:
            surface = pygame.Surface((w,h), pygame.SRCALPHA)
            surface.set_alpha(couleur[3])
        else:
            surface = pygame.Surface((w,h))
        surface.fill(couleur[:3])
        return surface
    
    def changement_etat_actif(self, iCarre=None):
        iCarre = self.iCarre if iCarre is None else iCarre
        self.lCarresActifs[iCarre] = False
        self.lCarres[iCarre].set_alpha(self.alphaInactif)








class Generateur_Texte(object):
    def __init__(self, menus, lAttributsPolice, dossier1, dossier2, dossier3, dicoNoms, transparence, enregistrement):
        self.menus = menus #class Menus

        self.lImages = {nom : Image(self.menus, self, dossier1, dossier2, dossier3, nomFichier, None, None, None, transparence, enregistrement) for nom,nomFichier in dicoNoms.items()}
        self.dicoImagesVu = {}
        self.nomPolice, self.taillePolice, self.grasPolice, self.italiquePolice = lAttributsPolice
        self.dicoPoliceVues = {}

    def recuperer_image(self, nom, w, h):
        dico = self.dicoImagesVu if self.menus.modeTexte == "IMAGES" else self.dicoPoliceVues
        if self.menus.modeTexte == "IMAGES":
            cle = (nom, w, h)
            if cle not in dico:
                image, _ = self.menus.modifier_dimensions(self.lImages[nom].image, w, h)
                dico[cle] = image
            return dico[cle]
        elif self.menus.modeTexte == "POLICE":
            cle = round(h)
            if cle not in dico:
                police = pygame.font.SysFont(self.nomPolice, cle, bold=self.grasPolice, italic=self.italiquePolice)
                #print(f"hTheorique = {cle} VS hRender = {police.render('None', True, (0,0,0)).get_height()}")
                dico[cle] = police
            return dico[cle].render(nom, True, (0,0,0))

    def creer_surface_texte(self, texte, wTotal, hTotal, espacement, couleur=None):
        texte = texte.upper()
        hL, hR = 0, hTotal
        while hR-hL > 1e-2:
            hM = (hL + hR)/2
            wImagesTotal = 0
            for car in texte:
                wImagesTotal += self.recuperer_image(car, hTotal, hM).get_width()
            wEspacement = (espacement*wImagesTotal) / (len(texte)-1) if len(texte) > 1 else 0
            wTotal2 = wImagesTotal + wEspacement*(len(texte)-1)
            if wTotal2 > wTotal:
                hR = hM
            else :
                hL = hM
        hI = hL
        lImages = []
        wImagesTotal = 0
        for car in texte:
            lImages.append(self.recuperer_image(car, wTotal, hI))
            wImagesTotal += lImages[-1].get_width()
        wEspacement = (espacement*wImagesTotal) / (len(texte)-1) if len(texte) > 1 else 0
        wTotal = wImagesTotal + wEspacement*(len(texte)-1)
        if self.menus.modeTexte == "IMAGES":
            surface = pygame.Surface((wTotal, hI), pygame.SRCALPHA)
            surface.set_alpha(0)
            x = 0
            for image in lImages:
                surface.blit(image, (x, 0))
                x += image.get_width() + wEspacement
        else :
            surface = self.dicoPoliceVues[round(hI)].render(texte, True, couleur)
        return surface








class Bouton(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menus = menus
        self.menu = menu
        self.image = Image(self.menus, self.menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement)
        self.imageNormal = self.image.image.copy()
        self.imageHover = self.menus.changer_couleur(self.imageNormal, 1.3)
        self.imagePressed = self.menus.changer_couleur(self.imageNormal, 0.8)
        self.hover, self.pressed = False, False

    def gerer_souris(self, xS=None, yS=None, appuie=None):
        if xS is None or yS is None:
            xS, yS = pygame.mouse.get_pos()
        if appuie is None:
            appuie = pygame.mouse.get_pressed()[0]
        self.hover = (self.image.position[0] <= xS <= self.image.position[0]+self.image.dimensions[0]) and (self.image.position[1] <= yS <= self.image.position[1]+self.image.dimensions[1])
        clicked = self.hover and self.pressed and not appuie
        self.pressed = self.hover and appuie
        if clicked and self.menus.audio and self.menus.son:
            self.menus.lSonsClique[self.menus.iSonClique].play()
        return clicked

    def afficher(self, fenetre):
        image = self.imagePressed if self.pressed else self.imageHover if self.hover else self.imageNormal
        x,y = self.image.position
        y += 0.05*self.image.dimensions[1] if self.pressed else 0
        fenetre.blit(image, (x,y))





class Image(object):
    def __init__(self, menus, menu, dossier1, dossier2, dossier3, nom, w, h, position, transparence, enregistrement):
        self.menus = menus
        self.menu = menu
        self.image, self.dimensions = self.menus.ouvrir_image(dossier1, dossier2, nom, dossier3, w, h, transparence, enregistrement)
        self.position = position

    def afficher(self, fenetre, position=None):
        self.position = self.position if position is None else position
        fenetre.blit(self.image, self.position)

    def tester_hover(self, xS=None, yS=None):
        if xS is None or yS is None:
            xS, yS = pygame.mouse.get_pos()
        return (self.position[0] <= xS <= self.position[0]+self.dimensions[0]) and (self.position[1] <= yS <= self.position[1]+self.dimensions[1])

class Menu_Type(object):
    def __init__(self, menus):
        self.menus = menus

        self.actif = False

        self.imFond = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\IMAGES", self.menus.dossierOutput, "background_1.jpg", None, self.menus.fenetre.get_height(), (0, 0), False, True)
        self.texte = Image(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\TEXTES", self.menus.dossierOutput, "None.png", None, 0.08*self.menus.hF, None, True, False)
        self.texte.position = ((self.menus.wF-self.texte.dimensions[0])/2, 0.01*self.menus.hF)
        self.boutonHome = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "accueil.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][0], True, False)
        self.boutonEcriture = Bouton(self.menus, self, self.menus.dossier, f"{self.menus.dossierInput}\\ICONS", self.menus.dossierOutput, "ecriture.png", self.menus.wBoutons, None, self.menus.lPositionsBoutons[0][1], True, False)

        self.lImages = [self.texteInfo]
        self.lBoutons = [self.boutonHome, self.boutonEcriture]
        self.lElements = self.lImages + self.lBoutons

    def reset(self):
        self.changer_mode_texte()

    def afficher(self):
        self.imFond.afficher(self.menus.fenetre)
        for element in self.lElements:
            element.afficher(self.menus.fenetre)

    def gerer_souris(self, lEvents):
        if self.boutonHome.gerer_souris():
            self.actif = False
            self.menus.menuHome.actif = True
            self.menus.menuHome.reset()
        if self.boutonEcriture.gerer_souris():
            self.menus.modeTexte = "POLICE" if self.menus.modeTexte == "IMAGES" else "IMAGES"
            self.changer_mode_texte()

    def changer_mode_texte(self):
        pass
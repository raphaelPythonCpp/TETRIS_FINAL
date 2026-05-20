import pygame
from math import ceil, sqrt

pygame.init()

wFenetre, hFenetre = 800, 600
fenetre = pygame.display.set_mode((wFenetre, hFenetre))
pygame.display.set_caption("TETRIS v8 Raphaël")

police = pygame.font.SysFont("Arial", 15, bold=True, italic=False)
clock = pygame.time.Clock()

GA = True
NES = False
DRL = False
assert GA and not NES and not DRL #pas implémentés

if GA : 
    fichier = "lDicoReseau_GA_NN"
elif DRL:
    fichier = "lConstantes_DRL"
with open(f"{fichier}.txt") as fichier:
    data = eval(fichier.read())
    lNbNoeuds = data[0]
    lDicoReseau = data[1:]
print(lNbNoeuds)
nbEpisodes = sum(1 if data is not None else 0 for data in lDicoReseau)
lItems = [[True, True, 2*(i-1), lNbNoeuds[i-1], lNbNoeuds[i]] for i in range(1, len(lNbNoeuds))] # (weight, bias, number, nbNodesBefore, nbNodesCurrent)
nbLayers = len(lNbNoeuds)
maxWeight, minWeight = -float("inf"), float("inf")
maxBias, minBias = -float("inf"), float("inf")
for i, (w,b,n,nbNA,nbNC) in enumerate(lItems):
    if w : #mandatory
        maxWeight = max(maxWeight, max(max(max(lValeurs) for lValeurs in dicoReseau[f"{n}.weight"]) for dicoReseau in lDicoReseau[:nbEpisodes]))
        minWeight = min(minWeight, min(min(min(lValeurs) for lValeurs in dicoReseau[f"{n}.weight"]) for dicoReseau in lDicoReseau[:nbEpisodes]))
    if b :
        maxBias = max(maxBias, max(max(dicoReseau[f"{n}.bias"]) for dicoReseau in lDicoReseau[:nbEpisodes]))
        minBias = min(minBias, min(min(dicoReseau[f"{n}.bias"]) for dicoReseau in lDicoReseau[:nbEpisodes]))
#print("lItems  :  ", lItems)

def calculate_lxy(nbNodes, x, r, h):
    dy = (h-2*r) / nbNodes
    yMin = h/2 - nbNodes//2*dy + dy/2*(nbNodes%2==0)
    lXY = [(x, yMin+dy*i) for i in range(nbNodes)]
    return lXY

radiusNodes = min(wFenetre/(3*(nbLayers+1)), hFenetre/(3*max(lNbNoeuds)))
dx = (wFenetre-2*radiusNodes) / (nbLayers-0.5)
xMin = wFenetre/2 - nbLayers//2*dx + dx/2*(nbLayers%2==0)
listeLXY = [calculate_lxy(lItems[0][3], xMin, radiusNodes, hFenetre)] + [calculate_lxy(lItems[i-1][4], xMin+i*dx, radiusNodes, hFenetre) for i in range(1, nbLayers)]

def calculate_lp1p2p3p4(lXYBefore, lXYCurrent, w):
    delta = w/2
    listeLP1P2P3P4 = []
    for (xNC, yNC) in lXYCurrent:
        lP1P2P3P4 = []
        for (xNB,yNB) in lXYBefore:
            dx = xNC - xNB
            dy = yNC - yNB
            l = sqrt(dx**2 + dy**2)
            ux = -dy / l
            uy = dx / l
            p1 = (xNB - ux*delta, yNB - uy*delta)
            p2 = (xNB + ux*delta, yNB + uy*delta)
            p3 = (xNC + ux*delta, yNC + uy*delta)
            p4 = (xNC - ux*delta, yNC - uy*delta)
            lP1P2P3P4.append((p1,p2,p3,p4))
        listeLP1P2P3P4.append(lP1P2P3P4)
    return listeLP1P2P3P4

wEdges = radiusNodes / 7
lListeLP1P2P3P4 = [calculate_lp1p2p3p4(listeLXY[i-1], listeLXY[i], wEdges) for i in range(1, nbLayers)]
#print(lListeLP1P2P3P4)

def draw_nodes_layer(fenetre, lXY, lBias, biasMax, biasMin, r, rMax, rMin, gMax, gMin, bMax, bMin, color=None):
    for (xN, yN), bias in zip(lXY, lBias) :
        rapport = (bias-biasMin) / (biasMax-biasMin)
        c = (rMin+(rMax-rMin)*rapport, gMin+(gMax-gMin)*rapport, bMin+(bMax-bMin)*rapport) if color is None else color
        pygame.draw.circle(fenetre, c, (xN,yN), r)

def draw_edges_layer(fenetre, listeLP1P2P3P4, listeLWeights, weightMax, weightMin, rMax, rMin, gMax, gMin, bMax, bMin):
    for lP1P2P3P4, lWeights in zip(listeLP1P2P3P4, listeLWeights):
        for lP1P2P3P4, weight in zip(lP1P2P3P4, lWeights):
            rapport = (weight-weightMin) / (weightMax-weightMin)
            c = (rMin+(rMax-rMin)*rapport, gMin+(gMax-gMin)*rapport, bMin+(bMax-bMin)*rapport)
            pygame.draw.polygon(fenetre, c, lP1P2P3P4)

def draw_texte(fenetre, text, xT, yT, c):
    surface = police.render(text, True, c)
    fenetre.blit(surface, (xT,yT))

def afficher(fenetre, iEpisode):
    fenetre.fill((0,0,0))

    for i in range(1, nbLayers):
        draw_edges_layer(fenetre, lListeLP1P2P3P4[i-1], lDicoReseau[iEpisode][f"{lItems[i-1][2]}.weight"], maxWeight, minWeight, 0, 255, 255, 0, 0, 0)
    draw_nodes_layer(fenetre, listeLXY[0], [0]*lItems[0][3], maxBias, minBias, radiusNodes, 0, 255, 255, 0, 0, 0, color=(255,255,255))
    for i in range(1, nbLayers):
        draw_nodes_layer(fenetre, listeLXY[i], lDicoReseau[iEpisode][f"{lItems[i-1][2]}.bias"], maxBias, minBias, radiusNodes, 0, 255, 255, 0, 0, 0)
    
    draw_texte(fenetre, f"Episode : {iEpisode+1}", wFenetre*0.8, hFenetre*0.1, (255,255,255))
    
    pygame.display.flip()

iEpisode = 0
quitterProgramme = False
while not quitterProgramme:
    clock.tick(nbEpisodes//3)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quitterProgramme = True
    afficher(fenetre, iEpisode)
    iEpisode += 1
    if iEpisode == nbEpisodes:
        iEpisode = 0
        pygame.time.delay(1000)

pygame.quit()
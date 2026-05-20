import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, Slider
import numpy as np
from scipy.optimize import linear_sum_assignment

with open("listeLDicoReseau_GA_NN.txt", 'r') as fichier:
    listeLDicoReseau = eval(fichier.read())
    iMax = max(i for i,lDicoReseau in enumerate(listeLDicoReseau) if lDicoReseau if not None)
    listeLDicoReseau = listeLDicoReseau[1:iMax+1]
nbGenerations = len(listeLDicoReseau)
nbIndividus = len(listeLDicoReseau[0])
listeLReseauNormal = [[dicoReseau['0.weight'][0] for iI,dicoReseau in lDicoReseau] for lDicoReseau in zip(*listeLDicoReseau)]
dico = {i : [] for i in range(nbIndividus)}
for lDicoReseau in listeLDicoReseau:
    for iI, dicoReseau in lDicoReseau:
        dico[iI].append(dicoReseau['0.weight'][0])
listeLReseauIndividus = [dico[i] for i in range(nbIndividus)]

listeLReseauTrie = [[lReseau[0] for lReseau in listeLReseauIndividus]]
for i in range(nbGenerations-1):
    lPointsCourant = np.array(listeLReseauTrie[-1])
    lPointsSuivant = np.array([lReseau[i+1] for lReseau in listeLReseauIndividus])
    lCouts = np.linalg.norm(lPointsCourant[:, None, :] - lPointsSuivant[None, :, :], axis=2)
    lI, lJ = linear_sum_assignment(lCouts)
    dico = {i:j for i,j in zip(lI, lJ)}
    """lDistances = []
    for j,(x,y) in enumerate(lPointsCourant):
        for k,(x2,y2) in enumerate(lPointsSuivant):
            lDistances.append((j, k, (x2-x)**2+(y2-y)**2))
    lDistances.sort(key=lambda triplet : triplet[2])
    dico = {i : None for i in range(nbIndividus)}
    lPointsPris = set()
    for i1,i2,_ in lDistances:
        if dico[i1] is not None or i2 in lPointsPris:
            continue
        dico[i1] = i2
        lPointsPris.add(i2)"""
    listeLReseauTrie.append([lPointsSuivant[dico[i]] for i in range(nbIndividus)])


v1Min, v1Max = -1, 1#min(v1 for lReseau in listeLReseauIndividus for v1,v2 in lReseau), max(v1 for lReseau in listeLReseauIndividus for v1,v2 in lReseau)
v2Min, v2Max = -1, 1#min(v2 for lReseau in listeLReseauIndividus for v1,v2 in lReseau), max(v2 for lReseau in listeLReseauIndividus for v1,v2 in lReseau)

def afficher(axe):
    global animationAxe

    axe.clear()
    listeLReseau = [listeLReseauTrie, listeLReseauNormal, listeLReseauIndividus][normal]
    listeLReseau = np.array([[(lValeurs[int(sliderIndex1.val)], lValeurs[int(sliderIndex2.val)]) for lValeurs in lReseau] for lReseau in listeLReseau])
    if animations:
        courbe = axe.scatter([], [], color=(0,0,0.8))
    else :
        courbe = axe.scatter(listeLReseau[:, :, 0], listeLReseau[:, :, 1], color=(0,0,0.8))
    axe.set_xlim(v1Min, v1Max)
    axe.set_ylim(v2Min, v2Max)
    if animationAxe is not None and animationAxe.event_source is not None:
            animationAxe.event_source.stop()
    if animations:
        animationAxe = animer(fig, courbe, listeLReseau)
    fig.canvas.draw()

def animer(fig, courbe, listeLReseau):
    def update(frame):
        u = frame/nbFrames
        t = u*(nbX-1)
        i = int(t)
        dx = t-i
        if i+1 < nbX:
            lPoints = listeLReseau[:, i, :] + dx*(listeLReseau[:, i+1, :]-listeLReseau[:, i, :]) 
        else :
            lPoints = listeLReseau[:, i, :]
        courbe.set_offsets(lPoints)
        return (courbe,)

    nbX = len(listeLReseau[0])
    nbFrames = 4*nbX
    return FuncAnimation(fig, update, frames=nbFrames, init_func=None, fargs=None, save_count=None, interval=1, repeat_delay=1000, repeat=False, blit=True, cache_frame_data=False)

def changer_mode_normal(_):
    global normal
    normal = (normal+1)%3
    boutonNormal.label.set_text("Individus ? " if normal==1 else "Normal ? " if normal==0 else "Trié ?")
    afficher(axe1)

def changer_mode_animations(_):
    global animations, animationAxe
    animations = not animations
    boutonAnimations.label.set_text("Sans animations ?" if animations else "Avec animations ?")
    afficher(axe1)

def changer_valeur_slider(slider1, slider2):
    """if slider1.val == slider2.val :
        slider1.val = (slider1.val+1)%slider1.valmax"""
    afficher(axe1)

fig, (axe1, axe2, axe3, axe4, axe5) = plt.subplots(5, 1)

axe1.set_position([0.1, 0.15, 0.8, 0.8])
axe2.set_position([0.85, 0.0, 0.1, 0.1])
axe3.set_position([0.70, 0.0, 0.1, 0.1])
axe4.set_position([0.40, 0.0, 0.2, 0.05])
axe5.set_position([0.10, 0.0, 0.2, 0.05])

normal = 0
boutonNormal = Button(axe2, "None")
boutonNormal.on_clicked(changer_mode_normal)

animations = True
animationAxe = None
boutonAnimations = Button(axe3, "None")
boutonAnimations.on_clicked(changer_mode_animations)

sliderIndex1 = Slider(axe4, "Index 1", 0, len(listeLReseauIndividus[0][0])-1)
sliderIndex2 = Slider(axe5, "Index 2", 0, len(listeLReseauIndividus[0][0])-1)
sliderIndex1.set_val(0)
sliderIndex2.set_val(1)
sliderIndex1.on_changed(lambda _ : changer_valeur_slider(sliderIndex1, sliderIndex2))
sliderIndex2.on_changed(lambda _ : changer_valeur_slider(sliderIndex2, sliderIndex1))

changer_mode_normal(None)
changer_mode_animations(None)

plt.show()
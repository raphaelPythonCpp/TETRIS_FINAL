import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from math import log10

def distribution(lValeurs, ecart): #trié ordre décroissant
    lValeursEffectifs = []
    valeurAvant, effectifAvant = 0, 0
    for valeur in lValeurs:
        ajout = ecart * ((valeur-valeurAvant)//ecart)
        if ajout > 0:
            lValeursEffectifs.append((valeurAvant, valeurAvant+ecart-1, effectifAvant))
            effectifAvant = 0
        valeurAvant += ecart * ((valeur-valeurAvant)//ecart)
        effectifAvant += 1
    lValeursEffectifs.append((valeurAvant, valeurAvant+ecart-1, effectifAvant))
    return lValeursEffectifs

def tracer_courbe(lValeursEffectifs, nom, axe):
    axe.clear()
    valeurMin, valeurMax = lValeursEffectifs[0][0], lValeursEffectifs[-1][1]
    for i, (valeur1, valeur2, effectif) in enumerate(lValeursEffectifs):
        valeur = (valeur1+valeur2)//2
        c = (valeur - valeurMin) / (valeurMax - valeurMin+1e-10)
        titre = f"{nom}Min" if i==0 else f"{nom}Max" if i==len(lValeursEffectifs)-1 else ""
        #axe.scatter(valeur, effectif, label=titre, color=(1-c, c, (2*c)%1))
        axe.bar(x=valeur1, height=effectif, width=(valeur2-valeur1+1), align="edge", label=titre, color=(1-c, c, (2*c)%1))
    axe.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    axe.set_xlabel(nom)
    axe.set_ylabel("effectif")
    axe.set_yscale("log")
    axe.set_ylim(0)
    return valeurMin, valeurMax

def calculs(ecart, lValeurs, nom, axe):
    lValeursEffectifs = distribution(lValeurs, ecart)
    vMin, vMax = tracer_courbe(lValeursEffectifs, nom, axe)
    return vMin, vMax

def changer_ecart(_, slider, lValeurs, nom, axe):
    ecart = int(10**slider.val)
    vMin, vMax = calculs(ecart, lValeurs, nom, axe)
    fig.canvas.draw_idle()

def changer_ecart_2(_, slider, lValeurs, nom, axe):
    global ani
    try:
        ani.event_source.stop()
    except:
        pass
    ecart_new = int(10**slider.val)
    ani = animer_transition(lValeurs, nom, axe, 1, ecart_new)

def animer_transition(lValeurs, nom, axe, ecart_old, ecart_new, steps=20):
    ecarts = [int(ecart_old + (ecart_new-ecart_old)*i/steps) for i in range(steps)]

    def update(frame):
        ecart = max(1, ecarts[frame])
        lValeursEffectifs = distribution(lValeurs, ecart)

        axe.clear()
        tracer_courbe(lValeursEffectifs, nom, axe)

        fig.canvas.draw_idle()      # 🔴 essentiel
        return axe.patches

    ani = FuncAnimation(
        fig,
        update,
        frames=len(ecarts),
        interval=10,
        blit=False,
        repeat=False
    )

    return ani

with open("recherche_initiale_GA_NN.txt", "r") as fichier:
    nbIndividus, lNbNoeuds, lScores, lNbCoups = eval(fichier.read()) #triés ordre décroissant
    iMax = max(i if doublet is not None else -1 for i,doublet in enumerate(lScores))
    lScores = sorted([score for iI, score in lScores[:iMax+1]], reverse=False)
    lNbCoups = sorted([nbCoups for iI,nbCoups in lNbCoups[:iMax+1]], reverse=False)

fig,(axe1,axe2,axe3,axe4) = plt.subplots(4, 1)
axe1.set_position([0.1, 0.65, 0.7, 0.25])
axe2.set_position([0.1, 0.3, 0.7, 0.3])
axe3.set_position([0.1, 0.15, 0.7, 0.1])
axe4.set_position([0.1, 0.05, 0.7, 0.1])

fig.suptitle(f"{nbIndividus} individus avec le réseau {'⇝'.join(map(str, lNbNoeuds))}")

scoreMin, scoreMax = calculs(1, lScores, "score", axe1)
nbCoupsMin, nbCoupsMax = calculs(1, lNbCoups, "nbCoups", axe2)

sliderScore = Slider(axe3, "Ecart scores", valmin=1, valmax=log10(lScores[-1]-lScores[0]), valinit=1)
sliderScore.on_changed(lambda _ : changer_ecart(_, sliderScore, lScores, "score", axe1))

sliderNbCoups = Slider(axe4, "Ecart nbCoups", valmin=1, valmax=log10(lNbCoups[-1]-lNbCoups[0]), valinit=1)
sliderNbCoups.on_changed(lambda _ : changer_ecart(_, sliderNbCoups, lNbCoups, "nbCoups", axe2))

plt.show()
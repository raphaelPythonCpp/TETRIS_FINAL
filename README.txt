Projet TETRIS de NSI (début 2026):

Auteurs : Raphaël + Joshua + Luther

Professeur : M.Mandon Hugues

Language : Python

Librairies : pygame, random, time, numpy, torch, collections, math

Sources illustrations : Internet + Paint + IA génératives

Source code : 100% humain (chaque ligne, absolument toutes, écrites par Raphaël)

Source musique (tetris theme) : Raphaël (marimba) + Joshua (alto) + Luther (non il a eu la flemme || skill_issue)

Répartitions du travail :
- Raphaël : Code + Illustrations + Idées
- Joshua : Code' + Illustrations + Idées
- Luther : Code'' + Soutient?
=> Elle était au départ totalement équitable, mais certains collaborateurs ne collaborants pas, le(s) autre(s) ont dû prendre le relais. 

Temps de travail : ->+inf

Fichiers nécessaires au minimum: main.py + menus.py + TETROMINO.py + dicoMatricesPiecesJolies.txt + MENUS (dossier dé-zipé)

ATTENTION : Ne pas modifier le code, lancer juste le main.py
Python est un peu incompréhensible, du coup certaines fonctionnalitées (ouvertures fichiers, algorithme, GA, écriture par images, ...) ne fonctionnent pas sur certains ordinateurs...
Pour cela, il faut être sous Windows (sinon l'ouvertue de fichier par '...\\...' n'est pas supportée), et il faut installer la librairie torch si on souhaite bénéficier des fonctionnalités d'algorithmique.
Si l'installation de torch se révèle impossible, désactiver ses fonctions en modifiant juste l'appel à 'Menus' dans 'main.py' en mettent 'algorithme = False' au lieu de 'algorithme = True'

Si tout fonctionne, on arrive sur le menu d'accueil. On va ensuite découper l'expérience en plusieurs blocs, atteignables en cliquant sur les logos (<=> boutons)
- Menu Paramètres (logo écrou) : permet de modifier les aspects visuels et sonores
- Menu Didactique (logo Feuille) (obligatoire pour ce projet) : permet de faire apprendre à l'utilisateur une composition correcte des paramètres des bots (voir présention 'presentation.odp'). Fonction activable que avec 'torch'. On peut alors tenter de répliquer une descente de gradient manuelle pour atteidre un optimum local. 
- Menu Création de pièces (logo sac) : permet de créer des propres pièces. L'icone 'sauvegarder' permet d'enregistrer la composition si elle est valide, donc si toutes les cases coloriées sont reliées avec un côté à une autre case coloriée. L'icone 'croix rouge' supprimer toutes les créations de pièces depuis le lancement du programme, et il ne reste alors que les pièces d'origine. Enfin l'icone 'reset' efface toutes les cases coloriées de la grille. Si une nouvelle piece est enregistrée, alors la grille redevient vide. 
- Menu Info (logo i) : permet de savoir qu'il faut venir ici
- Menu Jeu (gros logo 'TETRIS GALAXY RJL') : permet de jouer au jeu, selon l'un des 3 modes choisi en cliquant sur les icons 'easy' 'medium' ou 'hard' avec un board qui s'adapte en conséquence. Les touches sont : K_UP pour tourner la pièce (si possible), K_RIGHT pour la déplacer à droite (si possible), K_LEFT pour la déplacer à gauche (si possible), K_DOWN pour faire descendre la pièce plus vite, K_SPACE pour faire drop la pièce, K_B pour lancer le mode algo (si algo activé), K_A pour appliquer la position jugée optimale par le bot (si algo activé), K_P pour afficher visuelement toutes les positions d'arrivées de la pièces (si algo activé). Noter que le style du logo centrale évolu au cours du temps
- Menu GameOver (après mort jeu) : permet de rien du tout et faut revenir sur Menu_Home

Pour faire fonctionner les sliders, il faut appuyer sur la mini-pièce au centre du slider, entre la partie vide et celle pleine

Il est également normalement possible de lancer un algorithme génétique pour qu'ils apprennent à jouer, puis d'analyser les résultats avec les 3 fichiers d'analyse.

Note estimée méritée : 15/20 graphismes + 100/20 algorithmique + 15/20 idées + 0/20 partenaires + 10/20 période + 50/100 temps => +20/20
Noter que tout est hérité et compris par un (seul?) petit cerveau humain, et non d'un énorme datacenter qui a scrappé tout Internet.

Crédits : MOA
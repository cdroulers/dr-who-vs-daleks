# -*- encoding: utf-8 -*-
# Programme par Xtian Droulers et Pie-Hoes Leclapi
# Version 0.1 d�but� le 5 septembre 2006
# version 1.0 pr�te le 15 septembre 2006
# version 1.1 pr�te le 19 septembre 2006, voir "Docs/About.txt" pour les d�tails.

from Tkinter import *
import random
import winsound
from time import sleep
#from win32api import ShellExecute
import thread

class Controleur:
    # constructeur, cr�ation des variables de la partie
    def __init__(self):
        self.isZapping = False
        self.difficulte = "normal"
        self.root = Tk()
        self.aireDeJeu = AireDeJeu(self)
        self.vue = Vue(self)
        self.newGame()

    # si on clique sur File -> Exit
    def quit(self):
        self.root.quit()

    # appeller � chaque tour, pour voir si Dr. Who est mort, et effectuer les bonnes actions
    def isGameOver(self):
        if self.aireDeJeu.doc.isAlive:
            return False
        else:
            return True

    # probablement inutile :| # fonctions appell�es par le mod�le pour dessiner le Dr et les daleks
    def drawDrWho(self, doc):
        pass
    def drawDalek(self, dal):
        pass

    # pour passer de la vue � docWho
    def clickedCloseToDrWho(self, x, y):
        return self.aireDeJeu.doc.isClose(x, y)

    # pour retourner la position du doc � la vue
    def getPosDoc(self):
        return self.aireDeJeu.doc.posX, self.aireDeJeu.doc.posY

    # pour runner jusqu'� la fin de la ronde
    def run(self):
        while not self.isGameOver() and not self.isRoundOver():
            self.afterMove()
        # puis, on regarde si la ronde est termin�e i.e. tous les daleks sont morts.
        if self.isRoundOver():
            self.nextRound()

    # runner jusqu'� moins un
    def runMoinsUn(self):
        # si runMoinsUn retourne True, on peut continuer, si self.isRoundOver est False, on peut continuer
        while not self.isGameOver() and self.aireDeJeu.runMoinsUn() and not self.isRoundOver():
            self.afterMove()
        # puis, on regarde si la ronde est termin�e i.e. tous les daleks sont morts.
        if self.isRoundOver():
            self.nextRound()

    # teleporter Dr. Who
    def teleport(self):
        if not self.isGameOver():
            self.aireDeJeu.doc.teleport()
            self.afterMove()
            self.vue.playWav("Sounds/Teleportation.wav")
            # puis, on regarde si la ronde est termin�e i.e. tous les daleks sont morts.
            if self.isRoundOver():
                self.nextRound()

    # zapper autour de Dr. Who
    def zap(self):
        if not self.isGameOver() and not self.isZapping and self.aireDeJeu.doc.zap():
            self.isZapping = True
            self.vue.zap(self.aireDeJeu.doc.posX, self.aireDeJeu.doc.posY)
            self.afterMove()
            self.isZapping = False
            # puis, on regarde si la ronde est termin�e i.e. tous les daleks sont morts.
            if self.isRoundOver():
                self.nextRound()


    # apr�s un mouvement ou un zap ou un teleport, fait les v�rifications de GameOver et f�raille
    def afterMove(self):
        # on fait bouger tous les daleks
        for i in self.aireDeJeu.listeDaleks:
            x, y = i.findMove()
            i.move(x, y)
        # ensuite, on v�rifie s'il y a eu collision et si le doc est mort.
        self.aireDeJeu.verifierCollision()

        # si le doc est en vie, on continue � jouer
        if self.aireDeJeu.verifierVieDrWho():
            self.vue.updateBar("Ronde: " + str(self.aireDeJeu.ronde) + " ---- Cr�dits: " + str(self.aireDeJeu.doc.credits) + " --- Zaps: " + str(self.aireDeJeu.doc.nbZaps))

            # on update le canevas
            self.updateAireDeJeu()

    # bouger dr. Who
    def moveDrWho(self, x, y):
        if not self.isZapping:
            posX = self.aireDeJeu.doc.posX
            posY = self.aireDeJeu.doc.posY
            if self.aireDeJeu.doc.move(x, y):
                self.afterMove()
                # puis, on regarde si la ronde est termin�e i.e. tous les daleks sont morts.
                if self.isRoundOver():
                    self.nextRound()
            else:
                self.afficherMessage("Mouvement invalide")

    # bouger les dalek (INUTILE!!!!!)
    def moveDalek(self):
        pass

    # faire disparaitre Dr.Who
    def killDrWho(self):
        self.aireDeJeu.killDrWho()
        self.vue.playWav("Sounds/DocMort.wav")

    # faire disparaitre un Dalek (INUTILE!!! parce que l'aireDeJeu traite les collisions!)
    def killDalek(self, dalek):
        self.aireDeJeu.killDalek(dalek)

    # faire une nouvelle partie
    def newGame(self):
        if not self.isZapping:
            self.vue.newGame()
            if self.difficulte == "easy":
                nbDaleks, nbZaps, nbCredits, dim = 3, 3, 3, 30
            elif self.difficulte == "normal":
                nbDaleks, nbZaps, nbCredits, dim = 5, 1, 5, 30
            elif self.difficulte == "hard":
                nbDaleks, nbZaps, nbCredits, dim = 10, 1, 10, 30

            self.aireDeJeu = AireDeJeu(self, nbDaleks, nbZaps, nbCredits, dim)
            self.updateAireDeJeu()
            self.vue.updateBar("D�but de la partie! Ronde: " + str(self.aireDeJeu.ronde) + " ---- Cr�dits: " + str(self.aireDeJeu.doc.credits) + " --- Zaps: " + str(self.aireDeJeu.doc.nbZaps))

    # si la partie est termin�e
    def gameOver(self):
        self.killDrWho()
        self.vue.gameOver(self.aireDeJeu.doc.credits)

    # passer � la ronde suivante
    def nextRound(self):
        self.aireDeJeu.nextRound()
        self.vue.updateBar("Ronde: " + str(self.aireDeJeu.ronde))
        self.updateAireDeJeu()

    # pour savoir si tous les daleks sont morts
    def isRoundOver(self):
        return self.aireDeJeu.isRoundOver()

    # afficher la nouvelle aire de jeu
    def updateAireDeJeu(self):
        self.vue.update()

    # �crire un message sur la status bar
    def afficherMessage(self, texte):
        self.vue.updateBar(texte + " --- Ronde: " + str(self.aireDeJeu.ronde) + " ---- Cr�dits: " + str(self.aireDeJeu.doc.credits) + " --- Zaps: " + str(self.aireDeJeu.doc.nbZaps))

    # lire les score avec la calsse DB()
    def readScore(self):
        return DB().readScore()

    # lire le texte d'un fichier avec DB()
    def getText(self, filePath):
        return DB().getText(filePath)

    # �crier le score et le nom dans le fichier
    def writeNom(self, nom):
        DB().writeScore(nom, self.aireDeJeu.doc.credits)



# classe de partie
class AireDeJeu:
    def __init__(self, controleur = None, nbDaleksDePlus = 5, nbZapsDePlus = 1, nbCreditsParDalek = 5, dimension = 30, ronde = 1):
        self.controleur = controleur
        self.dimension = dimension
        self.ronde = ronde
        self.nbDaleksDePlus = nbDaleksDePlus
        self.nbZapsDePlus = nbZapsDePlus
        self.nbCreditsParDalek = nbCreditsParDalek
        self.doc = DrWho(self, nbZapsDePlus)
        self.listeDaleks = self.initialiserDaleks()

    # supprimer un dalek de la liste car il a �t� zapp�
    def deleteDalek(self, leDalekCon):
        for i in range(len(self.listeDaleks)):
            if self.listeDaleks[i].numero == leDalekCon.numero:
                del self.listeDaleks[i]
                break
        # si zap tous, fin de la ronde (inutile, on l'appellait 2 fois
        #if len(self.listeDaleks) == 0:
        #    self.controleur.nextRound()

    # v�rifier s'il y a eu des collision
    def verifierCollision(self):
        for i in self.listeDaleks:
            if i.isAlive and i.isOverOtherDalek():
                    self.doc.giveCredits()
                    self.killDalek(i)

    # v�rifier s'il y eu collision avec le Doc Who
    def verifierVieDrWho(self):
        for i in self.listeDaleks:
            if i.isOverDrWho(self.doc.posX, self.doc.posY):
                self.deleteDalek(i)
                self.controleur.gameOver()
                return False
        return True

    # v�rifier si un dalek est proche pour le run - 1
    def runMoinsUn(self):
        for i in self.listeDaleks:
            if self.doc.isClose(i.posX, i.posY):
                return False
        return True

    # tuer le doc
    def killDrWho(self):
        self.doc.die()

    # rendre un Dalek mort
    def killDalek(self, unDalekCon):
        for i in range(len(self.listeDaleks)):
            if self.listeDaleks[i].numero == unDalekCon.numero:
                self.listeDaleks[i].dieNormal()
                self.controleur.vue.playWav("Sounds/DalekMort.wav")

    # fonction r�initialisant les rondes
    def nextRound(self):
        self.ronde += 1
        self.listeDaleks = self.initialiserDaleks()
        self.doc.ajouterZap()
        self.doc.generatePos()

    # fonction qui cr�e les daleks n�c�ssaire � la ronde
    def initialiserDaleks(self):
        liste = []
        for i in range(self.ronde * self.nbDaleksDePlus):
            liste.append(Dalek(self, i))

        return liste

    # fonction qui check si tous les daleks sont morts
    def isRoundOver(self):
        for i in self.listeDaleks:
            if i.isAlive:
                return False

        return True



# classe du Dr. Who
class DrWho:
    def __init__(self, aireDeJeu, zaps):
        self.aireDeJeu = aireDeJeu
        self.isAlive = True
        self.nbZaps = zaps
        self.credits = 0
        self.generatePos()

    # pour zapper
    def zap(self):
        if self.nbZaps > 0:
            liste = []
            for i in self.aireDeJeu.listeDaleks:
                if i.isZapped():
                    liste.append(i)
            for i in liste:
                i.dieZap()
                self.aireDeJeu.controleur.vue.playWav("Sounds/DalekMort.wav")
            self.enleverZap()
            return True
        else:
            self.aireDeJeu.controleur.afficherMessage("Vous n'avez plus de zaps.")

    # nouvelle ronde = nouvelle position
    def generatePos(self):
        self.posX = random.randint(0, self.aireDeJeu.dimension - 1)
        self.posY = random.randint(0, self.aireDeJeu.dimension - 1)

    # voir si quelque chose (Dalek ou click) est proche de docWho (utile pour is Zapped et run -1)
    def isClose(self, posX, posY):
        if posX+1 == self.posX and posY+1 == self.posY:
            return True
        elif posX+1 == self.posX and posY == self.posY:
            return True
        elif posX+1 == self.posX and posY-1 == self.posY:
            return True
        elif posX == self.posX and posY-1 == self.posY:
            return True
        elif posX == self.posX and posY+1 == self.posY:
            return True
        elif posX-1 == self.posX and posY+1 == self.posY:
            return True
        elif posX-1 == self.posX and posY == self.posY:
            return True
        elif posX-1 == self.posX and posY-1 == self.posY:
            return True
        elif posX == self.posX and posY == self.posY:
            return True
        else:
            return False

    # quand le doc tue un dalek, il re�oit des cr�dits
    def giveCredits(self):
        self.credits += self.aireDeJeu.nbCreditsParDalek

    # pour voir si le doc move, j'ai fait une autre fonction, car elle faisait trop de chose dans le m�me if
    def canMove(self, x, y):
        if self.posX + x < 0 or self.posX + x > self.aireDeJeu.dimension -1 or self.posY + y < 0 or self.posY + y > self.aireDeJeu.dimension - 1:
            return False
        for i in self.aireDeJeu.listeDaleks:
            if i.isAlive == False and i.isOverDrWho(self.posX + x, self.posY + y):
                return False
        return True

    # pour bouger
    def move(self, x, y):
        if self.canMove(x, y):
            self.posX += x
            self.posY += y
            return True
        else:
            return False

    # pour ajouter un zap
    def ajouterZap(self):
        self.nbZaps += self.aireDeJeu.nbZapsDePlus

    # pour enlever un zap
    def enleverZap(self):
        self.nbZaps -= 1

    # quand il meurt!
    def die(self):
        self.isAlive = False

    # teleporter un peu partout
    def teleport(self):
        self.posX = random.randint(0, self.aireDeJeu.dimension - 1)
        self.posY = random.randint(0, self.aireDeJeu.dimension - 1)

    # se dessiner sur le canevas par le controleur (inutile aussi)
    def draw(self):
        self.aireDeJeu.controleur.drawDrWho(self)



class Dalek:
    def __init__(self, aireDeJeu, no):
        self.isAlive = True
        self.aireDeJeu = aireDeJeu
        self.numero = no
        self.posX = random.randint(0, self.aireDeJeu.dimension - 1)
        self.posY = random.randint(0, self.aireDeJeu.dimension - 1)
        docX = self.aireDeJeu.doc.posX
        docY = self.aireDeJeu.doc.posY
        while docX == self.posX and docY == self.posY:
            self.posX = random.randint(0, self.aireDeJeu.dimension - 1)
            self.posY = random.randint(0, self.aireDeJeu.dimension - 1)

    # se dessiner par le controleur (inutile aussi)
    def draw(self):
        self.aireDeJeu.controleur.drawDalek(self)

    # bouger le dalek
    def move(self, x, y):
        self.posX += x
        self.posY += y

    # pour trouver un move � faire
    def findMove(self):
        if self.isAlive:
            if self.aireDeJeu.doc.posX - self.posX > 0:
                reX = 1
            elif self.aireDeJeu.doc.posX - self.posX < 0:
                reX = -1
            else:
                reX = 0
            if self.aireDeJeu.doc.posY - self.posY > 0:
                reY = 1
            elif self.aireDeJeu.doc.posY - self.posY < 0:
                reY = -1
            else:
                reY = 0
            return reX, reY
        else:
            return 0, 0

    # mourir d'un zap, donc, supprimer de la liste
    def dieZap(self):
        self.aireDeJeu.deleteDalek(self)

    # mourir d'une collision, laisser un tas de feraille
    def dieNormal(self):
        self.isAlive = False

    #  voir s'il se fait zapper en v�rifiant s'il est proche de Dr. Who
    def isZapped(self):
        return self.aireDeJeu.doc.isClose(self.posX, self.posY)


    # voir s'il est par-dessus un autre Dalek, c'est-�-dire qu'il y a collision
    def isOverOtherDalek(self):
        for i in self.aireDeJeu.listeDaleks:
            if i.numero != self.numero:
                if self.posX == i.posX and self.posY == i.posY:
                    return True

        return False

    # coir s'il est par-dessus le doc Who les param�tres sont la positions du Doc!
    def isOverDrWho(self, x, y):
        if self.posX == x and self.posY == y:
            return True
        else:
            return False


class Vue:
    def __init__(self, controleur):
        self.controleur = controleur
        self.grandeurGrid = 30
        self.isPlayingMusic = False
        self.wantsGrid = True
        self.imageDrWho = PhotoImage(file="Icones/Doc.gif")
        self.imageDeadDrWho = PhotoImage(file="Icones/DocMort.gif")
        self.imageDalek = PhotoImage(file="Icones/Dalek.gif")
        self.imageTas = PhotoImage(file="Icones/DalekMort.gif")
        self.imageYellowZap = PhotoImage(file="Icones/YellowZap.gif")
        self.imageBlueZap = PhotoImage(file="Icones/BlueZap.gif")
        self.imageGameOver = PhotoImage(file="Icones/GameOver.gif")
        self.imageInstructions = PhotoImage(file="Icones/Numpad.gif")
        self.creerWidgets()

    # cr�er les widgets et la fenetre
    def creerWidgets(self):
        self.controleur.root.title("Dr. Who vs. Daleks!!!")
        self.controleur.root.wm_iconbitmap("Icones/LMAOSoft.ico")
        # cr�er le menubar
        self.menubar = Menu(self.controleur.root)
        # menu fichier
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Nouvelle partie", command=self.controleur.newGame)
        self.filemenu.add_command(label="Meilleurs scores", command=self.afficherScores)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Fermer", command=self.controleur.quit)
        self.menubar.add_cascade(label="Fichier", menu=self.filemenu)

        # menu options
        self.optionmenu = Menu(self.menubar, tearoff=0)
        self.optionmenu.add_command(label="Toggler la grid", command=self.toggleGrid)
        self.menubar.add_cascade(label="Options", menu=self.optionmenu)

        #menu difficult�
        self.difficultymenu = Menu(self.menubar, tearoff=0)
        self.difficultymenu.insert_radiobutton(1, label="Facile", command=self.clickEasy)
        self.difficultymenu.insert_radiobutton(2, label="Normal", command=self.clickNormal)
        self.difficultymenu.insert_radiobutton(3, label="Difficile", command=self.clickHard)
        self.menubar.add_cascade(label="Difficult�", menu=self.difficultymenu)

        # menu help
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="Instructions", command=self.afficherInstructions)
        self.helpmenu.add_separator()
        self.helpmenu.add_command(label="� propos", command=self.afficherAPropos)
        self.menubar.add_cascade(label="Aide", menu=self.helpmenu)
        # ajout du menu � root
        self.controleur.root.config(menu=self.menubar)


        # la status bar
        self.status = Label(self.controleur.root, bd=1, relief=SUNKEN, anchor=W)
        self.btnZap = Button(self.controleur.root, text="Zapper", command=self.hitZ)
        self.btnTeleport = Button(self.controleur.root, text="T�l�porter", command=self.hitT)
        self.btnRun = Button(self.controleur.root, text="Runner", command=self.hitRun)
        self.btnRunMoinsUn = Button(self.controleur.root, text="Runner moins un", command=self.hitRunMoinsUn)

        # le canevas
        self.canevas = Canvas(self.controleur.root, width=self.controleur.aireDeJeu.dimension*self.grandeurGrid, height=self.controleur.aireDeJeu.dimension*self.grandeurGrid, bg="white")

        # BINDING DES RACCOURCIS!
        self.controleur.root.bind("<F1>", self.hitF1)
        self.controleur.root.bind("<F2>", self.hitF2)
        self.controleur.root.bind("<F12>", self.hitF12)

        # gridage final
        self.btnZap.grid(row=0, column=0)
        self.btnTeleport.grid(row=0, column=1)
        self.btnRun.grid(row=0, column=2)
        self.btnRunMoinsUn.grid(row=0, column=3)
        self.canevas.grid(columnspan=4)
        self.status.grid(columnspan=4, sticky=W+E)
        self.status.config(text="Aller dans Fichier -> Nouvelle partie pour d�buter.")


    # changer le texte de la statusbar
    def updateBar(self, texte):
        self.status.config(text=texte)

    # changer la grilel qui apparait ou pas
    def toggleGrid(self, *args):
        if self.wantsGrid:
            self.wantsGrid = False
        else:
            self.wantsGrid = True
        self.update()

    # dessiner le doc sur le canevas
    def drawDrWho(self):
        x = self.controleur.aireDeJeu.doc.posX
        y = self.controleur.aireDeJeu.doc.posY
        if self.controleur.aireDeJeu.doc.isAlive:
            photo = self.imageDrWho
        else:
            photo = self.imageDeadDrWho
        self.canevas.create_image(x * self.grandeurGrid + self.grandeurGrid / 2, y * self.grandeurGrid + self.grandeurGrid / 2, image=photo)

    # dessiner un dalek
    def drawDaleks(self):
        for i in self.controleur.aireDeJeu.listeDaleks:
            if i.isAlive:
                photo = self.imageDalek
            else:
                photo = self.imageTas
            self.canevas.create_image(i.posX * self.grandeurGrid + self.grandeurGrid / 2, i.posY * self.grandeurGrid + self.grandeurGrid / 2, image=photo)

    # fonction en callback sur le frame pour F1
    def hitF1(self, event):
        self.afficherInstructions()
    # fonction en callback sur le frame pour F2
    def hitF2(self, event):
        self.controleur.newGame()

    # fonction en callback sur le frame pour F10
    def hitF12(self, event):
        self.afficherAPropos()

    # fonction en callback sur le frame pour les mouvements et les actions
    def hitKey(self, event):
        key = event.char
        if key == "1":
            self.controleur.moveDrWho(-1, 1)
        elif key == "2":
            self.controleur.moveDrWho(0, 1)
        elif key == "3":
            self.controleur.moveDrWho(1, 1)
        elif key == "4":
            self.controleur.moveDrWho(-1, 0)
        elif key == "5":
            self.controleur.moveDrWho(0, 0)
        elif key == "6":
            self.controleur.moveDrWho(1, 0)
        elif key == "7":
            self.controleur.moveDrWho(-1, -1)
        elif key == "8":
            self.controleur.moveDrWho(0, -1)
        elif key == "9":
            self.controleur.moveDrWho(1, -1)
        elif key == "+":
            self.controleur.run()
        elif key == "-":
            self.controleur.runMoinsUn()

    # fonction en callback sur le canevas pour les clicks de souris
    def click(self, event):
        x, y =  event.x / self.grandeurGrid,  event.y / self.grandeurGrid
        if self.controleur.clickedCloseToDrWho(x, y):
            docX, docY = self.controleur.getPosDoc()
            self.controleur.moveDrWho(x - docX, y - docY)
        else:
            self.controleur.teleport()

    # fonctions pour le settage des difficult�s
    def clickEasy(self):
        self.controleur.difficulte = "easy"
    def clickNormal(self):
        self.controleur.difficulte = "normal"
    def clickHard(self):
        self.controleur.difficulte = "hard"

    # fonction en callback sur le root pour le teleport
    def hitT(self, *args):
        self.controleur.teleport()

    # fonction en callback sur le root pour le zap
    def hitZ(self, *args):
        self.controleur.zap()

    # fonction pour le bouton run
    def hitRun(self):
        self.controleur.run()

    # fonction pour le bouton run moins un
    def hitRunMoinsUn(self):
        self.controleur.runMoinsUn()

    # fonction qui flash les lumi�res
    def zap(self, x, y):
        g = self.grandeurGrid
        self.playWav("Sounds/Zap.wav")
        for i in range(3):
            self.zappityZap(x+1, y+1, g)
            self.zappityZap(x+1, y, g)
            self.zappityZap(x+1, y-1, g)
            self.zappityZap(x-1, y+1, g)
            self.zappityZap(x-1, y, g)
            self.zappityZap(x-1, y-1, g)
            self.zappityZap(x, y+1, g)
            self.zappityZap(x, y-1, g)
        self.update()

    # fonction qui zappe un seul carr�
    def zappityZap(self, x, y, g):
        #self.canevas.create_rectangle(x * g, y * g, x * g + g, y * g + g, fill="blue")
        self.canevas.create_image(x * g + g / 2, y * g + g / 2, image=self.imageBlueZap)
        sleep(0.01)
        self.canevas.update()
        #self.canevas.create_rectangle(x * g, y * g, x * g + g, y * g + g, fill="yellow")
        self.canevas.create_image(x * g + g / 2, y * g + g / 2, image=self.imageYellowZap)
        sleep(0.01)
        self.canevas.update()

    # fonction pour afficher la grille sur le canevas
    def drawGrid(self):
        grandeur = self.controleur.aireDeJeu.dimension
        for i in range(self.controleur.aireDeJeu.dimension):
            self.canevas.create_line(0, i*self.grandeurGrid, grandeur*self.grandeurGrid, i*self.grandeurGrid)
            self.canevas.create_line(i*self.grandeurGrid, 0, i*self.grandeurGrid, grandeur*self.grandeurGrid)

    # updater le canevas
    def update(self):
        self.canevas.delete(ALL)
        if self.wantsGrid:
            self.drawGrid()
        self.drawDrWho()
        self.drawDaleks()
        self.canevas.update()

    # d�but de la partie, faire tous les bind n�cessaire
    def newGame(self):
        if not self.isPlayingMusic:
            self.playMid("Sounds/BackgroundMusic.mid")
        #winsound.PlaySound("Sounds/TestMusic.wav", winsound.SND_ASYNC + winsound.SND_LOOP)
        self.canevas.config(bg="white")
        # pour les touches du clavier num�rique
        self.controleur.root.bind("<Key>", self.hitKey)

        # pour le teleport et le zap
        self.controleur.root.bind("<t>", self.hitT)
        self.controleur.root.bind("<z>", self.hitZ)
        self.controleur.root.bind("<0>", self.hitT)
        self.controleur.root.bind("<.>", self.hitZ)
        self.controleur.root.bind("<g>", self.toggleGrid)
        # pour la souris
        self.canevas.bind("<Button-1>", self.click) #mouvement du doc plus teleport
        self.canevas.bind("<Button-3>", self.hitZ) # zapper

    # si la partie finit, il faut enlever le bind sur les fl�ches et la souris "TROUVER LE BON UNBIND!
    def gameOver(self, credits):

        self.canevas.config(bg="yellow")
        self.controleur.root.unbind("<k>")
        self.controleur.root.unbind("<t>")
        self.controleur.root.unbind("<g>")
        self.controleur.root.unbind("<Key>")
        self.controleur.root.unbind("<0>")
        self.controleur.root.unbind("<.>")
        self.canevas.unbind("<Button-1>")
        self.canevas.unbind("<Button-3>")
        self.updateBar("FIN DE LA PARTIE!!!!! Vous avez fait " + str(credits) + " cr�dits!!!")
        self.getNom()
        self.canevas.config(bg="gray")
        self.canevas.create_image(self.controleur.aireDeJeu.dimension * self.grandeurGrid / 2, self.controleur.aireDeJeu.dimension * self.grandeurGrid / 2, image=self.imageGameOver)
        self.canevas.update()

    # afficher les instructions
    def afficherInstructions(self):
        texte = self.controleur.getText("Docs/Instructions.txt")
        self.top = Toplevel(self.controleur.root)
        self.top.title("Instructions du jeu Dr.Who Vs. Daleks...")
        self.top.wm_iconbitmap("Icones/About.ico")

        self.top.lblImage = Label(self.top, image=self.imageInstructions)
        self.top.lblImage.grid()
        self.top.lblInstructions = Label(self.top, text=texte)
        self.top.lblInstructions.grid()
        Button(self.top, text="OK", command=self.top.destroy).grid()

    # afficher le About
    def afficherAPropos(self):
        texte = self.controleur.getText("Docs/About.txt")
        self.top = Toplevel(self.controleur.root)
        self.top.title("� propos du jeu Dr.Who Vs. Daleks...")
        self.top.wm_iconbitmap("Icones/LMAOSoft.ico")

        self.top.lblInstructions = Label(self.top, text=texte)
        self.top.lblInstructions.grid()
        Button(self.top, text="OK", command=self.top.destroy).grid()

    # afficher les high scores
    def afficherScores(self):
        listeScore = self.controleur.readScore()
        self.top = Toplevel(self.controleur.root)
        self.top.title("Les meilleurs scores")
        self.top.wm_iconbitmap("Icones/LMAOSoft.ico")
        for i in range(len(listeScore)):
            Label(self.top, text=str(listeScore[i][0]), width=50).grid(row=i, column=0)
            Label(self.top, text=str(listeScore[i][1]), width=50).grid(row=i, column=1)
        Button(self.top, text="OK", command=self.top.destroy).grid(columnspan=2, sticky=W+E)

    # demander un nom pour les high scores
    def getNom(self):
        self.top = Toplevel(self.controleur.root)
        self.top.title("Veuillez entrer votre nom")
        self.top.wm_iconbitmap("Icones/LMAOSoft.ico")
        Label(self.top, text="Nom:").grid(row=0, column=0)
        self.top.entryNom = Entry(self.top)
        self.top.entryNom.grid(row=0, column=1)
        self.top.btnOK = Button(self.top, text="OK", command=self.sendNom)
        self.top.btnOK.grid(row=1, columnspan=2, sticky=W+E)

    # d�truire le top et envoyer sese donn�es au controleur
    def sendNom(self):
        stringTempo = self.top.entryNom.get()
        self.top.destroy()
        self.controleur.writeNom(stringTempo)
        self.afficherScores()

    # jouer un son midi
    def playMid(self, filename):
        self.isPlayingMusic = True
        #ShellExecute(0, "open", filename, None, "", 0)

    # jouer un son wav
    def playWav(self, filename):
        winsound.PlaySound(filename, winsound.SND_ASYNC)


class DB:
    def writeScore(self, name, score):
        fichier = file("Saves/HighScores.txt", "a")
        fichier.write("\n" + str(name) + "," + str(score))
        fichier.close()

    def readScore(self):
        fichier = file("Saves/HighScores.txt")
        tempo = fichier.read()
        fichier.close()
        tempo = tempo.split("\n")
        for i in range(len(tempo)):
            tempo[i] = tempo[i].split(",")
        return tempo

    def getText(self, filePath):
        fichier = file(filePath)
        tempo = fichier.read()
        fichier.close()
        return tempo


# fonction main du fichier
if __name__ == "__main__":
    c = Controleur()
    print "LOL LIMEWIRE"
    print "PIRATONS LES LANGUES!!!! C'EST COMME DES OCEN MAIS PAS DE O LOL!"
    c.root.mainloop()





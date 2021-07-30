import math
import copy
import os
import time

# informatii despre un nod din arborele de parcurgere (nu din graful initial)
import sys


class NodParcurgere:
    gr = None  # trebuie setat sa contina instanta problemei

    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.g = cost
        self.h = h
        self.f = self.g + self.h
        # posibil sa mai am de adaugat informatii


    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(
            self, f
    ):
        l = self.obtineDrum()
        for nod in l:
            f.write(str(nod))
        f.write("Cost: {}\n".format(self.g))
        f.write("Lungime: {}\n".format(len(l)))

    def afisDrum1(self):
        l = self.obtineDrum()
        for nod in l:
            print(str(nod))
        print(self.g)
        print(len(l))


    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte

        return False


    def __repr__(self):
        sir = ""
        for linie in self.info:
            sir += " ".join(linie) + "\n"
        return sir


    def __str__(self):
        sir = ""
        for linie in self.info:
            sir += linie[0] + "\n"
        sir+="\n"
        return sir


class Graph:  # graful problemei
    def __init__(self, nume_fisier):

        # citire fisier

        f = open(nume_fisier, "r")
        textFisier = f.readlines()

        self.start = []
        self.scopuri = []

        linieSep = textFisier.index('\n')
        for i in range(0, linieSep):
            self.start.append([textFisier[i].strip('\n')])

        for i in range(linieSep + 1, len(textFisier)):
            self.scopuri.append([textFisier[i].strip('\n')])

        f.close()


    def checkInput(self):
        # verificare erori input

        inputStart = set()
        inputFinal = set()

        for element in self.start:
            for el in element:
                inputStart = inputStart.union(el)

        for element in self.scopuri:
            for el in element:
                inputFinal = inputFinal.union(el)

        #verific daca in starea finala am simboluri care nu sunt prezente in start
        diff = inputFinal.difference(inputStart)
        if diff:
            return False

        #verific daca matricea finala are un nr de linii/coloane mai mare decat matricea initiala (nu se poate realiza decuparea)
        if (len(self.scopuri) > len(self.start)) or (len(self.scopuri[0][0]) > len(self.start[0][0])):
            return False

        return True

    # generez perechi (index_start,linii/coloane de taiat)
    def combina(self, nr_curent, nr_de_taiat):
        '''

        :param nr_curent: nr actual de linii/coloane pentru care generez combinatii (indice start,nr de taiat)
        :param nr_de_taiat: cate linii/coloane trebuie sa decupez
        :return: tuplu de forma (indice start decupare, nr de elemente taiate)
        '''
        combinari = []
        for i in range(nr_curent):
            j = 1
            while j <= nr_de_taiat and i + j <= nr_curent:
                combinari.append((i, j))
                j += 1

        return combinari

    # functie ce returneaza noul grid dupa taierea a nr_de taiat linii
    def taiere_linii(self, index_linie, nr_de_taiat, grid):
        '''

        :param index_linie: indexul liniei de unde incep sa decupez
        :param nr_de_taiat: nr de linii pe care le tai
        :param grid: grid-ul din care decupez
        :return: noul grid, dupa taierea liniilor
        '''
        grid_nou = []
        for i in range(0, index_linie + 1):
            grid_nou.append(grid[i])
        for i in range(index_linie + nr_de_taiat, len(grid)):
            grid_nou.append(grid[i])

        # poate ar fi ok sa returnez si costul (?)
        return grid_nou

    def taiere_coloane(self, index_coloana, nr_de_taiat, grid):
        '''

        :param index_coloana: indexul de unde incep sa decupez
        :param nr_de_taiat: nr de coloane pe care trebuie sa le decupez
        :param grid: grid-ul din care tai
        :return: noul grid, dupa decuparea coloanelor
        '''
        grid_nou = []
        coloane = len(grid[0][0])
        for i in range(0, len(grid)):
            grid_nou.append([grid[i][0][:index_coloana] + grid[i][0][index_coloana + nr_de_taiat:]])

        return grid_nou

    def testeaza_scop(self, nodCurent):
        return nodCurent.info == self.scopuri

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        '''

        :param nodCurent:
        :param tip_euristica:
        :return:
        '''
        listaSuccesori = []
        linii_de_taiat = len(self.start) - len(self.scopuri) + 1
        # print("Linii de taiat",linii_de_taiat)
        # print(nodCurent.info)

        coloane_de_taiat = len(self.start[0][0]) - len(self.scopuri[0][0]) + 1
        # print("coloane de taiat",coloane_de_taiat)

        # taiem linii
        # print(self.combina(len(nodCurent.info), linii_de_taiat))
        # print(len(nodCurent.info))
        for index_linie, linii_de_taiat in self.combina(len(nodCurent.info), linii_de_taiat):
            grid_nou = self.taiere_linii(index_linie, linii_de_taiat, nodCurent.info)
            # print(grid_nou)
            # print("nod curent",nodCurent.info)
            cost_taiere = len(nodCurent.info[0][0]) / linii_de_taiat  #din enunt stim: costul taierii liniilor = nr coloane taiate/ nr linii

            #in acest caz, am taiat prea mult
            if len(grid_nou) < len(self.scopuri):
                continue

            nodNou = NodParcurgere(grid_nou, nodCurent, nodCurent.g + cost_taiere,
                                   self.calculeaza_h(grid_nou, tip_euristica))

            if not nodCurent.contineInDrum(grid_nou):
                listaSuccesori.append(nodNou)

        # taiem coloane
        # print(self.combina(len(nodCurent.info[0][0]), coloane_de_taiat))
        try:
            for index_coloana, coloane_de_taiat in self.combina(len(nodCurent.info[0][0]), coloane_de_taiat):
                grid_actual = nodCurent.info
                grid_nou = self.taiere_coloane(index_coloana, coloane_de_taiat, nodCurent.info)

                #   print(grid_nou)
                # calculez costul pentru taiere
                cost_taiere = 0

                for j in range(index_coloana, index_coloana + coloane_de_taiat):
                    for i in range(len(grid_actual)):  # verific in dreapta si in jos
                        if j + 1 < index_coloana + coloane_de_taiat:
                            if grid_actual[i][0][j] != grid_actual[i][0][j + 1]:  #verific vecinii diferiti pe coloana
                                cost_taiere += 1

                        if i + 1 < len(grid_actual):
                            if grid_actual[i][0][j] != grid_actual[i + 1][0][j]:  #verificare vecini diferiti pe linie
                                cost_taiere += 1

                cost_taiere = 1 + cost_taiere / coloane_de_taiat  #costul din enunt

                # nodNou = NodParcurgere(grid_nou, nodCurent, cost=nodCurent.g + cost_taiere,
                #                        h=self.calculeaza_h(grid_nou, tip_euristica))

                if not nodCurent.contineInDrum(grid_nou):
                    listaSuccesori.append(NodParcurgere(grid_nou, nodCurent, nodCurent.g + cost_taiere,
                                                        self.calculeaza_h(grid_nou, tip_euristica)))
        except:
            pass

        return listaSuccesori

    def calculeaza_h(self, infoNod, tip_euristica="euristica banala"):
        if tip_euristica == "euristica banala":
            if infoNod not in self.scopuri:
                return 1
            return 0
        #tin cont doar de numarul de coloane taiate
        elif tip_euristica == "euristica admisibila":
            if (len(infoNod[0][0]) != len(self.scopuri[0][0])):
                return 1
            else:
                return 0
        elif tip_euristica == "euristica inadmisibila":
            return len(self.start) - len(self.scopuri) + len(self.start[0][0]) - len(self.scopuri[0][0])
        return 1

    def _repr_(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir


def a_star(f, gr, nrSolutiiCautate, tip_euristica="euristica banala"):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)

    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    start = time.time()
    noduri_generate = 0
    nr_maxim_noduri = 0
    f.write("Solutii obtinute cu A*:\n")

    while len(c) > 0:
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            end = time.time()
            f.write("Solutie:\n")
            nodCurent.afisDrum(f)
            f.write("Timp gasire solutie: {} secunde\n".format(end - start))
            f.write("Numarul de noduri generate (succesori) {}\n".format(noduri_generate))
            f.write("Numarul maxim de noduri de la un moment dat din memorie: {}\n".format(nr_maxim_noduri))
            f.write("\n----------------\n")

            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)
        noduri_generate += len(lSuccesori)

        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].f >= s.f:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)

        if len(c) > nr_maxim_noduri:
            nr_maxim_noduri = len(c)


def uniform_cost(f,gr, nrSolutiiCautate, tip_euristica="euristica banala"):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)

    c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]

    f.write("Solutii obtinute cu UCS:\n")

    start = time.time()
    noduri_generate = 0
    nr_maxim_noduri = 0

    while len(c) > 0:
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            end = time.time()

            f.write("Solutie:\n")
            nodCurent.afisDrum(f)
            f.write("Timp gasire solutie {} secunde\n".format(end - start))
            f.write("Numarul de noduri generate (succesori) {}\n".format(noduri_generate))
            f.write("Numarul maxim de noduri de la un moment dat din memorie: {}\n".format(nr_maxim_noduri))
            f.write("\n----------------\n")

            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)
        noduri_generate += len(lSuccesori)

        for s in lSuccesori:
            # print(s)
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                # diferenta fata de UCS e ca ordonez dupa f
                if c[i].g >= s.g:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)
        if len(c) > nr_maxim_noduri:
            nr_maxim_noduri = len(c)


def a_star_optimizat(f,gr, nrSolutiiCautate=1, tip_euristica="euristica banala"):
    # in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
    l_open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))]


    start = time.time()
    noduri_generate = 0
    nr_maxim_noduri = 0

    # l_open contine nodurile candidate pentru expandare

    # l_closed contine nodurile expandate
    l_closed = []
    f.write("Solutii obtinute cu A* opt:\n")
    while len(l_open) > 0:
        # print("Coada actuala: " + str(l_open))
        nodCurent = l_open.pop(0)
        l_closed.append(nodCurent)

        if gr.testeaza_scop(nodCurent):
            end = time.time()
            f.write("Solutie:\n")
            nodCurent.afisDrum(f)
            f.write("Timp gasire solutie: {} secunde\n".format(end - start))
            f.write("Numarul de noduri generate (succesori) {}\n".format(noduri_generate))
            f.write("Numarul maxim de noduri de la un moment dat din memorie: {}\n".format(nr_maxim_noduri))
            f.write("\n----------------\n")
            return

        lSuccesori = gr.genereazaSuccesori(nodCurent)
        noduri_generate += len(lSuccesori)
        total = len(l_closed) + len(l_open) + len(lSuccesori)  # nr maxim de noduri la un moment dat in memorie
        if total > nr_maxim_noduri:
            nr_maxim_noduri = total

        for s in lSuccesori:
            gasitC = False
            for nodC in l_open:
                if s.info == nodC.info:
                    gasitC = True
                    if s.f >= nodC.f:
                        lSuccesori[:] = [x for x in lSuccesori if x != s]
                        # lSuccesori.remove(s)
                    else:  # s.f<nodC.f
                        l_open[:] = [x for x in l_open if x != nodC]
                        # l_open.remove(nodC)
            if not gasitC:
                for nodC in l_closed:
                    if s.info == nodC.info:
                        if s.f >= nodC.f:
                            lSuccesori[:] = [x for x in lSuccesori if x != s]
                            # lSuccesori.remove(s)
                        else:  # s.f<nodC.f
                            l_closed[:] = [x for x in l_closed if x != nodC]
                            # l_closed.remove(nodC)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(l_open)):
                # diferenta fata de UCS e ca ordonez crescator dupa f
                # daca f-urile sunt egale ordonez descrescator dupa g
                if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
                    gasit_loc = True
                    break
            if gasit_loc:
                l_open.insert(i, s)
            else:
                l_open.append(s)


def construieste_drum(f,gr, nodCurent, limita, nrSolutiiCautate=1):

    f. write("A ajuns la:\n" + str(nodCurent) +'\n')
    if nodCurent.f > limita:
        return nrSolutiiCautate, nodCurent.f
    if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
        f.write("Solutie: \n")
        nodCurent.afisDrum(f)
        f.write(str(limita))
        f.write("\n----------------\n")
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return 0, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent)
    minim = float('inf')
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(f,gr, s, limita, nrSolutiiCautate)
        if rez == "gata":
            return 0, "gata"
        f.write("Compara "+ str(rez) + " cu " + str(minim) +"\n")
        if rez < minim:
            minim = rez
            f.write("Noul minim: " +str(minim) + "\n")

    return nrSolutiiCautate, minim


def ida_star(f,gr, nrSolutiiCautate=1, tip_euristica="euristica banala"):
    nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start))
    limita = nodStart.f


    while True:

        f.write("Limita de pornire: "+ str(limita) + "\n")
        nrSolutiiCautate, rez = construieste_drum(f,gr, nodStart, limita, nrSolutiiCautate)
        f.write(str(rez) + "\n")
        if rez == "gata":
            break
        if rez == float('inf'):
            f.write("Nu exista solutii!")
            break
        limita = rez
        f.write(">>> Limita noua: " + str(limita) +"\n")



#partea de fisiere
if len(sys.argv) != 5:
    print("Numar invalid de argumente")
    exit(0)
else:
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    nsol = int(sys.argv[3])
    timeout = int(sys.argv[4])

if not os.path.exists(f"{output_path}"):
    os.mkdir(f"{output_path}")

try:
    listaFisiere = os.listdir(f"{input_path}")
except Exception as eroare:
    print("Path invalid")
    exit(0)

paths_output = []
for numeFisier in listaFisiere:
    numeFisierOutput = "output_" + numeFisier
    f = open(f"{output_path}/" + numeFisierOutput, "w")
    paths_output.append(f"{output_path}/" + numeFisierOutput)
    f.close()
for i in range(len(listaFisiere)):
    listaFisiere[i] = input_path + "/" + listaFisiere[i]

for i in range(len(listaFisiere)):
    gr = Graph(listaFisiere[i])
    if gr.checkInput() == True:
        f = open(paths_output[i],"w")
        a_star(f, gr, nrSolutiiCautate=nsol, tip_euristica="euristica banala")
        a_star_optimizat(f, gr, nrSolutiiCautate=nsol, tip_euristica="euristica  banala")
        uniform_cost(f, gr, nrSolutiiCautate=nsol, tip_euristica="euristica  banala")
        ida_star(f, gr, nrSolutiiCautate=1, tip_euristica="euristica  banala")
        f.close()
    else:
        f = open(paths_output[i],"w")
        f.write("Input invalid")
        f.close()



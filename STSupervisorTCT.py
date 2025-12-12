import math
import os

from PIL import Image
import matplotlib.pyplot as plt
import pitct as pytct
from graphviz import Digraph

user_route = "TCTX64_20210701/"  # Project route

## Common info for TCT files:
state_size = """State size (State set will be (0,1....,size-1)):     
# <-- Enter state size, in range 0 to 2000000, on line below."""
marker_state = "\n\n" + """Marker states:
# <-- Enter marker states, one per line.
# To mark ALL states, enter *.
# If no marker states, leave line blank.
# End marker list with blank line.
"""
vocal_state = """
Vocal states:
# <-- Enter vocal output states, one per line.
# Format: State  Vocal_Output.  Vocal_Output in range 10 to 99.
# Example: 0 10
# If no vocal states, leave line blank.
# End vocal list with blank line."""
transitions = "\n\n" + """Transitions:
# <-- Enter transition triple, one per line.
# Format: Exit_(Source)_State  Transition_Label  Entrance_(Target)_State.
# Transition_Label in range 0 to 9999.
# Example: 2 0 1 (for transition labeled 0 from state 2 to state 1)."""


class State:  # Automaton state structure
    def __init__(self, id):
        self.id = id
        self.active_events = []

    def __str__(self):
        return "id: " + str(self.id) + ", name: " + str(self.actuators)

    def add_active_event(self, event: str):  # Add active events
        try:
            self.active_events.append(event)
        except:
            print(event)
            print(self.id)

    def __repr__(self):
        # return "{ " + str(self.id) + " ," + str(self.actuators) + ", ev: " + str(self.active_events) + "}"
        return str(self.id)

    def get_active_events(self):  # Get active events
        return self.active_events

    def get_id(self):  # Get the state id
        return self.id


class Automata:  # Automaton structure
    def __init__(self, name: str):
        self.name = name
        self.c_events = []
        self.uc_events = []
        self.transitions = []
        self.states = []
        self.dict_events = dict([])
        self.dict_states = dict([])
        self.states_marked = []

    def __str__(self):
        return "name: " + str(self.name) + ", # states: " + str(len(self.states)) + ", # transitions: " + str(
            len(self.transitions))

    def add_state(self, number_of_states: int, names: list, marked: list):  # Add state in the automaton
        dif_mark = number_of_states - len(marked)
        if dif_mark > 0:
            for i in range(0, dif_mark):
                marked.append(False)
        for i in range(0, number_of_states):
            state = State(i)
            self.states.append(state)
            self.dict_states[names[i]] = i
            if marked[i]:
                self.states_marked.append(names[i])

    def add_transition(self, transitions: list, event: list, uncontrollable: list = [], uc_events: list = [],
                       c_events: list = [], dict_events: dict = [], dict_events_name: dict = []):
        # Add a transition in the automaton
        for i in range(0, len(event)):
            aux_event = event[i]
            aux_list = dict_events.keys()
            if event[i] not in self.uc_events and event[i] in uncontrollable:
                self.uc_events.append(event[i])
            if event[i] not in self.c_events and event[i] not in uncontrollable:
                self.c_events.append(event[i])

            if event[i] not in dict_events.keys():
                if event[i] in uncontrollable:
                    if event[i] not in uc_events:
                        uc_events.append(event[i])
                        id = 2 * (len(uc_events) - 1)
                        dict_events[event[i]] = str(id)
                        dict_events_name[str(id)] = event[i]
                else:
                    if event[i] not in c_events:
                        c_events.append(event[i])
                        id = 2 * (len(c_events) - 1) + 1
                        dict_events[event[i]] = str(id)
                        dict_events_name[str(id)] = event[i]

        for i in range(0, len(transitions)):
            aux = self.states[transitions[i][0]]
            eve = event[i]
            self.states[transitions[i][0]].add_active_event(event[i])
            self.transitions.append((transitions[i][0], int(dict_events.get(event[i])), transitions[i][1]))
        # print(self.transitions)
        # print(dict_events)


class process:
    def __init__(self, route):  # generate a closed enviorment to process related automata.
        self.automatas = dict([])
        self.dict_events = dict([])
        self.dict_events_name = dict([])
        self.dict_states = dict([])
        self.c_events = []
        self.uc_events = []
        pytct.init(route, overwrite=True)
        self.init = route + '\n' + 'CLOCK 0\n'
        self.route = route
        self.images_dir = os.path.join(self.route, "Images")
        os.makedirs(self.images_dir, exist_ok=True)


    def load_automata(self, names: list):  # Load the TCT synthesized automata
        for name in names:
            self.DES2TXT(name)
            self.aux_read_TXT(name)

    def DES2TXT(self, name):  # Load the TCT synthesized automata
        pytct.printdes(name, name)

    def get_automaton(self, name) -> Automata:  # Get a specfic automaton by its name
        return self.automatas[name]

    def print_events(self, actuators=[]):  # Print in console all events
        aux = list(map(int, self.dict_events.values()))
        aux.sort()
        aux = list(map(str, aux))
        if len(actuators) == 0:
            for n in aux:
                print(n + " -> " + self.dict_events_name[n])
        else:
            for n in aux:
                print(n + " -> " + self.dict_events_name[n] + " : " + actuators[self.dict_events_name[n]])

    def plot_automatas(self, nameList: list, numcolumns: int = 1,
                       show=True):  # Generate images of automata and plot them
        self.generate_image(nameList)
        num_filas = math.ceil(len(nameList) / numcolumns)
        if show:
            fig, axs = plt.subplots(num_filas, numcolumns, figsize=(15, 5 * num_filas))
            if len(nameList) == 1:
                axs = [axs]
            else:
                axs = axs.flatten()
            for i in range(len(nameList)):
                ruta = os.path.join(self.images_dir, f"{nameList[i]}.png")
                imagen = Image.open(ruta)
                # Mostrar la imagen
                axs[i].imshow(imagen)
                axs[i].axis('off')  # Ocultar los ejes
            plt.show()

    def generate_image(self, name_list: list):  # Generate image of autamaton list
        for name in name_list:
          self.aux_generate_image(name)

    # Función para ajustar el tamaño de la fuente basado en la longitud del label
    def adjust_fontsize(self, label):
        base_size = 12
        max_length = 20
        min_size = 8
        if len(label) > max_length:
            return str(max(min_size, base_size - (len(label) - max_length) // 2))
        return str(base_size)

    def aux_generate_image(self, name):  # Generate image for an automaton
        automaton = self.get_automaton(name)
        states = [str(state.get_id()) for state in automaton.states]
        transitions = []
        transition_labels = dict([])
        for start, label, end in automaton.transitions:
            key = (str(start), str(end))
            if key not in transitions:
                transitions.append(key)
            if key in transition_labels.keys():
                transition_labels[key] += ",\n " + self.dict_events_name[str(label)]
            else:
                transition_labels[key] = self.dict_events_name[str(label)]
        marked_states = [str(automaton.dict_states[key]) for key in automaton.states_marked]
        dot = Digraph()
        dot.attr(rankdir='LR', nodesep='0.3', ranksep='0.3', splines='true')
        for state in states:
            if state in marked_states:
                dot.node(state, shape='doublecircle', width='0.4', height='0.4', fixedsize='true')
            else:
                dot.node(state, shape='circle', width='0.5', height='0.5', fixedsize='true')
        for start, end in transitions:
            label = transition_labels.get((start, end), "")
            fontzise = self.adjust_fontsize(label)
            minlen = str(int(fontzise) // 6)
            dot.edge(start, end, label=label, fontsize=fontzise, constraint='true', minlen=minlen)  #
        # dot.render(self.route + "\\Images\\" + name, format='png', cleanup=True)
        output_path = os.path.join(self.images_dir, name)  # sin extensión
        dot.render(output_path, format='png', cleanup=True)

        return

    def complete_spec(self, name):  # For an automaton add all the self-loops of uncontrollable events
        for s in self.automatas[name].states:
            for e in self.automatas[name].uc_events:
                active_events = s.get_active_events()
                if e not in active_events:
                    self.add_transition(name, [(s.get_id(), s.get_id())], [e], [e])
                # print(s.get_id(),e)

    def add_self_events(self, name, events: list):  # Add a self loop  for each event in events in an automaton
        for e in events:
            self.add_self_event(name, e)

    def add_self_event(self, name, event, uncontrollable: bool = False):  # Add a self loop of one event in an automaton
        for s in self.automatas[name].states:
            active_events = s.get_active_events()
            if event not in active_events:
                if event not in self.c_events and event not in self.uc_events:
                    if uncontrollable:
                        self.add_transition(name, [(s.get_id(), s.get_id())], [event], [event])
                    else:
                        self.add_transition(name, [(s.get_id(), s.get_id())], [event], [])
                        return
                if event in self.uc_events:
                    self.add_transition(name, [(s.get_id(), s.get_id())], [event], [event])
                else:
                    self.add_transition(name, [(s.get_id(), s.get_id())], [event], [])

    def coordinator(self, supervisores, plantas):  # Returns if a pair of supervisors are nonconflicting
        TESTcoor = self.automata_syncronize(supervisores, "SUPt")
        planta = self.automata_syncronize(plantas, "plantaTotal")
        AEcoor = self.all_events(planta, 'AEcoor')
        noncoor = self.nonconflict(TESTcoor, AEcoor)
        return noncoor, TESTcoor, AEcoor

    def all_events(self, automata_name, alleventsname):  # Get the all events automaton from an automaton
        pytct.allevents(alleventsname, automata_name)
        return alleventsname

    def supreduce(self, plant, sup, sup_dat, simsup):  # returns the minimal proper supervisor
        pytct.supreduce(simsup, plant, sup, sup_dat)
        return simsup

    def condat(self, plant, sup, sup_dat):  # returns de .dat of a supervisor.
        pytct.condat(sup_dat, plant, sup)
        return sup_dat

    def supcon(self, plant, specifications, sup: str = ""):  # Synthetize the supervisor of a plant
        pytct.supcon(sup, plant, specifications)
        return sup

    def nonconflict(self, name_1, name_2):  # Returns if a pair of automata are conflicting
        return len(self.nonconflict_aux(name_1, [name_2])) == 0

    def nonconflict_aux(self, name, names: list):  # Find each conflicting supervisor in names with name
        conflicting = []
        for n in names:
            if not n == name:
                result = pytct.nonconflict(n, name)
                if not result:
                    conflicting.append((n))
        return conflicting

    def new_automaton(self, name: str):  # Generate a new automaton
        self.automatas[name] = Automata(name)
        return name

    def add_state(self, automaton_name: str, number_of_states: int, names: list,
                  marked: list):  # Define states of an empty automata
        if len(names) == 0:
            names = range(0, number_of_states)
            names = [str(numero) for numero in names]
        self.automatas[automaton_name].add_state(number_of_states, names, marked, )

    def add_transition(self, automaton_name: str, transitions: list, events: list, uncontrollable: list = []) -> object:
        # Add transitions to an automaton
        self.automatas[automaton_name].add_transition(transitions, events, uncontrollable, self.uc_events,
                                                      self.c_events,
                                                      self.dict_events, self.dict_events_name)

    def generate_all_automata(self):  # Generate all the automaton TCT files
        for name in self.automatas.keys():
            self.generate_automata(name)

    def generate_automata(self, name):  # Generate a TCT automaton file
        delta = []
        Qm = [self.automatas[name].dict_states[key] for key in self.automatas[name].states_marked]
        size = len(self.automatas[name].dict_states)
        for transition in self.automatas[name].transitions:
            delta.append((transition[0], transition[1], transition[2]))
        pytct.create(name, size, delta, Qm)
        return
        # Lista de comandos que deseas enviar

    def automata_syncronize(self, automata_names: list,
                            name_sync: str = ""):  # Syncronize the group of automata automata_names
        pytct.sync(name_sync, *automata_names)
        return name_sync

    def aux_read_TXT(self, name):  # Read TCT TXT files and charge the info in the process
        with open(self.route + "/" + name + ".TXT", "r") as archivo:
            marked = -1
            transitions = []
            uc_events = []
            events = []
            aux = 0
            for linea in archivo:
                if '# states: ' in linea:
                    aux = linea.split()
                    name = aux[0].strip()
                    # Normaliza separadores y quédate solo con el nombre base (sin ruta)
                    name = os.path.basename(name.replace("\\", "/"))
                    # (Opcional) si el nombre trae extensión, quítala:
                    name = os.path.splitext(name)[0]

                    num_state = int(aux[3])
                    self.new_automaton(name)
                if "marker" in linea and not 'none' in linea:
                    aux = 1
                    continue
                if aux == 1:
                    if "\n" == linea:
                        continue
                    marked = [int(x) for x in linea.split()]
                    self.add_state(name, num_state, [], [[x in marked for x in range(0, num_state)]])
                    aux = 2
                    continue
                if "[" not in linea:
                    continue
                if marked == -1:
                    self.add_state(name, num_state, [], [])
                    marked = 0
                aux_transitions = linea.replace(" ", "").replace("[", "").replace("\n", "").split("]")
                aux_transitions.pop()
                for transition in aux_transitions:
                    aux = transition.split(',')
                    transitions.append((int(aux[0]), int(aux[2])))
                    if aux[1] in self.dict_events_name.keys():
                        event = self.dict_events_name[aux[1]]
                    else:
                        event = aux[1]
                    if event not in events:
                        if int(aux[1]) % 2 == 0:
                            uc_events.append(event)
                    events.append(event)
        self.add_transition(name, transitions, events, uc_events)
        return name

    def aislated(self, aislated: list = [], actuators: list = [], interseccion=dict([])):
        # Generate ST code from Ailated supervisor and actuators.
        out = ""
        for a in aislated:
            add = ""
            if len(actuators[a[0]].split(':')) > 1:
                add = "NOT " if actuators[a[0]].split(':')[1] == 'OFF' else ''
            out += "\tIF NOT " + actuators[a[1]].split(':')[0] + " & " + add + actuators[a[0]].split(':')[
                0] + " THEN\n\t\t"
            out += actuators[a[1]].split(':')[0] + " := 1;\n"
            out += "\tELSIF " + actuators[a[1]].split(':')[0] + " & " + add + actuators[a[0]].split(':')[
                0] + " THEN\n\t\t"
            out += actuators[a[0]].split(':')[0] + " := 0;\n\t"
            if actuators[a[0]].split(':')[0] in interseccion.keys():
                out += "\t" + actuators[a[0]].split(':')[0] + "_G[0] := 0;\n"
            out += "END_IF;\n"
        return out

    def generate_ST_OPENPLC(self, supervisors: list, plants: list = [], actuators: dict = dict([]), namest='code_st',
                            Mask: dict = dict([]), Isolated: list = [], initial: str = "null"):
        # Generate the full ST code

        RANDOM = "FUNCTION_BLOCK random_number\n\tVAR_INPUT\n\t\tIN : BOOL;\n\tEND_VAR\n\tVAR\n\t\tM : BOOL;"
        RANDOM += "\n\t\tINIT : BOOL;\n\tEND_VAR\n\tVAR_OUTPUT\n\t\tOUT : DINT;\n\tEND_VAR\n"
        RANDOM += "\n\tIF NOT INIT THEN\n\t\t{#include <stdio.h>}\n\t\t{#include <stdlib.h>}\n\t\tIN := 1;\n\tEND_IF;"
        RANDOM += "\n\tIF NOT M AND IN THEN\n\t\t{SetFbVar(OUT,rand())}\n\tEND_IF;\nEND_FUNCTION_BLOCK\n"
        HEADER = "PROGRAM tesis0\n"
        END = "\nEND_PROGRAM\n\n"
        END += "CONFIGURATION Config0\n\n\tRESOURCE Res0 ON PLC\n\t\tTASK task0(INTERVAL := T#20ms,PRIORITY := 0);"
        END += "\n\t\tPROGRAM instance0 WITH task0 : tesis0;" + "\n\tEND_RESOURCE\nEND_CONFIGURATION"

        if len(supervisors) == 1:
            out = self.aux_generate_ST_OPENPLC(supervisors[0], actuators, namest, RANDOM, Mask=Mask,
                                               Isolated=Isolated, initial=initial)
        else:
            Coordinators = []
            Intersections = dict([])
            for i in range(len(supervisors)):
                for j in range(i + 1, len(supervisors)):
                    nonconflict, TESTcoor, alltest = self.coordinator([supervisors[i], supervisors[j]],
                                                                      [plants[i],
                                                                       plants[j]])  # revisa si son conflictivos
                    if not nonconflict:
                        print('conflict', i, j)
                        TESTSUP = self.supcon(TESTcoor, alltest, 'SUPf')
                        TESTSUP_dat = self.condat(TESTcoor, TESTSUP, 'TESTSUPdat')
                        CO = self.supreduce(TESTcoor, TESTSUP, TESTSUP_dat, "CO_" + str(i) + "_" + str(j))
#                        self.plot_automatas([CO, TESTcoor, alltest, TESTSUP], 1, False)
                        # DEStoADS(CO)
                        self.load_automata([CO])
                        Coordinators.append(CO)
                    a = set(self.automatas[supervisors[i]].c_events)
                    b = set(self.automatas[supervisors[j]].c_events)
                    intersect = list(a & b)
                    intersect = set([actuators[act].split(':')[0] for act in intersect])
                    if len(intersect) != 0:
                        for inter in intersect:
                            if inter in Intersections.keys():
                                if i not in Intersections[inter]:
                                    Intersections[inter].append(i)
                                if j not in Intersections[inter]:
                                    Intersections[inter].append(j)
                            else:
                                Intersections[inter] = [i, j]
            for c in Coordinators:
                for cont in self.automatas[c].c_events:
                    if actuators[cont].split(':')[0] not in Intersections.keys():
                        event = actuators[cont]
                        Intersections[event.split(':')[0]] = []
                        sup = c.split('_')
                        if cont in self.automatas[supervisors[int(sup[1])]].c_events:
                            Intersections[event.split(':')[0]].append(int(sup[1]))
                        if cont in self.automatas[supervisors[int(sup[2])]].c_events:
                            Intersections[event.split(':')[0]].append(int(sup[2]))
            COsw = ""
            COc = ""
            COu = ""
            st = []
            if_controllable = ""
            if_uncontrollable = ""
            sc = ""
            mask = ""
            j = 0
            aislated = ""
            if len(actuators) != 0:
                for i in range(len(supervisors)):
                    if_c, if_u = self.ifs(supervisors[i], actuators, i)
                    s, n_r = self.sw_case(supervisors[i], actuators, i, i, Intersections)
                    j += 1
                    if_controllable += if_c + "\n"
                    if_uncontrollable += if_u + '\n'
                    sc += "\n" + s + "\n"
                    st.append(n_r)
            if len(Isolated) != 0:
                if len(Isolated[0]) != 0:
                    for ais in range(len(Isolated[0])):
                        if_c, if_u = self.ifs(Isolated[0][ais], actuators, j)
                        s, n_r = self.sw_case(Isolated[0][ais], actuators, j, j)
                        j += 1
                        if_controllable += if_c + "\n"
                        if_uncontrollable += if_u + '\n'
                        sc += "\n" + s + "\n"
                        st.append(n_r)
                if len(Isolated[1]) != 0:
                    aislated = self.aislated(Isolated[1], actuators, Intersections)
                for c in Coordinators:
                    COsw += self.coordinator_sc(c, actuators=actuators, state_it=j)
                    a, b = self.ifs(c, actuators, j)
                    st.append(0)
                    j += 1
                    COc += a
                    COu += b

            intersection = self.intersection(Intersections, len(Coordinators) != 0)
            declaration = self.declaration_OPENPLC(actuators, st, j, Intersections, Coordinators, Mask,
                                                   initial=initial)
            for msk in Mask.keys():
                for e in Mask[msk]:
                    mask += "\t" + e[0] + " := " + msk + ";\n "
            out = RANDOM + HEADER + declaration

            out_aux = if_uncontrollable + COu + sc + COsw + intersection + COc + if_controllable + aislated + mask

            if initial == 'null':
                out += out_aux + END
            else:
                out_aux = out_aux.splitlines()
                out_aux = [f"\t{linea}" for linea in out_aux]
                out_aux = '\n'.join(out_aux)
                out += ('\tIF NOT initial THEN\n\t\tIF ' + actuators[initial].split(':')[
                    0] + ' THEN\n\t\t\tinitial := TRUE;\n\t\tEND_IF;\n\tELSIF initial THEN\n'
                        + out_aux + '\n\tEND_IF;' + END)
        if not os.path.exists('ST_Generated'):
            os.makedirs('ST_Generated')
        with open('ST_Generated/' + namest + ".st", 'w') as archivo:
            archivo.write(out)
        return out

    def aux_generate_ST_OPENPLC(self, name: str = "", actuators: dict = dict([]), namest="code_st", RANDOM="",
                                Mask: dict = dict([]), Isolated: list = [[], []], initial: str = 'null'):
        # Generate the ST code for 1 supervisor
        HEADER = "PROGRAM tesis0\n"
        END = "\nEND_PROGRAM\n\n"
        END += "CONFIGURATION Config0\n\n\tRESOURCE Res0 ON PLC\n\t\tTASK task0(INTERVAL := T#20ms,PRIORITY := 0);"
        END += "\n\t\tPROGRAM instance0 WITH task0 : tesis0;" + "\n\tEND_RESOURCE\nEND_CONFIGURATION"

        st = []
        if_controllable = ""
        if_uncontrollable = ""
        sc = ""
        mask = ""
        if_c, if_u = self.ifs(name, actuators)
        s, n_r = self.sw_case(name, actuators)
        if_controllable += if_c + "\n"
        if_uncontrollable += if_u + '\n'
        sc += "\n" + s + "\n"
        st.append(n_r)
        j = 1
        aislated = ""
        if len(Isolated) != 0:
            if len(Isolated[0]) != 0:
                for ais in range(len(Isolated[0])):
                    if_c, if_u = self.ifs(Isolated[0][ais], actuators, j)
                    s, n_r = self.sw_case(Isolated[0][ais], actuators, j, j)
                    j += 1
                    if_controllable += if_c + "\n"
                    if_uncontrollable += if_u + '\n'
                    sc += "\n" + s + "\n"
                    st.append(n_r)
            if len(Isolated[1]) != 0:
                aislated = self.aislated(Isolated[1], actuators)
        declaration = self.declaration_OPENPLC(actuators, st, j, mascara=Mask, initial=initial)
        for msk in Mask.keys():
            for e in Mask[msk]:
                mask += "\t" + e[0] + " := " + msk + ";\n "
        out = RANDOM + HEADER + declaration
        out_aux = if_uncontrollable + sc + if_controllable + aislated + mask
        if initial == 'null':
            out += out_aux + END
        else:
            out_aux = out_aux.splitlines()
            out_aux = [f"\t{linea}" for linea in out_aux]
            out_aux = '\n'.join(out_aux)
            out += ('\tIF NOT initial THEN\n\t\tIF ' + actuators[initial].split(':')[
                0] + ' THEN\n\t\t\tinitial := TRUE;\n\t\tEND_IF;\n\tELSIF initial THEN\n'
                    + out_aux + '\n\tEND_IF;' + END)
        return out

    def intersection(self, intersection: dict, CO=False, addG="_G[", addC="_C[", name_intersection="aux"):
        # Generate the code for the intersection between supervisors and coordinators
        out = ""
        for inter in intersection.keys():
            aux = ""
            coor = ""
            bandera = inter if not CO else name_intersection
            guesses = []
            for act in range(len(intersection[inter])):
                guesses.append(inter + addG + str(act) + "]")

            if len(guesses) != 1:
                if len(guesses) == 2:
                    out += "\tIF "
                    out += guesses[0] + " <> " + guesses[1] + " THEN\n"
                    out += "\t\t" + guesses[0] + " := " + inter + ";\n"
                    out += "\t\t" + guesses[1] + " := " + inter + ";"
                else:
                    out += "\tIF "
                    i = 0
                    j = 1
                    while j < len(guesses):
                        aux += "\t\t" + guesses[i] + " := " + inter + ";\n"
                        out += "(" + guesses[i] + " <> " + guesses[j] + ")"
                        i += 1
                        j += 1
                        if j != len(guesses):
                            out += " OR "
                        else:
                            out += " THEN\n"
                    aux += "\t\t" + guesses[j - 1] + " := " + inter + ";\t\t\t"
            if CO:
                coor += "\tIF " + bandera + " XOR " + inter + " THEN\n\t\t"
                coor += "IF NOT " + bandera + " & " + inter + addC + "0] THEN\n\t\t\t"
                coor += inter + " := 0;\n\t\t"
                coor += "ELSIF " + bandera + " & " + inter + addC + "1] THEN\n\t\t\t"
                coor += inter + " := 1;"
                coor += "\n\t\tEND_IF;"
                coor += "\n\tEND_IF;\n"
                coor += "\t" + inter + addG + "0] := " + inter + ";\n"
            out += aux + '\n'
            if len(guesses) != 1:
                out += "\tEND_IF;\n"

            out += "\t" + bandera + " := " + guesses[0] + ";\n"
            out += coor
        return out

    def declaration_OPENPLC(self, actuators, n_state: list, n_automata=-1, intersetion: dict = dict([]), CO: list = [],
                            mascara: dict = dict([]), initial: str = 'null'):
        # Variable blocks for OPENPLC ST version

        declaration = "\tVAR\n"
        clocks = ""
        start = "\tVAR\n"
        start += '\t\trandom : random_number;\n'
        start += '\t\trandom_num : DINT;\n'
        if initial != 'null':
            start += '\t\tinitial : BOOL;\n'
        if n_automata == -1:
            start += "\t\tstate :ARRAY [0..1] OF DINT;\n"
        else:
            start += "\t\tstate : ARRAY [0.." + str(n_automata) + "] OF DINT;\n"
        if len(CO) != 0:
            declared = []
            start += "\t\taux : BOOL := 0;\n"
            for coor in CO:
                for i in self.automatas[coor].c_events:
                    aux = actuators[i].split(':')[0]
                    if aux not in declared:
                        start += "\t\t" + aux + "_C : ARRAY [0..1] OF BOOL;\n"
                        declared.append(aux)
        if n_automata == -1 and n_state[0] != 0:
            start += "\t\tslt0" + " : ARRAY [0.." + str(n_state[0]) + "] OF DINT;\n"

        for i in range(0, n_automata):
            if n_state[i] == 0:
                continue
            start += "\t\tslt" + str(i) + " : ARRAY [0.." + str(n_state[i]) + "] OF DINT;\n"

        if len(intersetion.keys()) > 0:
            for inter in intersetion.keys():
                start += "\t\t" + inter + "_G : ARRAY [0.." + str(len(intersetion[inter])) + "] OF BOOL;\n"

        declared = []
        for msk in mascara.keys():
            for e in mascara[msk]:
                declaration += "\t\t" + e[0] + " AT " + e[1] + " : BOOL;\n "
        for act in actuators.values():
            aux = act.split(':')
            if 'INTERN' in aux[0]:
                if aux[0] not in declared:
                    start += "\t\t" + aux[0] + " : BOOL;\n"
                    declared.append(aux[0])
                    continue
            if aux[1] == 'ON' or aux[1] == 'OFF':
                if aux[0] in declared:
                    continue
                declaration += "\t\t" + aux[0] + " AT "
                declared.append(aux[0])
                if "IN" in aux[0]:
                    declaration += aux[2] + " : BOOL;\n"
                elif "OUT" in aux[0]:
                    declaration += aux[2] + " : BOOL;\n"
            else:
                if aux[1] not in declared:
                    declared.append(aux[1])
                    declaration += "\t\t" + aux[1] + " AT "
                    if "IN" in aux[1]:
                        declaration += aux[2] + " : BOOL;\n"
                    elif "OUT" in aux[1]:
                        declaration += aux[2] + " : BOOL;\n"
                start += "\t\t" + aux[0] + " : "

                if "FE" in aux[0]:
                    start += "F_TRIG;\n"
                if "RE" in aux[0]:
                    start += "R_TRIG;\n"

                clocks += "\t" + aux[0] + '(CLK:= ' + aux[1] + ');\n'
            ran = "\trandom(\n\t\tIN := True,\n\t\tOUT => random_num);\n"
        start += "\tEND_VAR\n"
        declaration += "\tEND_VAR\n"
        return start + declaration + clocks + ran

    def ifs(self, name: str, actuators=dict([]), n_state=0):  # Generate the ST code for conditional sentences
        if_uncontrollable = "\t"
        if_controllable = "\t"
        if name not in self.automatas.keys():
            return "ERROR"
        transit = self.automatas[name].transitions
        for i in range(0, len(transit)):
            origin = self.automatas[name].transitions[i][0]
            destination = self.automatas[name].transitions[i][2]
            event = str(self.automatas[name].transitions[i][1])
            if len(actuators) == 0:
                name_event = self.dict_events_name[event]
            else:
                name_event = actuators[self.dict_events_name[event]]
            name_event = name_event.split(':')

            if name_event[1] == 'OFF':
                name_event = 'NOT ' + name_event[0]
            else:
                name_event = name_event[0]
            if origin == destination:
                continue
            if self.dict_events_name[event] in self.c_events:
                if_controllable += "IF state[" + str(n_state) + "] = " + str(origin) \
                                   + " & " + name_event \
                                   + " THEN\n  " + "\t\t" + "state[" + str(n_state) + "] := " \
                                   + str(destination) + ";\n  " + "\tELS"
            elif self.dict_events_name[event] in self.uc_events:
                if_uncontrollable += "IF state[" + str(n_state) + "] = " + str(origin) + " & "
                if_uncontrollable += name_event + ('.Q' if 'FE' in name_event or 'RE' in name_event else '')
                if_uncontrollable += " THEN\n  " + "\t\t" + "state[" + str(n_state) + "] := "
                if_uncontrollable += str(destination) + ";\n  " + "\tELS"
        if if_controllable == "\t": if_controllable = ""
        if if_uncontrollable == "\t": if_uncontrollable = ""
        if not if_controllable == "":
            if_controllable = if_controllable.rstrip("ELS") + "END_IF;\n"
        if not if_uncontrollable == "":
            if_uncontrollable = if_uncontrollable.rstrip("ELS") + "END_IF;\n"
        return if_controllable, if_uncontrollable

    def sw_case(self, name, actuators=dict([]), n_aut=0, n_state=0, intersection: dict = dict([])):
        # Generate the ST code for the case statements
        act_guess = dict([])
        for inter in intersection.keys():
            for i in range(len(intersection[inter])):
                if intersection[inter][i] == n_aut:
                    if i in act_guess.keys():
                        act_guess[i].append(inter)
                    else:
                        act_guess[i] = [inter]
        n_r = 0
        state_list = self.automatas[name].states
        case = "\tCASE state[" + str(n_aut) + "] OF\n  "
        for state in state_list:
            events = [event for event in state.get_active_events() if event not in self.uc_events]
            num_event = len(events)
            if len(events) != 0:
                case += "\t\t" + str(state.get_id()) + ":\n  "
                if num_event > 1:
                    case += "\t\t\tCASE " + "slt" + str(n_state) + "[" + str(n_r) + "] OF\n  "
                    for i in range(0, num_event):
                        name_event = events[i] if len(actuators) == 0 else actuators[events[i]]
                        case += "\t\t\t\t" + str(i) + ":" + "\n  "
                        aux = name_event.split(":")
                        guess = ""
                        for i in act_guess.keys():
                            if aux[0] in act_guess[i]:
                                guess = "_G[" + str(i) + "]"
                        if "OFF" in name_event:
                            case += "\t\t\t\t\t" + aux[0]
                            case += guess
                            case += " := 0;\n  "
                        else:
                            case += "\t\t\t\t\t" + aux[0]
                            case += guess
                            case += " := 1;\n  "
                    case += "\t\t\tEND_CASE;\n  "
                    case += ("\t\t\t" + "slt" + str(n_state) + "[" + str(n_r) + "] := " + "(random_num + " + "slt" +
                             str(n_state) + "[" + str(n_r) + "]" + ") MOD " + str(num_event) + ";\n  ")
                    case += "\t\t\t" + "random_num := " + "random_num - " + "slt" + str(n_state) + "[" + str(
                        n_r) + "];\n "
                    n_r += 1

                elif num_event == 1:
                    name_event = name_event = events[0] if len(actuators) == 0 else actuators[events[0]]
                    aux = name_event.split(":")
                    guess = ""
                    for i in act_guess.keys():
                        if aux[0] in act_guess[i]:
                            guess = "_G[" + str(i) + "]"
                    if "OFF" in name_event:
                        case += "\t\t\t" + aux[0]
                        case += guess
                        case += " := 0;\n  "
                    else:
                        case += "\t\t\t" + aux[0]
                        case += guess
                        case += " := 1;\n"

        return [case + "\tEND_CASE;", n_r]

    def coordinator_sc(self, name, state_it: int = 2, actuators=dict([])):
        # Generate the ST code for the Coordinator case statements
        state_list = self.automatas[name].states
        case = "\tCASE state[" + str(state_it) + "] OF\n  "
        for state in state_list:
            all_events = self.automatas[name].c_events
            events = [event for event in state.get_active_events() if event not in self.uc_events]
            num_event = len(all_events)
            if len(events) != 0:
                case += "\t\t" + str(state.get_id()) + ":\n  "
                for i in range(0, num_event):
                    name_event = all_events[i] if len(actuators) == 0 else actuators[all_events[i]]
                    aux = name_event.split(":")
                    if "OFF" in name_event:
                        case += "\t\t\t" + aux[0]
                        case += "_C" + "[0]"
                    else:
                        case += "\t\t\t" + aux[0]
                        case += "_C" + "[1]"
                    if all_events[i] in events:
                        case += " := 1;\n"
                    else:
                        case += " := 0;\n"

        case += "\tEND_CASE;\n  "
        return case
    def __str__(self):
        if not self.automatas:
            return "No automata loaded."
        out = "Automata loaded in process:\n"
        for name, aut in self.automatas.items():
            out += f"  - {name} ({len(aut.states)} states, {len(aut.transitions)} transitions)\n"
        return out

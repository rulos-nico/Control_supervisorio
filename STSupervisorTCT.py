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
        # Convertir uncontrollable a set para búsquedas O(1)
        uncontrollable_set = set(uncontrollable) if uncontrollable else set()
        
        for i in range(0, len(event)):
            # aux_event no se usa, solo accedemos directamente a event[i]
            if event[i] not in self.uc_events and event[i] in uncontrollable_set:
                self.uc_events.append(event[i])
            if event[i] not in self.c_events and event[i] not in uncontrollable_set:
                self.c_events.append(event[i])

            if event[i] not in dict_events.keys():
                if event[i] in uncontrollable_set:
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
        # Optimización: acumular todas las transiciones y agregarlas en batch
        transitions_batch = []
        events_batch = []
        uncontrollable_batch = []
        
        uc_events = self.automatas[name].uc_events
        
        for s in self.automatas[name].states:
            # Convertir a set para búsqueda O(1)
            active_events_set = set(s.get_active_events())
            state_id = s.get_id()
            
            for e in uc_events:
                if e not in active_events_set:
                    transitions_batch.append((state_id, state_id))
                    events_batch.append(e)
                    uncontrollable_batch.append(e)
        
        # Agregar todas las transiciones en una sola llamada
        if transitions_batch:
            self.add_transition(name, transitions_batch, events_batch, uncontrollable_batch)

    def add_self_events(self, name, events: list):  # Add a self loop  for each event in events in an automaton
        for e in events:
            self.add_self_event(name, e)

    def add_self_event(self, name, event, uncontrollable: bool = False):  # Add a self loop of one event in an automaton
        # Optimización: precalcular verificaciones, usar sets, y batch processing
        # Lógica: Si un evento está bloqueado (no en active_events), agregar autoloop
        # Esto debe aplicarse a TODOS los estados donde el evento no está activo
        
        c_events_set = set(self.c_events)
        uc_events_set = set(self.uc_events)
        
        # Determinar categoría del evento
        is_uc = event in uc_events_set
        is_new_event = event not in c_events_set and event not in uc_events_set
        
        # Batch processing: acumular transiciones para una sola llamada
        transitions_batch = []
        events_batch = []
        uncontrollable_batch = []
        
        for s in self.automatas[name].states:
            # Convertir a set para búsqueda O(1)
            active_events_set = set(s.get_active_events())
            
            if event not in active_events_set:
                state_id = s.get_id()
                transitions_batch.append((state_id, state_id))
                events_batch.append(event)
                
                # Determinar si es evento no controlable para el batch
                if is_new_event:
                    if uncontrollable:
                        uncontrollable_batch.append(event)
                    # Si es nuevo y controlable, no agregar a uncontrollable_batch
                elif is_uc:
                    uncontrollable_batch.append(event)
                # Si es controlable conocido, no agregar a uncontrollable_batch
        
        # Agregar todas las transiciones en una sola llamada (batch processing)
        if transitions_batch:
            self.add_transition(name, transitions_batch, events_batch, uncontrollable_batch)

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
            events_set = set()  # Para búsquedas O(1)
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
                if "marker" in linea and 'none' not in linea:
                    aux = 1
                    continue
                if aux == 1:
                    if "\n" == linea:
                        continue
                    marked = [int(x) for x in linea.split()]
                    # Usar list comprehension es más eficiente
                    self.add_state(name, num_state, [], [x in marked for x in range(num_state)])
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
                    
                    # Obtener evento (precalcular en vez de repetir)
                    event_key = aux[1]
                    event = self.dict_events_name.get(event_key, event_key)
                    
                    # Usar set para búsqueda O(1)
                    if event not in events_set:
                        events_set.add(event)
                        if int(aux[1]) % 2 == 0:
                            uc_events.append(event)
                    events.append(event)
                    
        self.add_transition(name, transitions, events, uc_events)
        return name

    def aislated(self, aislated: list = [], actuators: list = [], interseccion=dict([])):
        # Generate ST code from Ailated supervisor and actuators.
        # Usar lista para acumular y join() al final (O(n) vs O(n²))
        out_parts = []
        for a in aislated:
            # Precalcular splits para evitar repetición
            act_a0_parts = actuators[a[0]].split(':')
            act_a1_part0 = actuators[a[1]].split(':')[0]
            
            add = ""
            if len(act_a0_parts) > 1:
                add = "NOT " if act_a0_parts[1] == 'OFF' else ''
            
            out_parts.append(f"\tIF NOT {act_a1_part0} & {add}{act_a0_parts[0]} THEN\n\t\t")
            out_parts.append(f"{act_a1_part0} := 1;\n")
            out_parts.append(f"\tELSIF {act_a1_part0} & {add}{act_a0_parts[0]} THEN\n\t\t")
            out_parts.append(f"{act_a0_parts[0]} := 0;\n\t")
            
            if act_a0_parts[0] in interseccion.keys():
                out_parts.append(f"\t{act_a0_parts[0]}_G[0] := 0;\n")
            out_parts.append("END_IF;\n")
        
        return ''.join(out_parts)

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
            Intersections = {}
            
            # Optimización: Precalcular eventos controlables como sets
            supervisor_c_events = [set(self.automatas[sup].c_events) for sup in supervisors]
            
            for i in range(len(supervisors)):
                for j in range(i + 1, len(supervisors)):
                    nonconflict, TESTcoor, alltest = self.coordinator([supervisors[i], supervisors[j]],
                                                                      [plants[i],
                                                                       plants[j]])  # revisa si son conflictivos
                    if not nonconflict:
                        print(f'conflict {i}, {j}')
                        TESTSUP = self.supcon(TESTcoor, alltest, 'SUPf')
                        TESTSUP_dat = self.condat(TESTcoor, TESTSUP, 'TESTSUPdat')
                        CO = self.supreduce(TESTcoor, TESTSUP, TESTSUP_dat, f"CO_{i}_{j}")
#                        self.plot_automatas([CO, TESTcoor, alltest, TESTSUP], 1, False)
                        # DEStoADS(CO)
                        self.load_automata([CO])
                        Coordinators.append(CO)
                    
                    # Optimización: Usar sets precalculados para intersección (O(min(n,m)) vs O(n*m))
                    intersect_events = supervisor_c_events[i] & supervisor_c_events[j]
                    
                    if intersect_events:
                        # Usar comprehension y precalcular split
                        intersect_actuators = {actuators[act].split(':')[0] for act in intersect_events}
                        
                        for inter in intersect_actuators:
                            if inter in Intersections:
                                # Usar set para evitar duplicados (más eficiente)
                                indices_set = set(Intersections[inter])
                                indices_set.add(i)
                                indices_set.add(j)
                                Intersections[inter] = list(indices_set)
                            else:
                                Intersections[inter] = [i, j]
            # Optimización: Procesar coordinadores de forma más eficiente
            for c in Coordinators:
                # Precalcular split del coordinador una sola vez
                sup_indices = c.split('_')
                sup_idx1 = int(sup_indices[1])
                sup_idx2 = int(sup_indices[2])
                
                # Precalcular sets de eventos controlables para búsquedas O(1)
                sup1_c_events = supervisor_c_events[sup_idx1]
                sup2_c_events = supervisor_c_events[sup_idx2]
                
                for cont in self.automatas[c].c_events:
                    # Precalcular split para evitar repetición
                    event_actuator = actuators[cont].split(':')[0]
                    
                    if event_actuator not in Intersections:
                        Intersections[event_actuator] = []
                        # Usar sets precalculados para búsquedas O(1)
                        if cont in sup1_c_events:
                            Intersections[event_actuator].append(sup_idx1)
                        if cont in sup2_c_events:
                            Intersections[event_actuator].append(sup_idx2)
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
        # Usar listas para acumular strings eficientemente
        out_parts = []
        
        for inter in intersection.keys():
            aux_parts = []
            coor_parts = []
            bandera = inter if not CO else name_intersection
            guesses = [f"{inter}{addG}{act}]" for act in range(len(intersection[inter]))]

            if len(guesses) != 1:
                if len(guesses) == 2:
                    out_parts.extend([
                        "\tIF ",
                        f"{guesses[0]} <> {guesses[1]} THEN\n",
                        f"\t\t{guesses[0]} := {inter};\n",
                        f"\t\t{guesses[1]} := {inter};"
                    ])
                else:
                    out_parts.append("\tIF ")
                    conditions = []
                    for i in range(len(guesses) - 1):
                        aux_parts.append(f"\t\t{guesses[i]} := {inter};\n")
                        conditions.append(f"({guesses[i]} <> {guesses[i+1]})")
                    
                    out_parts.append(" OR ".join(conditions))
                    out_parts.append(" THEN\n")
                    aux_parts.append(f"\t\t{guesses[-1]} := {inter};\t\t\t")
            
            if CO:
                coor_parts.extend([
                    f"\tIF {bandera} XOR {inter} THEN\n\t\t",
                    f"IF NOT {bandera} & {inter}{addC}0] THEN\n\t\t\t",
                    f"{inter} := 0;\n\t\t",
                    f"ELSIF {bandera} & {inter}{addC}1] THEN\n\t\t\t",
                    f"{inter} := 1;",
                    "\n\t\tEND_IF;",
                    "\n\tEND_IF;\n",
                    f"\t{inter}{addG}0] := {inter};\n"
                ])
            
            out_parts.extend(aux_parts)
            out_parts.append('\n')
            
            if len(guesses) != 1:
                out_parts.append("\tEND_IF;\n")

            out_parts.append(f"\t{bandera} := {guesses[0]};\n")
            out_parts.extend(coor_parts)
        
        return ''.join(out_parts)

    def declaration_OPENPLC(self, actuators, n_state: list, n_automata=-1, intersetion: dict = dict([]), CO: list = [],
                            mascara: dict = dict([]), initial: str = 'null'):
        # Variable blocks for OPENPLC ST version
        # Usar listas para acumular y sets para búsquedas O(1)
        declaration_parts = ["\tVAR\n"]
        start_parts = ["\tVAR\n", '\t\trandom : random_number;\n', '\t\trandom_num : DINT;\n']
        clocks_parts = []
        
        if initial != 'null':
            start_parts.append('\t\tinitial : BOOL;\n')
            
        if n_automata == -1:
            start_parts.append("\t\tstate :ARRAY [0..1] OF DINT;\n")
        else:
            start_parts.append(f"\t\tstate : ARRAY [0..{n_automata}] OF DINT;\n")
            
        declared = set()  # Usar set para búsquedas O(1)
        
        if len(CO) != 0:
            start_parts.append("\t\taux : BOOL := 0;\n")
            for coor in CO:
                for i in self.automatas[coor].c_events:
                    aux = actuators[i].split(':')[0]
                    if aux not in declared:
                        start_parts.append(f"\t\t{aux}_C : ARRAY [0..1] OF BOOL;\n")
                        declared.add(aux)
                        
        if n_automata == -1 and n_state[0] != 0:
            start_parts.append(f"\t\tslt0 : ARRAY [0..{n_state[0]}] OF DINT;\n")

        for i in range(n_automata):
            if n_state[i] == 0:
                continue
            start_parts.append(f"\t\tslt{i} : ARRAY [0..{n_state[i]}] OF DINT;\n")

        if len(intersetion.keys()) > 0:
            for inter in intersetion.keys():
                start_parts.append(f"\t\t{inter}_G : ARRAY [0..{len(intersetion[inter])}] OF BOOL;\n")

        declared.clear()  # Reutilizar el set
        
        for msk in mascara.keys():
            for e in mascara[msk]:
                declaration_parts.append(f"\t\t{e[0]} AT {e[1]} : BOOL;\n ")
                
        for act in actuators.values():
            aux = act.split(':')
            if 'INTERN' in aux[0]:
                if aux[0] not in declared:
                    start_parts.append(f"\t\t{aux[0]} : BOOL;\n")
                    declared.add(aux[0])
                    continue
                    
            if aux[1] == 'ON' or aux[1] == 'OFF':
                if aux[0] in declared:
                    continue
                declared.add(aux[0])
                io_type = "IN" if "IN" in aux[0] else ("OUT" if "OUT" in aux[0] else None)
                if io_type:
                    declaration_parts.append(f"\t\t{aux[0]} AT {aux[2]} : BOOL;\n")
            else:
                if aux[1] not in declared:
                    declared.add(aux[1])
                    io_type = "IN" if "IN" in aux[1] else ("OUT" if "OUT" in aux[1] else None)
                    if io_type:
                        declaration_parts.append(f"\t\t{aux[1]} AT {aux[2]} : BOOL;\n")
                
                trig_type = "F_TRIG" if "FE" in aux[0] else ("R_TRIG" if "RE" in aux[0] else None)
                if trig_type:
                    start_parts.append(f"\t\t{aux[0]} : {trig_type};\n")
                    clocks_parts.append(f"\t{aux[0]}(CLK:= {aux[1]});\n")
                    
        start_parts.append("\tEND_VAR\n")
        declaration_parts.append("\tEND_VAR\n")
        ran = "\trandom(\n\t\tIN := True,\n\t\tOUT => random_num);\n"
        
        return ''.join(start_parts) + ''.join(declaration_parts) + ''.join(clocks_parts) + ran

    def ifs(self, name: str, actuators=dict([]), n_state=0):  # Generate the ST code for conditional sentences
        if name not in self.automatas.keys():
            return "ERROR"
        
        # Usar listas para acumular eficientemente
        controllable_parts = []
        uncontrollable_parts = []
        
        # Precalcular sets para búsquedas O(1)
        c_events_set = set(self.c_events)
        uc_events_set = set(self.uc_events)
        
        transit = self.automatas[name].transitions
        for origin, event_id, destination in transit:
            if origin == destination:
                continue
                
            event = str(event_id)
            event_name = self.dict_events_name[event]
            
            # Obtener y procesar nombre del evento
            if len(actuators) == 0:
                name_event_raw = event_name
            else:
                name_event_raw = actuators[event_name]
            
            # Precalcular el split
            name_event_parts = name_event_raw.split(':')
            
            # Determinar el nombre final del evento
            if len(name_event_parts) > 1 and name_event_parts[1] == 'OFF':
                name_event = f'NOT {name_event_parts[0]}'
            else:
                name_event = name_event_parts[0]
            
            # Generar código según tipo de evento
            if event_name in c_events_set:
                controllable_parts.append(
                    f"IF state[{n_state}] = {origin} & {name_event} THEN\n  "
                    f"\t\tstate[{n_state}] := {destination};\n  \tELS"
                )
            elif event_name in uc_events_set:
                q_suffix = '.Q' if 'FE' in name_event or 'RE' in name_event else ''
                uncontrollable_parts.append(
                    f"IF state[{n_state}] = {origin} & {name_event}{q_suffix} THEN\n  "
                    f"\t\tstate[{n_state}] := {destination};\n  \tELS"
                )
        
        # Construir resultados finales
        if_controllable = ""
        if_uncontrollable = ""
        
        if controllable_parts:
            if_controllable = ''.join(controllable_parts).rstrip("ELS") + "END_IF;\n"
            
        if uncontrollable_parts:
            if_uncontrollable = ''.join(uncontrollable_parts).rstrip("ELS") + "END_IF;\n"
        
        return if_controllable, if_uncontrollable

    def sw_case(self, name, actuators=dict([]), n_aut=0, n_state=0, intersection: dict = dict([])):
        # Generate the ST code for the case statements
        # Precalcular act_guess de forma más eficiente
        act_guess = {}
        for inter, indices in intersection.items():
            for i, idx in enumerate(indices):
                if idx == n_aut:
                    act_guess.setdefault(i, []).append(inter)
        
        n_r = 0
        state_list = self.automatas[name].states
        case_parts = [f"\tCASE state[{n_aut}] OF\n  "]
        
        # Precalcular set de eventos no controlables para búsqueda O(1)
        uc_events_set = set(self.uc_events)
        
        for state in state_list:
            events = [event for event in state.get_active_events() if event not in uc_events_set]
            num_event = len(events)
            
            if num_event == 0:
                continue
                
            case_parts.append(f"\t\t{state.get_id()}:\n  ")
            
            if num_event > 1:
                case_parts.append(f"\t\t\tCASE slt{n_state}[{n_r}] OF\n  ")
                
                for i, event in enumerate(events):
                    name_event = events[i] if len(actuators) == 0 else actuators[event]
                    aux = name_event.split(":")
                    
                    # Buscar guess de forma más eficiente
                    guess = ""
                    for guess_idx, act_list in act_guess.items():
                        if aux[0] in act_list:
                            guess = f"_G[{guess_idx}]"
                            break
                    
                    value = "0" if "OFF" in name_event else "1"
                    case_parts.append(f"\t\t\t\t{i}:\n  \t\t\t\t\t{aux[0]}{guess} := {value};\n  ")
                
                case_parts.append("\t\t\tEND_CASE;\n  ")
                case_parts.append(
                    f"\t\t\tslt{n_state}[{n_r}] := (random_num + slt{n_state}[{n_r}]) MOD {num_event};\n  "
                )
                case_parts.append(f"\t\t\trandom_num := random_num - slt{n_state}[{n_r}];\n ")
                n_r += 1
                
            elif num_event == 1:
                name_event = events[0] if len(actuators) == 0 else actuators[events[0]]
                aux = name_event.split(":")
                
                # Buscar guess de forma más eficiente
                guess = ""
                for guess_idx, act_list in act_guess.items():
                    if aux[0] in act_list:
                        guess = f"_G[{guess_idx}]"
                        break
                
                value = "0" if "OFF" in name_event else "1"
                case_parts.append(f"\t\t\t{aux[0]}{guess} := {value};\n")
        
        case_parts.append("\tEND_CASE;")
        return [''.join(case_parts), n_r]

    def coordinator_sc(self, name, state_it: int = 2, actuators=dict([])):
        # Generate the ST code for the Coordinator case statements
        state_list = self.automatas[name].states
        case_parts = [f"\tCASE state[{state_it}] OF\n  "]
        
        # Precalcular set de eventos no controlables para búsqueda O(1)
        uc_events_set = set(self.uc_events)
        
        for state in state_list:
            all_events = self.automatas[name].c_events
            events_set = set(event for event in state.get_active_events() if event not in uc_events_set)
            
            if not events_set:
                continue
                
            case_parts.append(f"\t\t{state.get_id()}:\n  ")
            
            for event in all_events:
                name_event = event if len(actuators) == 0 else actuators[event]
                aux = name_event.split(":")
                
                index = "[0]" if "OFF" in name_event else "[1]"
                value = "1" if event in events_set else "0"
                
                case_parts.append(f"\t\t\t{aux[0]}_C{index} := {value};\n")
        
        case_parts.append("\tEND_CASE;\n  ")
        return ''.join(case_parts)
    def __str__(self):
        if not self.automatas:
            return "No automata loaded."
        out = "Automata loaded in process:\n"
        for name, aut in self.automatas.items():
            out += f"  - {name} ({len(aut.states)} states, {len(aut.transitions)} transitions)\n"
        return out

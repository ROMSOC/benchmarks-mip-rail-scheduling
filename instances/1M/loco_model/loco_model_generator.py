import csv
import os
import time
from datetime import date
import random
import gurobipy as grb
import networkx as nx


class LocosModelGenerator:

    def __init__(self, trains, unique_locos, trains_next_t_l, delta_index_list=None,
                 locos_d=None, drivers_t=None, delta = None):


        self.model = grb.Model()

        with open(trains, encoding="utf-8") as file1:
            trains = list(csv.reader(file1))
        self.trains = trains[1:]

        with open(unique_locos, encoding="utf-8") as file3:
            locos = list(csv.reader(file3))
        self.locos = locos[1:]
        locos_items = [item[1] for item in locos]

        if delta_index_list is not None:
            self.delta_index_list = delta_index_list

        if drivers_t is not None:
            self.drivers_t = drivers_t

        if delta is not None:
            self.delta = delta

        self.trains_next_t_l = trains_next_t_l

        self.locos_dict = {"Type8": {item for item in locos_items if item.split(" - ")[0] == "Type8"},
                           "Type7": {item for item in locos_items if item.split(" - ")[0] == "Type7"},
                           "Type5": {item for item in locos_items if item.split(" - ")[0] == "Type5"},
                           "Type6": {item for item in locos_items if item.split(" - ")[0] == "Type6"},
                           "Type4": {item for item in locos_items if item.split(" - ")[0] == "Type4"},
                           "Type2": {item for item in locos_items if item.split(" - ")[0] == "Type2"},
                           "Type3": {item for item in locos_items if item.split(" - ")[0] == "Type3"},
                           "Type1": {item for item in locos_items if item.split(" - ")[0] == "Type1"}}

        self.controller = locos_d
        if locos_d is not None:
            self.locos_d = {}
            for driver, locos in locos_d.items():
                self.locos_d[driver] = set([item.split(" - ")[0] for item in locos])

            self.drivers_l = {}
            all_locos = []
            for driver, locos in self.locos_d.items():
                for l1 in locos:
                    all_locos.append(l1)

            for l2 in all_locos:
                self.drivers_l[l2] = [k for k, v in self.locos_d.items() if l2 in v]

        self.loco_master_types = ["Type8", "Type4", "Type5", "Type6", "Type7"]
        self.locos_master = ["Type8 - 7", "Type4 - 166", "Type5 - 52", "Type6 - 6495", "Type7 - 90"]
        self.foreign_loco_types = ["Type1", "Type2", "Type3"]
        self.locos_dict_foreign = {k: v for k, v in self.locos_dict.items() if k in self.foreign_loco_types}
        self.network = nx.DiGraph()
        self.f = grb.tupledict()
        self.f_index_list = []
        self.lmbda = grb.tupledict()
        self.cL0 = grb.tupledict()
        self.cL1 = grb.tupledict()
        self.cL2 = grb.tupledict()
        self.cL3 = grb.tupledict()
        self.cL4 = grb.tupledict()
        self.cL5 = grb.tupledict()
        self.cC1 = grb.tupledict()
        self.cC2 = grb.tupledict()
        self.lmbda_index_list = []

    def generate_network(self):
        nx.set_edge_attributes(self.network, '', 'feasible_locos')

        for loco in self.locos_master:
            loco_type = loco.split(" - ")[0]
            successors = self.trains_next_t_l[loco]
            for train, values in successors.items():

                for t in values:
                    if (train, t) in self.network.edges and loco_type not in self.network[train][t]["feasible_locos"]:
                        self.network[train][t]["feasible_locos"].append(loco_type)
                    if (train, t) not in self.network.edges:
                        self.network.add_edge(train, t)
                        self.network[train][t]["feasible_locos"] = [loco_type]

        for train in self.trains:
            train_id = train[0]
            loco_requirement = train[20]
            if loco_requirement == "H_D":
                self.network.add_edge("ALPHA", str(train_id))
                self.network["ALPHA"][str(train_id)]["feasible_locos"] = self.locos_dict["Type4"]
                self.network.add_edge(str(train_id), "OMEGA")
                self.network[str(train_id)]["OMEGA"]["feasible_locos"] = self.locos_dict["Type4"]

            elif loco_requirement == "H_E":
                self.network.add_edge("ALPHA", str(train_id))
                self.network["ALPHA"][str(train_id)]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type5"])
                self.network.add_edge(str(train_id), "OMEGA")
                self.network[str(train_id)]["OMEGA"]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type5"])

            elif loco_requirement == "N_D":
                self.network.add_edge("ALPHA", str(train_id))
                self.network["ALPHA"][str(train_id)]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type6"]).union(self.locos_dict["Type7"])
                self.network.add_edge(str(train_id), "OMEGA")
                self.network[str(train_id)]["OMEGA"]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type6"]).union(self.locos_dict["Type7"])

            elif loco_requirement == "N_E":
                self.network.add_edge("ALPHA", str(train_id))
                self.network["ALPHA"][str(train_id)]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type6"]).union(self.locos_dict["Type7"]).union(self.locos_dict["Type5"]).union(self.locos_dict["Type5"])
                self.network.add_edge(str(train_id), "OMEGA")
                self.network[str(train_id)]["OMEGA"]["feasible_locos"] = self.locos_dict["Type4"].union(self.locos_dict["Type6"]).union(self.locos_dict["Type7"]).union(self.locos_dict["Type5"]).union(self.locos_dict["Type5"])

            else:
                self.network.add_edge("ALPHA", str(train_id))
                self.network["ALPHA"][str(train_id)]["feasible_locos"] = train[21]
                self.network.add_edge(str(train_id), "OMEGA")
                self.network[str(train_id)]["OMEGA"]["feasible_locos"] = train[21]

    def generate_variables(self):
        # variable generation
        for u, v, data in self.network.edges.data():
            if data["feasible_locos"] == "Type1" or data["feasible_locos"] == "Type2" or data["feasible_locos"] == "Type3":
                continue

            for loco in data["feasible_locos"]:
                self.f[str(u), str(v), str(loco)] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_{u}_{v}_{loco}")
                self.f_index_list.append([u, v, loco, f"f_{u}_{v}_{loco}"])

        for t in self.trains:
            train_id = t[0]
            self.lmbda[train_id] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"lmbda_{train_id}")
            self.lmbda_index_list.append(f"lmbda_{train_id}")

        for t in self.trains:
            if t[21] == "Type1":
                loco = self.locos_dict["Type1"].pop()
                l_str = loco.replace(" ", "")
                self.f["ALPHA", t[0], loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_ALPHA_{t[0]}_{l_str}")
                self.f[t[0], "OMEGA", loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_{t[0]}_OMEGA_{l_str}")
                self.f_index_list.append(["ALPHA", t[0], loco, f"f_ALPHA_{t[0]}_{l_str}"])
                self.f_index_list.append([t[0], "OMEGA", loco, f"f_{t[0]}_OMEGA_{l_str}"])

            if t[21] == "Type2":
                loco = self.locos_dict["Type2"].pop()
                l_str = loco.replace(" ", "")
                self.f["ALPHA", t[0], loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_ALPHA_{t[0]}_{l_str}")
                self.f[t[0], "OMEGA", loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_{t[0]}_OMEGA_{l_str}")
                self.f_index_list.append(["ALPHA", t[0], loco, f"f_ALPHA_{t[0]}_{l_str}"])
                self.f_index_list.append([t[0], "OMEGA", loco, f"f_{t[0]}_OMEGA_{l_str}"])

            if t[21] == "Type3":
                loco = self.locos_dict["Type3"].pop()
                l_str = loco.replace(" ", "")
                self.f["ALPHA", t[0], loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_ALPHA_{t[0]}_{l_str}")
                self.f[t[0], "OMEGA", loco] = self.model.addVar(vtype=grb.GRB.BINARY, name=f"f_{t[0]}_OMEGA_{l_str}")
                self.f_index_list.append(["ALPHA", t[0], loco, f"f_ALPHA_{t[0]}_{l_str}"])
                self.f_index_list.append([t[0], "OMEGA", loco, f"f_{t[0]}_OMEGA_{l_str}"])

        self.model.update()

        available_trains = set([int(t[0]) for t in self.delta_index_list])

        available_trains.add("ALPHA")
        available_trains.add("OMEGA")

        delta_vars = set([i[2] for i in self.delta_index_list])

        for [t1, t2, l, var_name] in self.f_index_list:
            # if t1 == "ALPHA" and int(t2) not in available_trains:
            #     self.model.remove(self.model.getVarByName(var_name))
            #     if (t1, t2, l) in self.f.keys():
            #         del self.f[t1, t2, l]
            #         print(t1, t2, l)
            # if t2 == "OMEGA" and int(t1) not in available_trains:
            #     self.model.remove(self.model.getVarByName(var_name))
            #     if (t1, t2, l) in self.f.keys():
            #         del self.f[t1, t2, l]
            #         print(t1, t2, l)
            # if t1 != "ALPHA" and t2 != "OMEGA":
            #     if int(t1) not in available_trains:
            #         self.model.remove(self.model.getVarByName(var_name))
            #         if (t1, t2, l) in self.f.keys():
            #             del self.f[t1, t2, l]
            #             print(t1, t2, l)
            #     if int(t2) not in available_trains:
            #         self.model.remove(self.model.getVarByName(var_name))
            #         if (t1, t2, l) in self.f.keys():
            #             del self.f[t1, t2, l]
            #             print(t1, t2, l)
            if t1 == "ALPHA":
                continue
            if " - " in l:
                loco_type = l.split(" - ")[0]
                drivers_t_arg = set([item for item in self.drivers_t[t1]])
                drivers_l_1 = self.drivers_l[loco_type]
                relevant_drivers = drivers_t_arg.intersection(drivers_l_1)
                # relevant_deltas = [item[2] for item in self.delta_index_list if
                #                    item[0] == t1 and item[1] in relevant_drivers]
                relevant_deltas = 0
                for rd in relevant_drivers:
                    if (t1, rd) in self.delta:
                        relevant_deltas += 1
                        break

                if relevant_deltas == 0:
                    self.model.remove(self.model.getVarByName(var_name))
                    if (t1, t2, l) in self.f.keys():
                        del self.f[t1, t2, l]
            else:
                drivers_t_arg = set([item for item in self.drivers_t[t1]])
                drivers_l_1 = self.drivers_l[l]
                relevant_drivers = drivers_t_arg.intersection(drivers_l_1)
                relevant_deltas = []
                for d1 in relevant_drivers:
                    if f"delta_{t1}_{d1}" in delta_vars:
                        relevant_deltas.append(f"delta_{t1}_{d1}")
                # relevant_deltas = [item[2] for item in self.delta_index_list if
                #                    item[0] == t1 and item[1] in relevant_drivers]
                if len(relevant_deltas) == 0:
                    self.model.remove(self.model.getVarByName(var_name))
                    if (t1, t2, l) in self.f.keys():
                        del self.f[t1, t2, l]
        self.model.update()

    def generate_constraints(self):
        # coupling variables
        for train in self.trains:
            train_id = str(train[0])
            self.cL0[train_id] = self.model.addConstr(self.lmbda[train_id] == self.f.sum(train_id, "*", "*"),
                                                      name=f"cL0_{train_id}")

        print("C0", len(self.cL0))

        # arc capacity constraint:
        for u, v in self.network.edges:
            if u in ["ALPHA", "OMEGA"] or v in ["ALPHA", "OMEGA"]:
                expr1 = self.f.sum(u, v, "*")
                if expr1.size() > 1:
                    self.cL1[u, v] = self.model.addConstr(self.f.sum(u, v, "*") <= 1, name=f"cL1_{u}_{v}")
                # self.cL1[u, v].Lazy = -1
        print("C1", len(self.cL1))

        # flow conservation - per loco
        for train in self.trains:
            train_id = str(train[0])
            loco_requirement = train[20]
            expr1 = self.f.sum("*", train_id, "*")
            self.cL2[train_id, 2] = self.model.addConstr(expr1 <= 1, name=f"cL2_{train_id}_2")

            if loco_requirement == "H_D":
                for l_id in self.locos_dict["Type4"]:
                    expr1 = self.f.sum("*", train_id, l_id)
                    expr2 = self.f.sum(train_id, "*", l_id)
                    self.cL2[train_id, l_id] = self.model.addConstr(expr1 - expr2 == 0, name=f"cL2_{train_id}_{l_id.replace(' ','')}")

            elif loco_requirement == "H_E":
                loco_types = ["Type4", "Type5"]
                for loco in loco_types:
                    for l_id in self.locos_dict[loco]:
                        expr1 = self.f.sum("*", train_id, l_id)
                        expr2 = self.f.sum(train_id, "*", l_id)
                        self.cL2[train_id, l_id] = self.model.addConstr(expr1 - expr2 == 0,
                                                                        name=f"cL2_{train_id}_{l_id.replace(' ', '')}")

            elif loco_requirement == "N_D":
                loco_types = ["Type4", "Type6", "Type7"]
                for loco in loco_types:
                    for l_id in self.locos_dict[loco]:
                        expr1 = self.f.sum("*", train_id, l_id)
                        expr2 = self.f.sum(train_id, "*", l_id)
                        self.cL2[train_id, l_id] = self.model.addConstr(expr1 - expr2 == 0,
                                                                        name=f"cL2_{train_id}_{l_id.replace(' ', '')}")

            elif loco_requirement == "N_E":
                loco_types = ["Type4", "Type6", "Type7", "Type5", "Type8"]
                for loco in loco_types:
                    for l_id in self.locos_dict[loco]:
                        expr1 = self.f.sum("*", train_id, l_id)
                        expr2 = self.f.sum(train_id, "*", l_id)
                        self.cL2[train_id, l_id] = self.model.addConstr(expr1 - expr2 == 0,
                                                                        name=f"cL2_{train_id}_{l_id.replace(' ', '')}")

            else:
                self.cL2[train_id, "foreign"] = self.model.addConstr(
                    self.f.sum("ALPHA", train_id, "*") - self.f.sum(train_id, "OMEGA", "*") == 0,
                    name=f"cL2_{train_id}_foreign")

        print("C2", len(self.cL2))

        # source and sink - normal locos
        for loco_type, locos in self.locos_dict.items():
            for l5 in locos:

                # self.cL5[l5] = self.model.addConstr(cap_variable <= cap, name=f"{l5}_cap")

                self.cL3[l5] = self.model.addConstr(self.f.sum("ALPHA", "*", l5) <= 1, name=f"cL3_{l5}")
                self.cL4[l5] = self.model.addConstr(self.f.sum("*", "OMEGA", l5) <= 1, name=f"cL4_{l5}")
                # self.cL3[l5] = self.model.addConstr(self.f.sum("ALPHA", "*", l5) <= cap, name=f"cL3_{l5}")
                # self.cL4[l5] = self.model.addConstr(self.f.sum("*", "OMEGA", l5) <= cap, name=f"cL4_{l5}")
                self.cL5[l5] = self.model.addConstr(self.f.sum("ALPHA", "*", l5) - self.f.sum("*", "OMEGA", l5) == 0,
                                                    name=f"cL5_{l5}")

        # # source and sink - foreign locos
        # for loco_type in self.foreign_loco_types:
        #     locos_to_be_considered = self.locos_dict_foreign[loco_type]
        #     for l7 in locos_to_be_considered:
        #         l_str = l7.replace(" ", "")
        #         self.cL3[l7] = self.model.addConstr(self.f.sum("ALPHA", "*", l7) <= 1, name=f"cL3_{l_str}")
        #         self.cL4[l7] = self.model.addConstr(self.f.sum("*", "OMEGA", l7) <= 1, name=f"cL4_{l_str}")
        #         self.cL5[l7] = self.model.addConstr(self.f.sum("ALPHA", "*", l7) - self.f.sum("*", "OMEGA", l7) == 0,
        #                                             name=f"cL5_{l_str}")

        print("C3", len(self.cL3))
        print("C4", len(self.cL4))
        print("C5", len(self.cL5))




    def generate_loco_model(self):
        timestamp1 = time.time()
        id = random.randint(0, 999999)
        self.generate_network()
        self.generate_variables()
        self.generate_constraints()
        # dir_name = os.path.basename(os.getcwd())
        # today = date.today()
        self.model.setObjective(self.lmbda.sum("*"), grb.GRB.MAXIMIZE)
        # self.model.setParam('SolFiles', f"solutions_{today}_{dir_name}_loco")
        # self.model.setParam('SolFiles', f"loco_solution_{id}")
        # self.model.setParam('LogFile', f"gurobi_{today}_{dir_name}_loco.log")

        f = grb.tupledict()
        for [t1, t2, l, var_name] in self.f_index_list[:]:
            if self.model.getVarByName(var_name) is not None:
                f[t1, t2, l] = self.model.getVarByName(var_name)
            else:
                self.f_index_list.remove([t1, t2, l, var_name])


        timestamp2 = time.time()
        time_taken = timestamp2 - timestamp1
        print(f"The whole process took {time_taken:.2f} seconds.")
        if self.controller is not None:
            return self.model, self.f_index_list, self.drivers_l, self.lmbda_index_list, self.locos_dict, self.network
        else:
            return self.model, self.f_index_list, self.lmbda_index_list

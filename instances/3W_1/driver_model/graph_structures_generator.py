# -*- coding: utf-8 -*
import time
import networkx as nx
# from clique_heuristics.clique_heuristics import greedy_max_clique_cover
# import pickle
from driver_model.constraints_hybrid_driver import lexicographic_sort


# def lexicographic_sort(list_of_cliques):
#     if type(list_of_cliques) is list:
#         ans = sorted(list_of_cliques)
#         ans = sorted(ans, key=len, reverse=True)
#         return list(ans)
#
#     if type(list_of_cliques) is set:
#         ans = list(list_of_cliques)
#         ans = sorted(ans)
#         ans = sorted(ans, key=len, reverse=True)
#         return list(ans)
#
#     if type(list_of_cliques) is dict:
#         ans = list()
#         for k, v in list_of_cliques.items():
#             ans.append(v)
#         ans = sorted(ans)
#         ans = sorted(ans, key=len, reverse=True)
#         ans = {frozenset(i) for i in ans}
#         return list(ans)


def sorted_max_cliques(list_of_cliques):
    ans1 = []
    for clq in list_of_cliques:
        ans1.append(sorted(clq))
    ans = sorted(ans1)
    ans = sorted(ans, key=len, reverse=True)
    ans = list(ans)
    return ans


def translate_loco_type(in_type):
    if in_type == "3E":
        return "3E - 7"
    elif in_type == "DE6400":
        return "DE6400 - 6495"
    elif in_type == "JT42C":
        return "JT42C - 166"
    elif in_type == "TEM2":
        return "TEM2 - 083"
    elif in_type == "X4EC":
        return "X4EC - 52"
    elif in_type[0:5] == "BR232":
        return "BR232 - 1003"
    elif in_type[0:5] == "ES64F":
        return "ES64F - 1006"
    else:
        return "59E - 1001"


class GraphStructures:

    def __init__(self, sets, variable_structures, time_perspective):
        self.time_perspective = time_perspective
        self.trains = sets["trains"]
        self.long_trains_d_pruned = sets["long_trains_d_pruned"]
        self.trains_d_pruned = sets["trains_d_pruned"]
        self.trains_time_conflict_init = sets["trains_time_conflict_init"]
        self.trains_break_backward_t_d = sets["trains_break_backward_t_d"]
        self.trains_break_forward_t_d = sets["trains_break_forward_t_d"]
        self.trains_break_35h_t_d = sets["trains_break_35h_t_d"]
        self.delta = variable_structures["delta"]
        self.y = variable_structures["y"]
        self.v = variable_structures["v"]
        self.delta_index_list = variable_structures["delta_index_list"]
        self.y_index_list = variable_structures["y_index_list"]
        self.v_index_list = variable_structures["v_index_list"]
        if self.time_perspective in {"weekly", "monthly"}:
            self.z = variable_structures["z"]
            self.z_index_list = variable_structures["z_index_list"]

        self.trains_time_conflict_d = dict()
        self.drivers_conflict_graphs = dict()
        self.input_for_matrix_c3 = []
        self.sets_for_c18_d = dict()
        self.input_for_matrix_c18 = []
        self.sets_for_c20_d = dict()
        self.input_for_matrix_c20 = []
        self.sets_for_c24_d = dict()
        self.input_for_matrix_c24 = []

        self.master_graph = nx.Graph()
        self.cliques = set()

    def generate_trains_time_conflict_d(self):

        g = nx.Graph()
        # g.add_nodes_from([item[0] for item in self.trains])
        for train in self.trains:
            t_id = train[0]
            for c in self.trains_time_conflict_init["all_trains"][t_id]:
                if c != t_id:
                    g.add_edge(t_id, c)
                    self.master_graph.add_edge(t_id, c)

        self.input_for_matrix_c3 = sorted_max_cliques(list(nx.find_cliques(g)))
        # self.input_for_matrix_c3 = greedy_max_clique_cover(g)
        self.input_for_matrix_c3 = set([frozenset(i) for i in self.input_for_matrix_c3])
        self.input_for_matrix_c3 = lexicographic_sort(self.input_for_matrix_c3)

        for i in self.input_for_matrix_c3:
            self.cliques.add(frozenset(i))

        for driver, driver_trains in self.long_trains_d_pruned.items():
            dt = set([i[0] for i in driver_trains])
            max_clqs = []
            for mc in self.input_for_matrix_c3:
                limited_clique = {i for i in mc if i in dt}
                if limited_clique:
                    max_clqs.append(limited_clique)

            self.trains_time_conflict_d[driver] = sorted_max_cliques(max_clqs)

        # pickle.dump(self.trains_time_conflict_d, open("ttc2.p", "wb"))



    def generate_set_for_constraint_c18(self):
        g1 = nx.Graph()

        # g.add_nodes_from([item[0] for item in self.trains])
        for train in self.trains:
            t_id = train[0]
            for c in self.trains_break_backward_t_d["all_trains"][t_id]:
                if c != t_id:
                    g1.add_edge(("y", t_id), ("delta", c))
                    g1.add_edge(("y", t_id), ("y", c))
                    self.master_graph.add_edge(t_id, c)
                    # self.master_graph.add_edge(("y", t_id), ("y", c))
        # self.input_for_matrix_c18 = greedy_max_clique_cover(g1) # list(nx.find_cliques(g1))
        self.input_for_matrix_c18 = sorted_max_cliques(list(nx.find_cliques(g1)))
        self.input_for_matrix_c18 = set([frozenset(i) for i in self.input_for_matrix_c18])
        self.input_for_matrix_c18 = lexicographic_sort(self.input_for_matrix_c18)

        for driver, _ in self.trains_d_pruned.items():
            # print(f"C18 - Now considering {driver} of 217")
            ys = {i[0] for i in self.y_index_list if i[1] == driver}
            deltas = {i[0] for i in self.delta_index_list if i[1] == driver}
            clqs = []
            for c in self.input_for_matrix_c18:
                clq = []
                for v in c:
                    (v_type, t) = v
                    if v_type == "delta" and t in deltas:
                        clq.append(f"delta_{t}_{driver}")
                    if v_type == "y" and t in ys:
                        clq.append(f"y_{t}_{driver}")
                if len(clq) <= 1:
                    continue
                clqs.append(clq)

            self.sets_for_c18_d[driver] = clqs

        for i in self.input_for_matrix_c18:
            self.cliques.add(frozenset(i))


    def generate_set_for_constraint_c20(self):
        g1 = nx.Graph()

         # g.add_nodes_from([item[0] for item in self.trains])
        for train in self.trains:
            t_id = train[0]
            for c in self.trains_break_forward_t_d["all_trains"][t_id]:
                if c != t_id:
                    g1.add_edge(("v", t_id), ("delta", c))
                    g1.add_edge(("v", t_id), ("v", c))
                    # self.master_graph.add_edge(("v", t_id), ("delta", c))
                    # self.master_graph.add_edge(("v", t_id), ("v", c))
                    self.master_graph.add_edge(t_id, c)
        # self.input_for_matrix_c20 = greedy_max_clique_cover(g1) # list(nx.find_cliques(g1))
        self.input_for_matrix_c20 = sorted_max_cliques(list(nx.find_cliques(g1)))
        self.input_for_matrix_c20 = set([frozenset(i) for i in self.input_for_matrix_c20])
        self.input_for_matrix_c20 = lexicographic_sort(self.input_for_matrix_c20)

        for driver, _ in self.trains_d_pruned.items():
            vs = {i[0] for i in self.v_index_list if i[1] == driver}
            deltas = {i[0] for i in self.delta_index_list if i[1] == driver}
            clqs = []
            for c in self.input_for_matrix_c20:
                clq = []
                for v in c:
                    (v_type, t) = v
                    if v_type == "delta" and t in deltas:
                        clq.append(f"delta_{t}_{driver}")
                    if v_type == "v" and t in vs:
                        clq.append(f"v_{t}_{driver}")
                if len(clq) <= 1:
                    continue
                clqs.append(clq)
            self.sets_for_c20_d[driver] = clqs

        for i in self.input_for_matrix_c20:
            self.cliques.add(frozenset(i))


    def generate_set_for_constraint_c24(self):
        g1 = nx.Graph()
        # g.add_nodes_from([item[0] for item in self.trains])
        for train in self.trains:
            t_id = train[0]
            for c in self.trains_break_35h_t_d["all_trains"][t_id]:
                if c != t_id:
                    g1.add_edge(("z", t_id), ("delta", c))
                    g1.add_edge(("z", t_id), ("z", c))
                    # self.master_graph.add_edge(("z", t_id), ("delta", c))
                    # self.master_graph.add_edge(("z", t_id), ("z", c))
                    self.master_graph.add_edge(t_id, c)

        # self.input_for_matrix_c24 = greedy_max_clique_cover(g1)
        self.input_for_matrix_c24 = lexicographic_sort(list(nx.find_cliques(g1)))
        self.input_for_matrix_c24 = set([frozenset(i) for i in self.input_for_matrix_c24])
        self.input_for_matrix_c24 = lexicographic_sort(self.input_for_matrix_c24)

        for driver, _ in self.trains_d_pruned.items():
            zs = {i[0] for i in self.z_index_list if i[1] == driver}
            deltas = {i[0] for i in self.delta_index_list if i[1] == driver}
            clqs = []
            for c in self.input_for_matrix_c24:
                clq = []
                for v in c:
                    (v_type, t) = v
                    if v_type == "delta" and t in deltas:
                        clq.append(f"delta_{t}_{driver}")
                    if v_type == "z" and t in zs:
                        clq.append(f"z_{t}_{driver}")
                if len(clq) <= 1:
                    continue
                clqs.append(clq)
            self.sets_for_c24_d[driver] = clqs

        # for i in self.input_for_matrix_c24:
        #     self.cliques.add(frozenset(i))


    def generate_set_structures(self):
        self.time1 = time.time()
        self.generate_trains_time_conflict_d()
        time2 = time.time()
        print(f"C3: {len(self.input_for_matrix_c3)} {time2-self.time1:.2f} seconds")
        self.generate_set_for_constraint_c18()
        time3 = time.time()
        print(f"C18: {len(self.input_for_matrix_c18)} {time3-time2:.2f} seconds")
        self.generate_set_for_constraint_c20()
        time4 = time.time()
        print(f"C20: {len(self.input_for_matrix_c20)} {time4-time3:.2f} seconds")

        if self.time_perspective in {"weekly", "monthly"}:
            self.generate_set_for_constraint_c24()
            time5 = time.time()
            print(f"C24: {len(self.input_for_matrix_c24)} {time5-time4:.2f} seconds")

        # self.cliques = list(nx.find_cliques(self.master_graph))


    def get_graph_structures(self):
        answer1 = dict(self.__dict__)



        clqs = lexicographic_sort(self.cliques)
        ans_cliques = []

        for clq in clqs:
            clq = list(clq)
            if type(clq[0]) is tuple:
                clq_temp = set()
                for t in clq:
                    clq_temp.add(t[1])

            else:
                clq_temp = set(clq)

            if clq_temp in ans_cliques:
                continue
            subset_indicator = 0
            for clq1 in ans_cliques:
                if clq_temp.issubset(clq1):
                    subset_indicator += 1
                    break
            if subset_indicator > 0:
                continue

            ans_cliques.append(clq_temp)

        self.cliques = ans_cliques
        time_end = time.time()
        print(f"Graph structures for constraints and cutting planes generated in {time_end - self.time1:.2f} seconds")
        return answer1, self.cliques


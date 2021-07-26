import networkx as nx
import time

def lexicographic_sort(list_of_cliques):
    if type(list_of_cliques) is list:
        ans = sorted(list_of_cliques)
        ans = sorted(ans, key=len, reverse=True)
        return list(ans)

    if type(list_of_cliques) is set:
        ans = list(list_of_cliques)
        ans = sorted(ans)
        ans = sorted(ans, key=len, reverse=True)
        return list(ans)

    if type(list_of_cliques) is dict:
        ans = list()
        for k, v in list_of_cliques.items():
            ans.append(v)
        ans = sorted(ans)
        ans = sorted(ans, key=len, reverse=True)
        ans = {frozenset(i) for i in ans}
        return list(ans)


def sorted_max_cliques(list_of_cliques):
    ans1 = []
    for clq in list_of_cliques:
        ans1.append(sorted(clq))
    ans = sorted(ans1)
    ans = sorted(ans, key=len, reverse=True)
    ans = list(ans)
    return ans


def generate_trains_time_conflict_d(trains, long_trains_d_pruned, trains_time_conflict_init, cliques):
    time1 = time.time()
    no_of_cliques = 0
    trains_time_conflict_d = dict()
    g = nx.Graph()
    # g.add_nodes_from([item[0] for item in self.trains])
    for train in trains:
        t_id = train[0]
        for c in trains_time_conflict_init["all_trains"][t_id]:
            if c != t_id:
                g.add_edge(t_id, c)

    input_for_matrix_c3 = sorted_max_cliques(list(nx.find_cliques(g)))
    # self.input_for_matrix_c3 = greedy_max_clique_cover(g)
    input_for_matrix_c3 = set([frozenset(i) for i in input_for_matrix_c3])
    input_for_matrix_c3 = lexicographic_sort(input_for_matrix_c3)
    no_of_cliques += len(input_for_matrix_c3)

    # for i in input_for_matrix_c3:
    #     cliques.add(frozenset(i))

    for driver, driver_trains in long_trains_d_pruned.items():
        dt = set([i[0] for i in driver_trains])
        max_clqs = []
        for mc in input_for_matrix_c3:
            limited_clique = {i for i in mc if i in dt}
            if limited_clique:
                max_clqs.append(limited_clique)

        trains_time_conflict_d[driver] = sorted_max_cliques(max_clqs)
    print(f"Generation of time-conflict-based cliques took {time.time() - time1:.2f} seconds to generate {no_of_cliques} cliques")
    return trains_time_conflict_d, cliques

    # pickle.dump(self.trains_time_conflict_d, open("ttc2.p", "wb"))


def generate_set_for_constraint_c18(trains, trains_d_pruned, trains_break_backward_t_d, trains_time_conflict_init, delta_index_list, cliques):
    time1 = time.time()
    g1 = nx.Graph()
    sets_for_c18_d = dict()
    no_of_cliques = len(cliques)
    # g.add_nodes_from([item[0] for item in self.trains])
    for train in trains:
        t_id = train[0]
        for c in trains_break_backward_t_d["all_trains"][t_id]:
            if c != t_id:
                g1.add_edge(("y", t_id), ("delta", c))
                g1.add_edge(("y", t_id), ("y", c))
        # for c1 in trains_time_conflict_init["all_trains"][t_id]:
        #     if c1 != t_id:
        #         g1.add_edge(("y", t_id), ("y", c1))
        #         g1.add_edge(("delta", t_id), ("delta", c1))
                # self.master_graph.add_edge(("y", t_id), ("y", c))
    # self.input_for_matrix_c18 = greedy_max_clique_cover(g1) # list(nx.find_cliques(g1))
    input_for_matrix_c18 = sorted_max_cliques(list(nx.find_cliques(g1)))
    input_for_matrix_c18 = set([frozenset(i) for i in input_for_matrix_c18])
    input_for_matrix_c18 = lexicographic_sort(input_for_matrix_c18)

    for driver, _ in trains_d_pruned.items():
        # print(f"C18 - Now considering {driver} of 217")
        ys = {i[0] for i in delta_index_list if i[1] == driver}
        deltas = {i[0] for i in delta_index_list if i[1] == driver}
        clqs = []
        for c in input_for_matrix_c18:
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

        sets_for_c18_d[driver] = clqs

    for i in input_for_matrix_c18:
        cliques.add(frozenset([j[1] for j in i]))

    new_no_cliques = len(cliques)
    print(f"Generation of backward-break-based cliques took {time.time() - time1:.2f} seconds to generate {new_no_cliques - no_of_cliques} cliques")
    return sets_for_c18_d, cliques


def generate_set_for_constraint_c20(trains, trains_d_pruned, trains_break_forward_t_d, trains_time_conflict_init, delta_index_list, cliques):
    time1 = time.time()
    g1 = nx.Graph()
    sets_for_c20_d = dict()
    no_of_cliques = len(cliques)
    # g.add_nodes_from([item[0] for item in self.trains])
    for train in trains:
        t_id = train[0]
        for c in trains_break_forward_t_d["all_trains"][t_id]:
            if c != t_id:
                g1.add_edge(("v", t_id), ("delta", c))
                g1.add_edge(("v", t_id), ("v", c))

        # for c1 in trains_time_conflict_init["all_trains"][t_id]:
        #     if c1 != t_id:
        #         g1.add_edge(("v", t_id), ("v", c1))
        #         g1.add_edge(("delta", t_id), ("delta", c1))
    input_for_matrix_c20 = sorted_max_cliques(list(nx.find_cliques(g1)))
    input_for_matrix_c20 = set([frozenset(i) for i in input_for_matrix_c20])
    input_for_matrix_c20 = lexicographic_sort(input_for_matrix_c20)

    for driver, _ in trains_d_pruned.items():
        vs = {i[0] for i in delta_index_list if i[1] == driver}
        deltas = {i[0] for i in delta_index_list if i[1] == driver}
        clqs = []
        for c in input_for_matrix_c20:
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
        sets_for_c20_d[driver] = clqs

    for i in input_for_matrix_c20:
        cliques.add(frozenset([j[1] for j in i]))

    new_no_cliques = len(cliques)
    print(f"Generation of forward-break-based cliques took {time.time() - time1:.2f} seconds to generate {new_no_cliques - no_of_cliques} cliques")
    return sets_for_c20_d, cliques


def generate_set_for_constraint_c24(trains, trains_d_pruned, trains_break_35h_t_d, trains_time_conflict_init, delta_index_list, z_index_list, cliques):
    time1 = time.time()
    g1 = nx.Graph()
    sets_for_c24_d = dict()
    no_of_cliques = len(cliques)
    # g.add_nodes_from([item[0] for item in self.trains])
    for train in trains:
        t_id = train[0]
        for c in trains_break_35h_t_d["all_trains"][t_id]:
            if c != t_id:
                g1.add_edge(("z", t_id), ("delta", c))
                g1.add_edge(("z", t_id), ("z", c))
                # self.master_graph.add_edge(("z", t_id), ("delta", c))
                # self.master_graph.add_edge(("z", t_id), ("z", c))

    # self.input_for_matrix_c24 = greedy_max_clique_cover(g1)
    input_for_matrix_c24 = lexicographic_sort(list(nx.find_cliques(g1)))
    input_for_matrix_c24 = set([frozenset(i) for i in input_for_matrix_c24])
    input_for_matrix_c24 = lexicographic_sort(input_for_matrix_c24)

    for driver, _ in trains_d_pruned.items():
        zs = {i[0] for i in z_index_list if i[1] == driver}
        deltas = {i[0] for i in delta_index_list if i[1] == driver}
        clqs = []
        for c in input_for_matrix_c24:
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
        sets_for_c24_d[driver] = clqs

        for i in input_for_matrix_c24:
            cliques.add(frozenset([j[1] for j in i]))
    new_no_cliques = len(cliques)
    print(f"Generation of long-break-based cliques took {time.time() - time1:.2f} seconds to generate {new_no_cliques - no_of_cliques} cliques")
    return sets_for_c24_d, cliques
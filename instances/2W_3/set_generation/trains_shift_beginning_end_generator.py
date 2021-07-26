import time
import networkx as nx


def generate_trains_prev_shift_beginning_end_t_d(trains_d_pruned, trains_next_t_d, all_trains):
    time1 = time.time()
    trains_shift_end_t_d = dict()
    trains_shift_beginning_t_d = dict()
    trains_previous_t_d = dict()
    for driver, trains in trains_d_pruned.items():
        trains_shift_end_t_d[driver] = dict()
        trains_shift_beginning_t_d[driver] = dict()
        trains_previous_t_d[driver] = dict()
        g1 = nx.DiGraph()
        g1.add_nodes_from(trains)
        # g2 = nx.DiGraph()
        # g2.add_nodes_from(trains)
        for t in trains:
            next_trains = trains_next_t_d[driver][t]
            ts1 = [t for _ in range(len(next_trains))]
            g1.add_edges_from(list(zip(ts1, next_trains)))

            # prev_trains = trains_previous_t_d[driver][t]
            # ts2 = [t for _ in range(len(prev_trains))]
            # g2.add_edges_from(list(zip(ts2, prev_trains)))

        for t in trains:
            t_b = all_trains[t]["begin"]
            t_e = all_trains[t]["end"]

            trains_shift_end_t_d[driver][t] = [i for i in list(nx.descendants(g1, t))
                                                    if float(all_trains[i]["end"]) <= float(t_b) + 0.5]
            trains_shift_end_t_d[driver][t].append(t)

            trains_shift_beginning_t_d[driver][t] = [j for j in list(nx.ancestors(g1, t))
                                                          if float(all_trains[j]["begin"]) >= float(t_e) - 0.5]
            trains_shift_beginning_t_d[driver][t].append(t)

            trains_previous_t_d[driver][t] = [j for j in g1.predecessors(t)]

    time2 = time.time() - time1
    print(f"trains_shift_beginning_t_d & trains_shift_end_t_d: {time2:.2f}")
    return trains_shift_beginning_t_d, trains_shift_end_t_d, trains_previous_t_d


def generate_common_beginnings_t_d(trains_shift_beginning_t_d):
    t_start = time.time()
    common_beginnings_t_d = dict()
    for driver, trains in trains_shift_beginning_t_d.items():
        common_beginnings_t_d[driver] = {}

        trains_copy = trains
        for t, block in trains.items():
            if block is None:
                continue
            answer2 = [t]

            for t1, block1 in trains_copy.items():
                if block == block1 and len(block) > 0:
                    answer2.append(t1)
            common_beginnings_t_d[driver][t] = set(answer2)
    t2 = time.time() - t_start
    print(f"common_beginnings_t_d: {t2:.2f}")
    return common_beginnings_t_d


def generate_common_ends_t_d(trains_shift_end_t_d):
    t0 = time.time()
    common_ends_t_d = dict()
    for driver, trains in trains_shift_end_t_d.items():
        common_ends_t_d[driver] = {}

        trains_copy = trains
        for t, block in trains.items():
            if block is None:
                continue
            ans13 = [t]
            for t1, block1 in trains_copy.items():
                if block == block1 and len(block) > 0:
                    ans13.append(t1)
            common_ends_t_d[driver][t] = set(ans13)
    t2 = time.time() - t0
    print(f"common_ends_t_d: {t2:.2f}")
    return common_ends_t_d
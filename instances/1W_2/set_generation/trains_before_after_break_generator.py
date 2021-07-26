import time
import networkx as nx


def generate_trains_before_after_break_t_d(long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_after_break_t_d = dict()
    trains_before_break_t_d = dict()
    for driver, trains in long_trains_d_pruned.items():
        g = nx.DiGraph()
        trains_after_break_t_d[driver] = {}
        trains_before_break_t_d[driver] = {}
        for train in trains:
            train_id = train[0]
            g.add_node(train_id)
            train_end = float(train[6])
            train_arr_station = train[5]

            # ans1 = set(
            #     [item[0] for item in long_trains_d_pruned[driver] if
            #      float(item[4]) > train_end + (11 / 24) and
            #      (item[3] == train_arr_station)])

            ans3 = set()

            for i in trains:
                if float(i[4]) <= train_end + (11 / 24):
                    continue
                if i[3] == train_arr_station and float(i[4]) > train_end + (11 / 24):
                    ans3.add(i[0])
                elif train_arr_station in neighborhood_set.keys() and \
                        i[3] in neighborhood_set[train_arr_station].keys():
                    transit_time = float(neighborhood_set[train_arr_station][i[3]])
                    if float(i[4]) > (train_end + (11 / 24) + transit_time):
                        ans3.add(i[0])

                else:
                    transit_time = float(neighborhood_set[i[3]][train_arr_station])
                    if float(i[4]) > (train_end + (11 / 24) + transit_time):
                        ans3.add(i[0])

            trains_after_break_t_d[driver][train_id] = ans3
            g.add_edges_from([(train_id, t1) for t1 in ans3])

        for train in trains:
            train_id = train[0]
            trains_before_break_t_d[driver][train_id] = [j for j in g.predecessors(train_id)]
    t2 = time.time() - t1
    print(f"trains_before_after_break_t_d: {t2:.2f}")
    return trains_after_break_t_d, trains_before_break_t_d


# def generate_trains_before_break_t_d(long_trains_d_pruned, neighborhood_set):
#     trains_before_break_t_d = dict()
#     t1 = time.time()
#     for driver, trains in long_trains_d_pruned.items():
#         trains_before_break_t_d[driver] = {}
#         for train in trains:
#             train_id = train[0]
#             train_beg = float(train[4])
#             train_org_station = train[3]
#
#             ans1 = set(
#                 [item[0] for item in long_trains_d_pruned[driver] if
#                  float(item[6]) <= train_beg - (11 / 24) and
#                  item[5] == train_org_station])
#
#             ans2 = []
#
#             for i in trains:
#                 if train_org_station in neighborhood_set.keys() and \
#                         i[5] in neighborhood_set[train_org_station].keys():
#                     transit_time = float(neighborhood_set[train_org_station][i[5]])
#
#                 else:
#                     transit_time = float(neighborhood_set[i[5]][train_org_station])
#
#                 if float(i[6]) <= (train_beg - (11 / 24) - transit_time):
#                     ans2.append(str(i[0]))
#
#             ans3 = ans1.union(set(ans2))
#
#             trains_before_break_t_d[driver][train_id] = ans3
#     t2 = time.time() - t1
#     print(f"trains_before_break_t_d: {t2:.2f}")
#     return trains_before_break_t_d

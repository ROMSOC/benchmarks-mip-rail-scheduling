import time

def generate_trains_break_forward_t_d(trains_arg, long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_break_forward_t_d = dict()
    trains_break_forward_t_d["all_trains"] = dict()

    for train in trains_arg:
        t_id = train[0]
        arr = float(train[6])
        train_arr_station = train[5]
        input1 = [item[0] for item in trains_arg if
                  float(item[4]) >= arr and float(item[6]) <= arr + (11 / 24)]
        input2 = [item[0] for item in trains_arg if float(item[4]) >= arr and
                  float(item[4]) <= arr + (11 / 24) and float(item[6]) >= arr + (11 / 24)]
        input4 = [item[0] for item in trains_arg if
                  float(item[4]) < arr and float(item[6]) >= arr + (11 / 24)]

        input5 = []
        for i in trains_arg:

            if train_arr_station in neighborhood_set.keys() and \
                    i[3] in neighborhood_set[train_arr_station].keys():
                transit_time = float(neighborhood_set[train_arr_station][i[3]])

            else:
                transit_time = float(neighborhood_set[i[3]][train_arr_station])

            if (arr + 11 / 24 + transit_time) > float(i[4]) and int(i[0]) >= int(t_id):
                input5.append(i[0])

        entry = input1 + input2 + input4 + input5
        entry = set(entry)
        if t_id in entry:
            entry.remove(t_id)
        trains_break_forward_t_d["all_trains"][t_id] = entry

    for driver, driver_trains in long_trains_d_pruned.items():
        trains_break_forward_t_d[driver] = dict()
        dt = [i[0] for i in driver_trains]
        for train in driver_trains:
            t_id = train[0]
            trains_break_forward_t_d[driver][t_id] = {i for i in trains_break_forward_t_d["all_trains"][t_id]
                                                      if i in dt}

    t2 = time.time() - t1
    print(f"trains_break_forward_t_d: {t2:.2f}")
    return trains_break_forward_t_d



def generate_trains_break_35h_t_d(trains_arg, long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_break_35h_t_d = dict()
    trains_break_35h_t_d["all_trains"] = dict()

    travel_times_between_stations = []
    for train in trains_arg:
        train_1_arr_station = train[5]
        for i in trains_arg:
            train_2_dep_station = i[3]
            if train_1_arr_station in neighborhood_set.keys() and train_2_dep_station in neighborhood_set[train_1_arr_station].keys():
                travel_times_between_stations.append(float(neighborhood_set[train_1_arr_station][train_2_dep_station]))

            else:
                travel_times_between_stations.append(float(neighborhood_set[train_2_dep_station][train_1_arr_station]))

    heur_transit_time = float(max(travel_times_between_stations))

    for train in trains_arg:
        t_id = train[0]
        arr = float(train[6])
        # train_arr_station = train[5]
        input1 = [item[0] for item in trains_arg if
                  float(item[4]) >= arr and float(item[6]) <= arr + (35 / 24)]
        input2 = [item[0] for item in trains_arg if
                  float(item[4]) > arr and float(item[4]) <= arr + (35 / 24)
                  and float(item[6]) >= arr + 35 / 24]

        input5 = []
        for i in trains_arg:
            # if train_arr_station in neighborhood_set.keys() and \
            #         i[3] in neighborhood_set[train_arr_station].keys():
            #     transit_time = float(neighborhood_set[train_arr_station][i[3]])
            #
            # else:
            #     transit_time = float(neighborhood_set[i[3]][train_arr_station])

            if (arr + 35 / 24 + heur_transit_time) > float(i[4]) and int(i[0]) >= int(t_id):
                input5.append(i[0])

        entry = input1 + input2 + input5
        entry = set(entry)
        if t_id in entry:
            entry.remove(t_id)
        trains_break_35h_t_d["all_trains"][t_id] = entry

    for driver, driver_trains in long_trains_d_pruned.items():
        trains_break_35h_t_d[driver] = dict()
        dt = {i[0] for i in driver_trains}
        for train in driver_trains:
            t_id = train[0]
            trains_break_35h_t_d[driver][t_id] = {i for i in trains_break_35h_t_d["all_trains"][t_id]
                                                  if i in dt}

    t2 = time.time() - t1
    print(f"trains_break_35h_t_d: {t2:.2f}")
    return trains_break_35h_t_d


def generate_trains_break_backward_t_d(trains_arg, long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_break_backward_t_d = dict()
    trains_break_backward_t_d["all_trains"] = dict()
    for train in trains_arg:
        t_id = train[0]
        train_org_station = train[3]
        dep = float(train[4])
        input1 = [item[0] for item in trains_arg if
                  float(item[4]) <= dep - (11 / 24) and float(item[6]) >= dep - (11 / 24) and float(
                      item[6]) <= dep]
        input2 = [item[0] for item in trains_arg if
                  float(item[4]) >= dep - (11 / 24) and float(item[6]) <= dep]
        input4 = [item[0] for item in trains_arg if
                  float(item[4]) <= (dep - 11 / 24) and float(item[6]) >= dep]

        input5 = []
        for i in trains_arg:
            if int(i[0]) > int(t_id):
                continue
            if train_org_station in neighborhood_set.keys() and \
                    i[5] in neighborhood_set[train_org_station].keys():
                transit_time = float(neighborhood_set[train_org_station][i[5]])
            else:
                transit_time = float(neighborhood_set[i[5]][train_org_station])
            if (dep - 11 / 24 - transit_time) < float(i[6]):
                input5.append(i[0])

        entry = input1 + input2 + input4 + input5
        entry = set(entry)
        if t_id in entry:
            entry.remove(t_id)
        trains_break_backward_t_d["all_trains"][t_id] = entry


    for driver, driver_trains in long_trains_d_pruned.items():
        trains_break_backward_t_d[driver] = {}
        dt = [i[0] for i in driver_trains]
        for train in dt:
            trains_break_backward_t_d[driver][train] = {i for i in trains_break_backward_t_d["all_trains"][train]
                                                           if i in dt}

    t2 = time.time() - t1
    print(f"trains_break_backward_t_d: {t2:.2f}")
    return trains_break_backward_t_d

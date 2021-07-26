import time


def generate_trains_time_conflict_init(trains_arg, neighborhood_set, long_trains_d_pruned, trains_d_pruned):
    t1 = time.time()
    trains_time_conflict_init = dict()
    trains_time_conflict_init["all_trains"] = {}
    for train in trains_arg:
        t_id = train[0]

        t_beg = float(train[4])
        t_end = float(train[6])
        t_dest = train[5]

        conf1 = [i[0] for i in trains_arg if
                 float(i[4]) <= t_beg and float(i[6]) >= t_end]
        conf2 = [i[0] for i in trains_arg if
                 float(i[4]) >= t_beg and float(i[4]) <= t_end and float(i[6]) >= t_end]
        conf3 = [i[0] for i in trains_arg if
                 float(i[4]) <= t_beg and float(i[6]) >= t_beg and float(i[6]) <= t_end]
        conf4 = [i[0] for i in trains_arg if
                 float(i[4]) >= t_beg and float(i[6]) <= t_end]
        conf5 = []
        for i in trains_arg:
            try:
                transit_time = neighborhood_set[t_dest][i[3]]
            except KeyError:
                transit_time = neighborhood_set[i[3]][t_dest]
                if t_end + transit_time > float(i[4]) and float(i[6]) <= t_beg + 0.5 and int(i[0]) > int(t_id):
                    conf5.append(i[0])
            else:
                if t_end + transit_time > float(i[4]) and float(i[6]) <= t_beg + 0.5 and int(i[0]) > int(t_id):
                    conf5.append(i[0])

        conflicting_trains_1 = conf1 + conf2 + conf3 + conf4 + conf5
        conflicting_trains_1 = set(conflicting_trains_1)
        conflicting_trains_1.remove(t_id)
        if len(conflicting_trains_1) == 0:
            trains_time_conflict_init["all_trains"][t_id] = set()
        else:
            trains_time_conflict_init["all_trains"][t_id] = conflicting_trains_1


    for driver, trains in long_trains_d_pruned.items():

        trains_time_conflict_init[driver] = {}

        for train in trains:
            t_id = train[0]
            trains_time_conflict_init[driver][t_id] = [i for i in trains_time_conflict_init["all_trains"][t_id]
                                                       if i in trains_d_pruned[driver]]
    t2 = time.time() - t1

    print(f"trains_time_conflict_d: {t2:.2f}")
    return trains_time_conflict_init
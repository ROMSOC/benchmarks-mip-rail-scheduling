import time

def generate_trains_previous_t_d(long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_previous_t_d = dict()
    for driver, trains in long_trains_d_pruned.items():
        trains_previous_t_d[driver] = {}
        for train in trains:
            train_id = train[0]
            train_beginning = float(train[4])
            train_end = float(train[6])
            train_origin = train[3]
            ans = set()
            for item in long_trains_d_pruned[driver]:
                if float(item[4]) > float(train_end) - 0.5 and float(item[6]) < train_beginning and item[5] == train_origin:
                    ans.add(item[0])

            # previous_jobs1 = [item[0] for item in long_trains_d_pruned[driver] if
            #                   float(item[4]) > float(train_end) - 0.5 and float(item[6]) < train_beginning
            #                   and item[5] == train_origin]
                elif train_origin in neighborhood_set.keys() and item[5] in neighborhood_set[train_origin].keys():
                    transit_time = neighborhood_set[train_origin][item[5]]
                    if float(item[4]) > float(train_end) - 0.5 and float(item[6]) + transit_time < train_beginning:
                        ans.add(item[0])

                else:
                    transit_time = neighborhood_set[item[5]][train_origin]
                    if float(item[4]) > float(train_end) - 0.5 and float(item[6]) + transit_time < train_beginning:
                        ans.add(item[0])
            # previous_jobs2 = []
            # for i in trains:
            #     try:
            #         transit_time = neighborhood_set[train_origin][i[5]]
            #     except KeyError:
            #         transit_time = neighborhood_set[i[5]][train_origin]
            #         if float(i[4]) > float(train_end) - 0.5 and float(i[6]) + transit_time < train_beginning:
            #             previous_jobs2.append(i[0])
            #     else:
            #         if float(i[4]) > float(train_end) - 0.5 and float(i[6]) + transit_time < train_beginning:
            #             previous_jobs2.append(i[0])
            #
            # trains_previous_t_d[driver][train_id] = previous_jobs1 + previous_jobs2
            trains_previous_t_d[driver][train_id] = ans

    t2 = time.time() - t1
    print(f"trains_previous_t_d: {t2:.2f}")
    return trains_previous_t_d


def generate_trains_next_t_d(long_trains_d_pruned, neighborhood_set):
    t1 = time.time()
    trains_next_t_d = dict()
    for driver, trains in long_trains_d_pruned.items():
        trains_next_t_d[driver] = {}
        for train in trains:
            train_id = train[0]
            train_beginning = float(train[4])
            train_end = float(train[6])
            train_destination = train[5]
            ans = set()
            for item in long_trains_d_pruned[driver]:
                if int(item[0]) <= int(train_id):
                    continue
                if float(item[4]) > float(train_beginning) + 0.5:
                    continue
                if float(item[4]) > float(train_end) and float(item[6]) < train_beginning + 0.5 and item[3] == train_destination:
                    ans.add(item[0])

                elif train_destination in neighborhood_set.keys() and item[3] in neighborhood_set[train_destination].keys():
                    transit_time = neighborhood_set[train_destination][item[3]]
                    if float(item[4]) > (train_end + transit_time) and float(item[6]) <= train_beginning + 0.5:
                        ans.add(item[0])

                else:
                    transit_time = neighborhood_set[item[3]][train_destination]
                    if float(item[4]) > (train_end + transit_time) and float(item[6]) <= train_beginning + 0.5:
                        ans.add(item[0])



            # next_jobs1 = [item[0] for item in long_trains_d_pruned[driver] if
            #               float(item[4]) > float(train_end) and float(item[6]) < train_beginning + 0.5
            #               and item[3] == train_destination]
            #
            # next_jobs2 = []
            # for i in trains:
            #     try:
            #         transit_time = neighborhood_set[train_destination][i[3]]
            #
            #     except KeyError:
            #         transit_time = neighborhood_set[i[3]][train_destination]
            #         if float(i[4]) > (train_end + transit_time) and float(i[6]) <= train_beginning + 0.5:
            #             next_jobs2.append(i[0])
            #     else:
            #         if float(i[4]) > (train_end + transit_time) and float(i[6]) <= train_beginning + 0.5:
            #             next_jobs2.append(i[0])

            # trains_next_t_d[driver][train_id] = next_jobs1 + next_jobs2
            trains_next_t_d[driver][train_id] = ans
    t2 = time.time() - t1
    print(f"trains_next_t_d: {t2:.2f}")
    return trains_next_t_d
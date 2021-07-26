import time


def generate_trains_week_w_d(long_trains_d_pruned):
    t1 = time.time()
    trains_week_w_d = dict()
    weeks = {"1": {"beg": 43862, "end": 43869}, "2": {"beg": 43869, "end": 43876},
             "3": {"beg": 43876, "end": 43883}, "4": {"beg": 43883, "end": 43890}}

    for driver, driver_trains in long_trains_d_pruned.items():
        trains_week_w_d[driver] = dict()
        for i in weeks.keys():
            trains_week_w_d[driver][i] = [item[0] for item in driver_trains
                                                 if (float(item[6]) == weeks[i]["beg"])
                                                 or (float(item[6]) > weeks[i]["beg"]
                                                     and float(item[6]) + 35 / 24 <= weeks[i]["end"])]
    t2 = time.time() - t1
    print(f"trains_week_w_d: {t2:.2f}")
    return trains_week_w_d


def generate_trains_sunday_w_d(long_trains_d_pruned):
    t1 = time.time()
    trains_sunday_w_d = dict()
    sundays = {"1": {"beg": 43863 + (6 / 24), "end": 43863 + (6 / 24) + 1},
               "2": {"beg": 43870 + (6 / 24), "end": 43870 + (6 / 24) + 1},
               "3": {"beg": 43877 + (6 / 24), "end": 43877 + (6 / 24) + 1},
               "4": {"beg": 43884 + (6 / 24), "end": 43884 + (6 / 24) + 1}}

    for driver, driver_trains in long_trains_d_pruned.items():
        trains_sunday_w_d[driver] = dict()
        for i in sundays.keys():

            s1_1 = [item[0] for item in driver_trains if float(item[4]) >= sundays[i]["beg"]
                    and float(item[6]) <= sundays[i]["end"]]
            s1_2 = [item[0] for item in driver_trains if
                    float(item[4]) >= sundays[i]["beg"] and float(item[4]) <= sundays[i]["end"]
                    and float(item[6]) >= sundays[i]["end"]]
            s1_3 = [item[0] for item in driver_trains if
                    float(item[4]) <= sundays[i]["beg"] and float(item[6]) >= sundays[i]["beg"]
                    and float(item[6]) <= sundays[i]["end"]]
            entry1 = s1_1 + s1_2 + s1_3
            entry1 = set(entry1)
            trains_sunday_w_d[driver][i] = entry1

    t2 = time.time() - t1
    print(f"trains_sunday_w_d: {t2:.2f}")
    return trains_sunday_w_d


def generate_train_to_week_attribution(long_trains_d_pruned):
    t0 = time.time()
    train_to_week_attribution = dict()
    weeks = {"1": {"beg": 43862, "end": 43869}, "2": {"beg": 43869, "end": 43876},
             "3": {"beg": 43876, "end": 43883}, "4": {"beg": 43883, "end": 43890}}
    weeks_represented = set()
    for driver, trains in long_trains_d_pruned.items():
        for train in trains:
            weeks_represented.add(train[7])
    for driver, driver_trains in long_trains_d_pruned.items():
        train_to_week_attribution[driver] = dict()
        for i in weeks.keys():
            if i in weeks_represented:
                train_to_week_attribution[driver][i] = [item[0] for item in driver_trains if
                                                               (float(item[6]) >= weeks[i]["beg"] and
                                                                float(item[6]) < weeks[i]["end"])]


    t2 = time.time() - t0
    print(f"train_to_week_attribution: {t2:.2f}")
    return train_to_week_attribution
def generate_long_trains_l(locos, trains):
    long_trains_l = dict()
    loco_types = ["Type5", "Type6", "Type7", "Type3", "Type8", "Type1", "Type4", "Type2"]
    for loco in locos:

        loco_type = loco[13]
        if loco_type in loco_types:
            meta_loco_type = loco[12]

            if meta_loco_type == "H_D":
                long_trains_l[loco[1]] = [item for item in trains if
                                               item[20] in ["H_E", "N_E", "H_D", "N_D"]]
            if meta_loco_type == "H_E":
                long_trains_l[loco[1]] = [item for item in trains if item[20] in ["H_E", "N_E"]]
            if meta_loco_type == "N_D":
                long_trains_l[loco[1]] = [item for item in trains if item[20] in ["N_D", "N_E"]]
            if meta_loco_type == "N_E":
                long_trains_l[loco[1]] = [item for item in trains if item[20] in ["N_E"]]
            if loco_type in ["Type3", "Type1", "Type2"]:
                long_trains_l[loco[1]] = [item for item in trains if item[21] == loco_type]
    return long_trains_l


def generate_trains_next_t_l(locos_master, long_trains_l):
    trains_next_t_l = dict()
    for loco in locos_master:
        trains_for_consideration = long_trains_l[loco]
        trains_next_t_l[loco] = {}
        for train in trains_for_consideration:
            train_id = train[0]
            train_end = float(train[6])
            train_destination = train[5]
            next_jobs1 = [item[0] for item in long_trains_l[loco] if
                          float(item[4]) > float(train_end) and item[3] == train_destination]
            trains_next_t_l[loco][train_id] = next_jobs1

    return trains_next_t_l
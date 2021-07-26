import time


def generate_loco_skill_set(drivers_listed_arg, drivers_listed_header_arg):
    feasible_drivers_dict = dict()
    for loco_requirement in ["Type1", "Type2", "Type3", "Type4", "Type5", "Type6", "Type7", "Type8"]:
        loco_type_index = drivers_listed_header_arg.index(loco_requirement)
        feasible_drivers_dict[loco_requirement] = set([item[2] for item in drivers_listed_arg
                                                       if item[loco_type_index] == "1"])

    return feasible_drivers_dict


def generate_route_skill_set(drivers_listed_arg, drivers_listed_header_arg, trains):
    feasible_route_dict = dict()
    routes = set([i[9] for i in trains])
    for r in routes:
        route_index = drivers_listed_header_arg.index(r)
        feasible_route_dict[r] = set([item[2] for item in drivers_listed_arg if item[route_index] == "1"])

    return feasible_route_dict


def generate_foreign_loco_compatibility_set(train_id, route, drivers_arg, drivers_t, long_drivers_t, drivers_listed,
                                            drivers_listed_header, delta, loco_requirement, locos_appropriate_drivers, route_appropriate_drivers):
    drivers_t[train_id] = route_appropriate_drivers[route]
    long_drivers_t[train_id] = [t for t in drivers_listed if t[0] in route_appropriate_drivers[route]]

    tmp1 = route_appropriate_drivers[route]
    tmp2 = locos_appropriate_drivers[loco_requirement]

    feasible_drivers = tmp1.intersection(tmp2)
    for item in feasible_drivers:
        if [train_id, item, f"delta_{train_id}_{item}"] not in delta:
            delta.append([train_id, item, f"delta_{train_id}_{item}"])

    return delta, drivers_t, long_drivers_t

def generate_own_loco_compatibility_set(train_id_arg, route_arg, meta_loco_requirement_arg, loco_requirement_arg,
                                        drivers_arg, drivers_t_arg, drivers_listed_header_arg, drivers_listed_arg,
                                        delta_arg, long_drivers_t_arg, locos_appropriate_drivers, route_appropriate_drivers):
    drivers_t_arg[train_id_arg] = route_appropriate_drivers[route_arg]
    long_drivers_t_arg[train_id_arg] = [t for t in drivers_listed_arg if t[0] in route_appropriate_drivers[route_arg]]
    tmp1 = route_appropriate_drivers[route_arg]

    if meta_loco_requirement_arg == "H_D":
        tmp2 = set(locos_appropriate_drivers[loco_requirement_arg])
        feasible_drivers = tmp1.intersection(tmp2)


    elif meta_loco_requirement_arg == "H_E":
        feasible_drivers1 = set(locos_appropriate_drivers[loco_requirement_arg]).intersection(tmp1)
        feasible_drivers2 = set(locos_appropriate_drivers["Type4"]).intersection(tmp1)

        feasible_drivers = feasible_drivers1.union(feasible_drivers2)


    elif meta_loco_requirement_arg == "N_E":
        feasible_drivers1 = set(locos_appropriate_drivers[loco_requirement_arg]).intersection(tmp1)


        feasible_drivers2 = set(locos_appropriate_drivers["Type4"]).intersection(tmp1)

        feasible_drivers3 = set(locos_appropriate_drivers["Type7"]).intersection(tmp1)

        feasible_drivers4 = set(locos_appropriate_drivers["Type5"]).intersection(tmp1)

        feasible_drivers5 = set(locos_appropriate_drivers["Type6"]).intersection(tmp1)

        feasible_drivers = feasible_drivers1.union(feasible_drivers2).union(feasible_drivers3)
        feasible_drivers = feasible_drivers.union(feasible_drivers4).union(feasible_drivers5)

    else:
        feasible_drivers2 = set(locos_appropriate_drivers["Type4"]).intersection(tmp1)

        feasible_drivers3 = set(locos_appropriate_drivers["Type7"]).intersection(tmp1)

        feasible_drivers5 = set(locos_appropriate_drivers["Type6"]).intersection(tmp1)

        feasible_drivers = feasible_drivers2.union(feasible_drivers3).union(feasible_drivers5)

    for item in feasible_drivers:
        if [train_id_arg, item, f"delta_{train_id_arg}_{item}"] not in delta_arg:
            delta_arg.append([train_id_arg, item, f"delta_{train_id_arg}_{item}"])

    long_drivers_t_arg[train_id_arg] = [i for i in drivers_arg if i[0] == drivers_t_arg]

    return delta_arg, drivers_t_arg, long_drivers_t_arg


def gen_comp_set_loco(trains, drivers, drivers_header):
    time5 = time.time()
    drivers_t = dict()
    delta = []
    long_drivers_t = dict()
    all_trains = {item[0]: {"begin": item[4], "end": item[6], "org_st": item[3], "arr_st": item[5]} for item in trains}
    drivers_listed = drivers
    drivers_listed_header = drivers_header
    locos_appropriate_drivers = generate_loco_skill_set(drivers_listed, drivers_listed_header)
    route_appropriate_drivers = generate_route_skill_set(drivers_listed, drivers_listed_header, trains)


    for train in trains:
        train_id = train[0]
        route = train[9]
        loco_requirement = train[21]
        meta_loco_requirement = train[20]

        if loco_requirement not in ["Type1", "Type3", "Type2"]:
            delta, drivers_t, long_drivers_t = generate_own_loco_compatibility_set(train_id, route,
                                                                                   meta_loco_requirement,
                                                                                   loco_requirement, drivers,
                                                                                   drivers_t, drivers_listed_header,
                                                                                   drivers_listed, delta,
                                                                                   long_drivers_t, locos_appropriate_drivers, route_appropriate_drivers)
        else:
            delta, drivers_t, long_drivers_t = generate_foreign_loco_compatibility_set(train_id, route, drivers,
                                                                                       drivers_t, long_drivers_t,
                                                                                       drivers_listed,
                                                                                       drivers_listed_header, delta,
                                                                                       loco_requirement, locos_appropriate_drivers, route_appropriate_drivers)
    time6 = time.time()
    print(f"Train sets generated, delta generated in {time6 - time5:.2f} seconds")

    return all_trains, drivers_t, delta, drivers_t, long_drivers_t

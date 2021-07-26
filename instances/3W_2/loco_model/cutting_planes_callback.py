import gurobipy as grb
import time

def generate_locos_available_for_driver(t_argument, d, sets, foreign_locos):
    locos_available_for_driver = list(set([i.split(" - ")[0] for i in sets["locos_d"][d]]))
    for t in t_argument:
        if "ES64F" in locos_available_for_driver and t in foreign_locos["ES64F"].keys():
            locos_available_for_driver.append(foreign_locos["ES64F"][t])

        if "59E" in locos_available_for_driver and t in foreign_locos["59E"].keys():
            locos_available_for_driver.append(foreign_locos["59E"][t])

        if "BR232" in locos_available_for_driver and t in foreign_locos["BR232"].keys():
            locos_available_for_driver.append(foreign_locos["BR232"][t])
    return locos_available_for_driver


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


def generate_conflict_matrix(master_matrix, clique):
    conflict_matrix = dict()
    drivers_in_matrix = set()
    common_drivers_in_clq = set()
    i = 0
    # print(master_matrix.keys())
    for t_id in clique:
        # if type(t_iter) is tuple:
        #     t_id = t_iter[1]
        # else:
        if t_id not in conflict_matrix.keys():
            continue
        conflict_matrix[t_id] = master_matrix[t_id]["drivers"]
        if i == 0:
            common_drivers_in_clq = master_matrix[t_id]["drivers"]
        else:
            common_drivers_in_clq = common_drivers_in_clq.intersection(master_matrix[t_id]["drivers"])

        # for k, v in master_matrix.items():
        #     if k[0] == t_id:
        #         conflict_matrix[k] = v["drivers"]
        #         if i == 0:
        #             common_drivers_in_clq = v["drivers"]
        #         else:
        #             common_drivers_in_clq = common_drivers_in_clq.intersection(v["drivers"])

    for drivers in conflict_matrix.values():
        drivers_in_matrix = drivers_in_matrix.union(drivers)

    return conflict_matrix, drivers_in_matrix, common_drivers_in_clq


def generate_limited_master_matrix(master_matrix, assignments):
    # temp_matrix = dict()
    limited_matrix = dict()
    chosen_rows = set()
    if assignments == []:
        return 0
    for v in assignments:
        if v.varName[0] == "f":
            [_, t1, _, loco] = v.varName.split("_")
            if t1 == "ALPHA":
                continue
            if (t1, loco) in chosen_rows:
                continue
            else:
                chosen_rows.add((t1, loco))

    for k, v in master_matrix.items():
        if k in chosen_rows:
            limited_matrix[k[0]] = v
    # print(limited_matrix)
    return limited_matrix


def generate_set_packing_cuts(model, master_matrix, cliques, assignments, f_index_list):
    """
    assignments - f-variables which got a value of 1
    """
    time1 = time.time()
    limited_matrix = generate_limited_master_matrix(master_matrix, assignments)
    if limited_matrix == 0:
        return
    print(f"************ generating limited matrix took {time.time() - time1:.2f} seconds ************")
    time_conflict_matrix = 0
    time_dominance_conflict_matrix = 0
    time_cut1 = 0
    time_cut2 = 0
    c1 = 0
    c2 = 0

    for clique in cliques:
        # for l in range(2, len(cliques)):
        #     for clique in it.combinations(master_clique, l):
        time3 = time.time()
        conflict_matrix, drivers_in_matrix, common_drivers_in_clq = generate_conflict_matrix(limited_matrix, clique)
        time_conflict_matrix += time.time() - time3
        time4 = time.time()
        if len(common_drivers_in_clq) == 0:
            continue
        if len(conflict_matrix.keys()) > len(drivers_in_matrix):
            # warnings.warn(f"{len(conflict_matrix.keys())} > {len(drivers_in_matrix)}")
            # warnings.warn(f"{conflict_matrix.keys()} > {drivers_in_matrix}")
            relevant_variables_names = (i[3] for i in f_index_list if (i[0], i[2]) in conflict_matrix.keys())
            # vars = [model.getVarByName(i) for i in relevant_variables_names]
            # coefficients = [1 for _ in range(len(vars))]
            # expr1 = grb.LinExpr(coefficients, vars)
            expr1 = grb.quicksum(model.getVarByName(i) for i in relevant_variables_names)
            model.cbLazy(expr1 <= len(drivers_in_matrix))
            c1 += 1
            time_cut1 += time.time() - time4

        dominance_conflict_cuts = set()
        dominance_conflict_matrix = dict()

        time5 = time.time()
        for (t, l), drivers in conflict_matrix.items():
            dominance_conflict_matrix[(t,l)] = {"drivers": drivers, "dominated_trains": set()}
            for (t1, l1), potentially_dominated_drivers in conflict_matrix.items():
                if potentially_dominated_drivers.issubset(drivers):
                    dominance_conflict_matrix[(t,l)]["dominated_trains"].add((t1, l1))
        time_dominance_conflict_matrix += time.time() - time5

        time6 = time.time()

        for values_dict in dominance_conflict_matrix.values():
            if len(values_dict["drivers"]) < len(values_dict["dominated_trains"]):
                if frozenset(values_dict["dominated_trains"]) not in dominance_conflict_cuts:
                    dominance_conflict_cuts.add(frozenset(values_dict["dominated_trains"]))
                    relevant_variables_names = (i[3] for i in f_index_list
                                                if (i[0], i[2]) in values_dict["dominated_trains"])
                    # vars = [model.getVarByName(i) for i in relevant_variables_names]
                    # coefficients = [1 for _ in range(len(vars))]
                    expr2 = grb.quicksum(model.getVarByName(i) for i in relevant_variables_names)
                    model.cbLazy(expr2 <= len(values_dict["drivers"]))
                    c2 += 1
        time_cut2 += time.time() - time6

    print(f"************ generating conflict_matrix took {time_conflict_matrix:.2f} seconds ************")
    print(f"************ generating dominance_conflict_matrix took {time_dominance_conflict_matrix:.2f} seconds ************")
    print(f"************ generating type1 cuts took {time_cut1:.2f} seconds. {c1} cuts generated. ************")
    print(f"************ generating type2 cuts took {time_cut2:.2f} seconds {c2} cuts generated. ************")


    return 0


def lazyCutCallback(model, where):
    if where == grb.GRB.Callback.MIPSOL:
        t1 = time.time()
        values = model.cbGetSolution(model._f)
        assignments = [model._f[t1, t2, l1] for t1, t2, l1 in model._f.keys() if values[t1, t2, l1] > 0.5]
        generate_set_packing_cuts(model, model._master_matrix, model._cliques, assignments, model._f_index_list)
        print(f"************ Time spent in callback: {time.time() - t1:.2f} seconds ************")
import time
import gurobipy as grb
from tqdm import tqdm


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

def generate_master_matrix(drivers_l_arg, f_index_list_arg, train_driver_combinations):
    matrix = dict()
    rows = {(t1, loco_type) for [t1, _, loco_type, _] in f_index_list_arg if t1 != "ALPHA"}
    for (t, loco_type) in rows:
        drivers_l = set(drivers_l_arg[translate_loco_type(loco_type)])
        drivers_t = train_driver_combinations[t]
        relevant_drivers = drivers_l.intersection(drivers_t)
        matrix[(t, loco_type)] = {"drivers": relevant_drivers}
        # matrix[(t, loco_type)]["drivers_v"] = {i[1] for i in v_index_list_arg if
        #                                        i[0] == t and i[1] in relevant_drivers}
        # matrix[(t, loco_type)]["drivers_y"] = {i[1] for i in y_index_list_arg if
        #                                        i[0] == t and i[1] in relevant_drivers}
        # matrix[(t, loco_type)]["drivers_z"] = {i[1] for i in z_index_list_arg if
        #                                        i[0] == t and i[1] in relevant_drivers}
    return matrix


def generate_conflict_matrix(master_matrix, clique):
    conflict_matrix = dict()
    drivers_in_matrix = set()
    common_drivers_in_clq = set()
    i = 0
    for t_id in clique:
        for k, v in master_matrix.items():
            if k[0] == t_id:
                conflict_matrix[k] = v["drivers"]
                if i == 0:
                    common_drivers_in_clq = v["drivers"]
                else:
                    common_drivers_in_clq = common_drivers_in_clq.intersection(v["drivers"])

        for drivers in conflict_matrix.values():
            drivers_in_matrix = drivers_in_matrix.union(drivers)

    return conflict_matrix, drivers_in_matrix, common_drivers_in_clq


def generate_limited_master_matrix(master_matrix, assignments):
    limited_matrix = dict()
    chosen_rows = set()
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
            limited_matrix[k] = v
    return limited_matrix

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

def generate_cuts_c11(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations):
    if t2 != "OMEGA":

        drivers_l = set(sets["drivers_l"][translate_loco_type(loco_type)])
        drivers_t = train_driver_combinations[t2]
        drivers_available = drivers_l.intersection(drivers_t)

        # Condition 1 - no v variables
        # v_counter = len([i for i in v_index_list if i[0] == t2 and i[1] in drivers_available])
        v_counter = len(drivers_available)
        v_condition = v_counter == 0
        if v_counter > 0:
            return 0

        # Condition 2 - next trains
        feasible_next_trains_counter = 0
        rhs_variables_list = []

        for d in drivers_available:
            next_trains = sets["trains_next_t_d"][d][t2]
            feasible_next_trains = set()
            for t_i in next_trains:
                if d in train_driver_combinations[t_i]:
                    feasible_next_trains.add(t_i)
            feasible_next_trains_counter += len(feasible_next_trains)

            if feasible_next_trains:
                locos_available_for_driver = generate_locos_available_for_driver(feasible_next_trains, d, sets,
                                                                                 foreign_locos)
                rhs_variables_list += [i[3] for i in f_index_list
                                       if i[1] in feasible_next_trains and i[2] in locos_available_for_driver]

        rhs_variables_list = set(rhs_variables_list)
        if v_condition and feasible_next_trains_counter == 0:
            prohibited_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
            coefficients = [1 for _ in range(len(prohibited_vars_names))]
            prohibited_vars = [model.getVarByName(i) for i in prohibited_vars_names]
            expr = grb.LinExpr(coefficients, prohibited_vars)
            model.addConstr(expr <= 0)
            return 0

        if v_condition and feasible_next_trains_counter != 0:
            lhs_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
            coefficients = [1 for _ in range(len(lhs_vars_names))]
            lhs_vars = [model.getVarByName(i) for i in lhs_vars_names]
            lhs = grb.LinExpr(coefficients, lhs_vars)

            variables = [model.getVarByName(i) for i in rhs_variables_list]
            coefficients = [1 for _ in range(len(variables))]
            rhs = grb.LinExpr(coefficients, variables)
            model.addConstr(lhs <= rhs, name=f"c11_proj_{t2}_{loco_type}")
            return 0


def generate_cuts_c12(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations):
    if t2 != "OMEGA":
#
        drivers_l = set(sets["drivers_l"][translate_loco_type(loco_type)])
        drivers_t = train_driver_combinations[t2]
        drivers_available = drivers_l.intersection(drivers_t)

        # Condition 1 - no y variables
        # y_counter = len([i for i in y_index_list if i[0] == t2 and i[1] in drivers_available])
        y_counter = len(drivers_available)
        y_condition = y_counter == 0
        if y_counter > 0:
            return 0

        # Condition 2 - previous trains
        feasible_prev_trains_counter = 0
        rhs_variables_list = []

        for d in drivers_available:
            prev_trains = sets["trains_previous_t_d"][d][t2]
            feasible_prev_trains = set()
            for t_i in prev_trains:
                if d in train_driver_combinations[t_i]:
                    feasible_prev_trains.add(t_i)

            # feasible_prev_trains = [i[0] for i in delta_index_list if i[0] in prev_trains and i[1] == d]
            feasible_prev_trains_counter += len(feasible_prev_trains)

            if feasible_prev_trains:
                locos_available_for_driver = generate_locos_available_for_driver(feasible_prev_trains, d, sets,
                                                                                 foreign_locos)
                rhs_variables_list += [i[3] for i in f_index_list
                                       if i[1] in feasible_prev_trains and i[2] in locos_available_for_driver]
        rhs_variables_list = set(rhs_variables_list)
        if y_condition and feasible_prev_trains_counter == 0:
            prohibited_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
            coefficients = [1 for _ in range(len(prohibited_vars_names))]
            prohibited_vars = [model.getVarByName(i) for i in prohibited_vars_names]
            expr = grb.LinExpr(coefficients, prohibited_vars)
            model.addConstr(expr <= 0, name=f"C12_proj_{t2}_{loco_type}")
            return 0

        if y_condition and feasible_prev_trains_counter != 0:
            lhs_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
            coefficients = [1 for _ in range(len(lhs_vars_names))]
            lhs_vars = [model.getVarByName(i) for i in lhs_vars_names]
            lhs = grb.LinExpr(coefficients, lhs_vars)

            variables = [model.getVarByName(i) for i in rhs_variables_list]
            coefficients = [1 for _ in range(len(variables))]
            rhs = grb.LinExpr(coefficients, variables)
            model.addConstr(lhs <= rhs, name=f"c12_proj_{t2}_{loco_type}")
            return 0


def generate_cuts_c13(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations, omega_dict):
    if t2 == "OMEGA":
        return 0

    drivers_l = set(sets["drivers_l"][translate_loco_type(loco_type)])
    drivers_t = train_driver_combinations[t2]
    drivers_available = drivers_l.intersection(drivers_t)
    if len(drivers_available) == 0:
        return 0

    # Condition 1 - no omega variables
    if t2 not in omega_dict.keys():
        omega_counter = 0
    else:
        omegas = omega_dict[t2].intersection(drivers_available)
        omega_counter = len(omegas)

    omega_condition = omega_counter == 0
    if omega_counter > 0:
        return 0

    # Condition 2 - trains after break
    feasible_trains_after_break_counter = 0
    trains_to_enforce = []
    locos_to_enforce = []


    for d in drivers_available:
        trains_after_break = sets["trains_after_break_t_d"][d][t2]
        feasible_trains_after_break = set()
        for t_i in trains_after_break:
            if d in train_driver_combinations[t_i]:
                feasible_trains_after_break.add(t_i)
        # feasible_trains_after_break = set([i[0] for i in y_index_list if i[0] in trains_after_break and i[1] == d])
        feasible_trains_after_break_counter += len(feasible_trains_after_break)

        if feasible_trains_after_break:
            trains_to_enforce.extend(feasible_trains_after_break)
            locos_available_for_driver = set(generate_locos_available_for_driver(feasible_trains_after_break, d, sets,
                                                                             foreign_locos))
            locos_to_enforce.extend(locos_available_for_driver)


    if omega_condition and feasible_trains_after_break_counter == 0:
        prohibited_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
        coefficients = [1 for _ in range(len(prohibited_vars_names))]
        prohibited_vars = [model.getVarByName(i) for i in prohibited_vars_names]
        expr = grb.LinExpr(coefficients, prohibited_vars)
        model.addConstr(expr <= 0, name=f"C13_proj_{t2}_{loco_type}")
        return 0

    if omega_condition and feasible_trains_after_break_counter != 0:
        lhs_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
        coefficients = [1 for _ in range(len(lhs_vars_names))]
        lhs_vars = [model.getVarByName(i) for i in lhs_vars_names]
        lhs = grb.LinExpr(coefficients, lhs_vars)
        trains_to_enforce = set(trains_to_enforce)
        locos_to_enforce = set(locos_to_enforce)
        rhs_variables_list = [i[3] for i in f_index_list if i[1] in trains_to_enforce and i[2] in locos_to_enforce]
        variables = [model.getVarByName(i) for i in rhs_variables_list]
        coefficients = [1 for _ in range(len(variables))]
        rhs = grb.LinExpr(coefficients, variables)
        model.addConstr(lhs <= rhs, name=f"c13_proj_{t2}_{loco_type}")
        return 0


def generate_cuts_c14(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations, alpha_dict):

    drivers_l = set(sets["drivers_l"][translate_loco_type(loco_type)])
    # dont loop below, use a dict! Same holds for all the other places when you loop like this!
    drivers_t = train_driver_combinations[t2]
    drivers_available = drivers_l.intersection(drivers_t)

    # Condition 1 - no alpha variables available
    if t2 not in alpha_dict.keys():
        alpha_counter = 0
    else:
        alphas = alpha_dict[t2].intersection(drivers_available)
        alpha_counter = len(alphas)
    alpha_condition = alpha_counter == 0
    if alpha_counter > 0:
        return 0

    # Condition 2 - trains before break
    feasible_trains_before_break_counter = 0
    trains_to_enforce = []
    locos_to_enforce = []

    for d in drivers_available:
        trains_before_break = sets["trains_before_break_t_d"][d][t2]
        feasible_trains_before_break = set()
        for t_i in trains_before_break:
            if d in train_driver_combinations[t_i]:
                feasible_trains_before_break.add(t_i)

        # feasible_trains_before_break = [i[0] for i in v_index_list if i[0] in trains_before_break and i[1] == d]
        feasible_trains_before_break_counter += len(feasible_trains_before_break)

        if feasible_trains_before_break:
            trains_to_enforce.extend(feasible_trains_before_break)
            locos_available_for_driver = set(generate_locos_available_for_driver(feasible_trains_before_break, d, sets,
                                                                             foreign_locos))
            locos_to_enforce.extend(locos_available_for_driver)

    if alpha_condition and feasible_trains_before_break_counter == 0:
        prohibited_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
        coefficients = [1 for _ in range(len(prohibited_vars_names))]
        prohibited_vars = [model.getVarByName(i) for i in prohibited_vars_names]
        expr = grb.LinExpr(coefficients, prohibited_vars)
        model.addConstr(expr <= 0, name=f"C14_proj_{t2}_{loco_type}")
        return 0


    if alpha_condition and feasible_trains_before_break_counter != 0:
        lhs_vars_names = [i[3] for i in f_index_list if i[1] == t2 and i[2] == loco_type]
        trains_to_enforce = set(trains_to_enforce)
        locos_to_enforce = set(locos_to_enforce)
        rhs_variables_list = [i[3] for i in f_index_list if i[1] in trains_to_enforce and i[2] in locos_to_enforce]
        coefficients = [1 for _ in range(len(lhs_vars_names))]
        lhs_vars = [model.getVarByName(i) for i in lhs_vars_names]
        lhs = grb.LinExpr(coefficients, lhs_vars)

        variables = [model.getVarByName(i) for i in rhs_variables_list]
        coefficients = [1 for _ in range(len(variables))]
        rhs = grb.LinExpr(coefficients, variables)
        model.addConstr(lhs <= rhs, name=f"C14_proj_{t2}_{loco_type}")
        return 0



def extend_loco_model(model, f_index_list, sets, master_matrix, train_driver_combinations):
    alpha_index_list = sets["alpha_index_list"]
    omega_index_list = sets["omega_index_list"]
    alpha_dict = dict()
    omega_dict = dict()

    for (ta, da, _) in alpha_index_list:
        if ta not in alpha_dict.keys():
            alpha_dict[ta] = {da}
        else:
            alpha_dict[ta].add(da)

    for (to, do, _) in omega_index_list:
        if to not in omega_dict.keys():
            omega_dict[to] = {do}
        else:
            omega_dict[to].add(do)

    foreign_locos = dict()
    foreign_locos["ES64F"] = {i[1]: i[2].replace(" - ", "-") for i in f_index_list
                              if i[2][0:5] == "ES64F" and i[1] != "OMEGA"}
    foreign_locos["59E"] = {i[1]: i[2].replace(" - ", "-") for i in f_index_list
                            if i[2][0:5] == "BR232" and i[1] != "OMEGA"}
    foreign_locos["BR232"] = {i[1]: i[2].replace(" - ", "-") for i in f_index_list
                              if i[2][0:3] == "59E" and i[1] != "OMEGA"}

    time_c11 = 0
    time_c12 = 0
    time_c13 = 0
    time_c14 = 0

    for (t2, loco_type) in tqdm(master_matrix.keys()):
        if loco_type[0:5] != "ES64F" and loco_type[0:5] != "BR232" and loco_type[0:3] != "59E":

            # c11_beginning_time = time.time()
            # generate_cuts_c11(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations)
            # c11_end_time = time.time()
            # time_c11 += c11_end_time - c11_beginning_time
            #
            # c12_beginning_time = time.time()
            # generate_cuts_c12(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations)
            # c12_end_time = time.time()
            # time_c12 += c12_end_time - c12_beginning_time

            c13_beginning_time = time.time()
            generate_cuts_c13(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations, omega_dict)
            c13_end_time = time.time()
            time_c13 += c13_end_time - c13_beginning_time

            c14_beginning_time = time.time()
            generate_cuts_c14(model, t2, loco_type, foreign_locos, f_index_list, sets, train_driver_combinations, alpha_dict)
            c14_end_time = time.time()
            time_c14 += c14_end_time - c14_beginning_time

    # print(f"projection of C11: {time_c11:.2f} s.")
    # print(f"projection of C12: {time_c12:.2f} s.")
    print(f"projection of C13: {time_c13:.2f} s.")
    print(f"projection of C14: {time_c14:.2f} s.")

    return model

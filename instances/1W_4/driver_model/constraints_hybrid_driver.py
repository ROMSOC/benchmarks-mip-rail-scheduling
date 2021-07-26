import gurobipy as grb
import time
import os
from datetime import date
import numpy as np


def lexicographic_sort(list_of_cliques):
    if type(list_of_cliques) is list:
        ans = sorted(list_of_cliques)
        ans = sorted(ans, key=len, reverse=True)
        ans = list(ans)
        return ans
    if type(list_of_cliques) is dict:
        ans = list()
        for k, v in list_of_cliques.items():
            ans.append(v)
        ans = sorted(ans)
        ans = sorted(ans, key=len, reverse=True)
        ans = list(ans)
        return ans


def translate_loco_type(in_type):
    if in_type == "Type8":
        return "Type8 - 7"
    elif in_type == "Type6":
        return "Type6 - 6495"
    elif in_type == "Type4":
        return "Type4 - 166"
    elif in_type == "Type7":
        return "Type7 - 90"
    elif in_type == "Type5":
        return "Type5 - 52"
    elif in_type[0:5] == "Type2":
        return "Type2 - 1003"
    elif in_type[0:5] == "Type3":
        return "Type3 - 1006"
    else:
        return "Type1 - 1001"



class Constraints:

    def __init__(self, model, sets_dict, time_perspective, delta, delta_index_list, v, v_index_list, y, y_index_list,
                 alpha, alpha_index_list, omega, omega_index_list, z, z_index_list, h, h_index_list, f, driver_trains_dict, locos_dict, network):

        self.init_time = time.time()

        if time_perspective == "monthly":
            self.z_indicator = 1
            self.h_indicator = 1
        if time_perspective == "weekly":
            self.z_indicator = 1
            self.h_indicator = 0
        if time_perspective == "daily":
            self.z_indicator = 0
            self.h_indicator = 0

        self.model = model

        self.delta = delta
        self.delta_index_list = delta_index_list
        self.v = v
        self.v_index_list = v_index_list
        self.y = y
        self.y_index_list = y_index_list
        self.alpha = alpha
        self.alpha_index_list = alpha_index_list
        self.omega = omega
        self.omega_index_list = omega_index_list
        self.z = z
        self.z_index_list = z_index_list
        self.h = h
        self.h_index_list = h_index_list

        self.f = f

        self.driver_trains_dict = driver_trains_dict

        self.drivers_l = sets_dict["drivers_l"]
        self.locos_d = sets_dict["locos_d"]
        self.drivers_t = sets_dict["drivers_t"]

        self.trains_d = sets_dict["trains_d"]
        # self.trains_time_conflict_d = sets_dict["trains_time_conflict_d"]
        self.trains_time_conflict_init = sets_dict["trains_time_conflict_init"]
        self.trains_break_forward_t_d = sets_dict["trains_break_forward_t_d"]
        self.trains_break_35h_t_d = sets_dict["trains_break_35h_t_d"]
        self.trains_break_backward_t_d = sets_dict["trains_break_backward_t_d"]

        self.trains_week_w_d = sets_dict["trains_week_w_d"]
        self.trains_sunday_w_d = sets_dict["trains_sunday_w_d"]
        self.trains_previous_t_d = sets_dict["trains_previous_t_d"]
        self.trains_next_t_d = sets_dict["trains_next_t_d"]
        self.trains_shift_beginning_t_d = sets_dict["trains_shift_beginning_t_d"]
        self.trains_shift_end_t_d = sets_dict["trains_shift_end_t_d"]

        self.trains_after_break_t_d = sets_dict["trains_after_break_t_d"]
        self.trains_before_break_t_d = sets_dict["trains_before_break_t_d"]
        self.train_to_week_attribution = sets_dict["train_to_week_attribution"]
        # self.drivers_conflict_graphs = sets_dict["drivers_conflict_graphs"]
        # self.common_ends_t_d = sets_dict["common_ends_t_d"]
        # self.common_beginnings_t_d = sets_dict["common_beginnings_t_d"]
        self.trains_d_pruned = sets_dict["trains_d_pruned"]

        self.all_trains = sets_dict["all_trains"]

        self.trains_in_conflict_break_backward = dict()

        self.input_for_matrix_c3 = sets_dict["input_for_matrix_c3"]
        # self.sets_for_c18_d = sets_dict["sets_for_c18_d"]
        # self.input_for_matrix_c18 = sets_dict["input_for_matrix_c18"]
        # self.sets_for_c20_d = sets_dict["sets_for_c20_d"]
        # self.input_for_matrix_c20 = sets_dict["input_for_matrix_c20"]
        # self.sets_for_c24_d = sets_dict["sets_for_c24_d"]
        # self.input_for_matrix_c24 = sets_dict["input_for_matrix_c24"]

        # self.cliques = sets_dict["cliques"]

        self.locos_dict = locos_dict

        self.c1 = grb.tupledict()
        self.c3 = grb.tupledict()
        self.c11 = grb.tupledict()
        self.c12 = grb.tupledict()
        self.c13 = grb.tupledict()
        self.c14 = grb.tupledict()
        self.c15 = grb.tupledict()
        self.c16 = grb.tupledict()
        self.c17 = grb.tupledict()
        self.c18 = grb.tupledict()
        self.c19 = grb.tupledict()
        self.c20 = grb.tupledict()
        self.c21 = grb.tupledict()
        self.c22 = grb.tupledict()
        self.c23 = grb.tupledict()
        self.c24 = grb.tupledict()
        self.c25 = grb.tupledict()
        self.c26 = grb.tupledict()
        self.c27 = grb.tupledict()
        self.cN1 = grb.tupledict()
        self.cN2 = grb.tupledict()
        self.cN3 = grb.tupledict()
        self.cC1 = grb.tupledict()
        self.cC2 = grb.tupledict()

        self.network = network

    def generate_constraint_1(self):
        time1 = time.time()

        trains = set([item[0] for item in self.delta.keys()])
        for train in trains:
            expr1 = self.delta.sum(train, "*")
            if expr1.size() == 1:
                continue
            self.c1[train] = self.model.addLConstr(expr1 <= 1, name=f"c1_{train}")
        time2 = time.time()
        print(f"Constraint 1 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c1.keys())}")

    def generate_constraint_3(self):
        time1 = time.time()
        self.model.update()
        for driver, trains in self.trains_time_conflict_init.items():
        # for driver, trains in self.trains_time_conflict_d.items():
            if driver == "all_trains":
                continue
            for train, trains_to_be_blocked in trains.items():
                if (train, driver) not in self.delta.keys():
                    continue
                var = self.delta[train, driver]
                for t in trains_to_be_blocked:
                    if (t, driver) not in self.delta.keys():
                        continue
                    expr2 = var + self.delta[t, driver]
                    self.c3[driver, train, t] = self.model.addLConstr(expr2 <= 1,
                                                              name=f"c3_{driver}_{train}_{t}")
        time2 = time.time()
        print(f"Constraint 3 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c3.keys())}")

    def generate_constraint_11(self):
        time1 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            for train in trains:
                if self.model.getVarByName(f"delta_{train}_{driver}") is None:
                    continue
                expr1 = self.model.getVarByName(f"delta_{train}_{driver}")
                next_trains = self.trains_next_t_d[driver][train]
                if (train, driver) not in self.v.keys():
                    if len(next_trains) > 0:
                        expr3 = grb.quicksum(self.model.getVarByName(f"delta_{t}_{driver}") for t in next_trains if self.model.getVarByName(f"delta_{t}_{driver}") is not None)
                        # if expr3.size() == 0 and expr1.size() > 0:
                        #     self.implicit_bounds.append([[f"delta_{train}_{driver}"], 0])
                        self.c11[driver, train] = self.model.addLConstr(expr1 <= expr3, name=f"c11_{driver}_{train}")
                    else:
                        continue
                else:
                    expr2 = self.model.getVarByName(f"v_{train}_{driver}")
                    expr3 = grb.quicksum(self.model.getVarByName(f"delta_{t}_{driver}") for t in next_trains if self.model.getVarByName(f"delta_{t}_{driver}") is not None)
                    # if expr3.size() == 0 and expr2.size() == 0 and expr1.size() > 0:
                    #     self.implicit_bounds.append([[f"delta_{train}_{driver}"], 0])
                    self.c11[driver, train] = self.model.addLConstr(expr1 <= expr2 + expr3, name=f"c11_{driver}_{train}")

        time2 = time.time()
        print(f"Constraint 11 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c11.keys())}")

    def generate_constraint_12(self):
        time1 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            for train in trains:
                if self.model.getVarByName(f"delta_{train}_{driver}") is None:
                    continue
                expr1 = self.model.getVarByName(f"delta_{train}_{driver}")
                if self.model.getVarByName(f"y_{train}_{driver}") is not None:
                    expr2 = self.model.getVarByName(f"y_{train}_{driver}")
                else:
                    expr2 = grb.LinExpr()

                expr3 = grb.quicksum(self.model.getVarByName(f"delta_{t}_{driver}") for t in self.trains_previous_t_d[driver][train]
                                     if self.model.getVarByName(f"delta_{t}_{driver}") is not None)

                # if expr3.size() == 0 and expr2.size() == 0:
                #     self.implicit_bounds.append([[f"delta_{train}_{driver}"], 0])

                self.c12[driver, train] = self.model.addLConstr(expr1 <= expr2 + expr3, name=f"c12_{driver}_{train}")

        time2 = time.time()
        print(f"Constraint 12 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c12.keys())}")

    def generate_constraint_13(self):
        time_start_13 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            for train in trains:
                if (train, driver) not in self.v.keys():
                    continue
                expr1 = self.v[train, driver]
                list_of_ts = set(self.trains_after_break_t_d[driver][train])

                # terms = [self.y[t, driver] for t in list_of_ts if t in self.driver_trains_dict[driver]]
                # coefficients = np.ones(len(terms))
                # expr2 = grb.LinExpr(coefficients, terms)
                expr2 = grb.quicksum(self.y[t, driver] for t in list_of_ts if t in self.driver_trains_dict[driver])

                # if ((train, driver) not in self.omega.keys() or self.model.getVarByName(f"omega_{train}_{driver}") is None) and expr2.size() == 0:
                #     continue
                if (train, driver) not in self.omega.keys() and expr2.size() == 0:
                    continue
                # elif (train, driver) not in self.omega.keys() or self.model.getVarByName(f"omega_{train}_{driver}") is None:
                elif (train, driver) not in self.omega.keys():
                    # print(expr1)
                    # print(expr2)
                    self.c13[driver, train] = self.model.addLConstr(expr1 <= expr2, name=f"c13_{driver}_{train}")

                else:
                    # print(expr1)
                    # print(expr2)
                    # print(self.omega[train, driver])
                    self.c13[driver, train] = self.model.addLConstr(expr1 <= expr2 + self.omega[train, driver],
                                                                   name=f"c13_{driver}_{train}")

        time_end_13 = time.time()
        time_lapsed = time_end_13 - time_start_13
        print(f"Constraint 13 generated in {time_lapsed:.2f} seconds, # of constraints: {len(self.c13.keys())}")

    def generate_constraint_14(self):
        time_start_14 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            for train in trains:
                if (train, driver) not in self.y.keys():
                    continue
                expr1 = self.y[train, driver]

                list_of_ts = set(self.trains_before_break_t_d[driver][train])
                # terms = [self.v[t, driver] for t in list_of_ts if t in self.driver_trains_dict[driver]]
                # coefficients = [1 for _ in range(len(terms))]
                # coefficients = np.ones(len(terms))
                expr2 = grb.quicksum(self.v[t, driver] for t in list_of_ts if t in self.driver_trains_dict[driver])

                if self.model.getVarByName(f"alpha_{train}_{driver}") is None and expr2.size() == 0:
                    continue
                elif self.model.getVarByName(f"alpha_{train}_{driver}") is None:
                    self.c14[driver, train] = self.model.addLConstr(expr1 <= expr2, name=f"c14_{driver}_{train}")

                else:
                    self.c14[driver, train] = self.model.addLConstr(expr1 <= expr2 + self.alpha[train, driver],
                                                                   name=f"c14_{driver}_{train}")


        time_end_14 = time.time()
        time_lapsed_14 = time_end_14 - time_start_14
        print(f"Constraint 14 generated in {time_lapsed_14:.2f} seconds, # of constraints: {len(self.c14.keys())}")

    def generate_constraint_15(self):
        time_start_15 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            if len(self.trains_d_pruned[driver]) > 0:
                expr2 = grb.quicksum(self.model.getVarByName(f"alpha_{t}_{driver}") for (t, d) in self.alpha.keys() if d == driver and self.model.getVarByName(f"alpha_{t}_{driver}") is not None)
                if expr2.size() == 0:
                    continue
                self.c15[driver] = self.model.addLConstr(expr2 <= 1, name=f"c15_{driver}")
        time_end_15 = time.time()
        time_lapsed_15 = time_end_15 - time_start_15
        print(f"Constraint 15 generated in {time_lapsed_15:.2f} seconds, # of constraints: {len(self.c15.keys())}")

    def generate_constraint_16(self):
        time1 = time.time()
        for driver, trains in self.trains_d_pruned.items():
            if len(self.trains_d_pruned[driver]) > 0:
                expr2 = grb.quicksum(self.model.getVarByName(f"omega_{t}_{driver}") for (t, d) in self.omega.keys() if d == driver and self.model.getVarByName(f"omega_{t}_{driver}") is not None)
                if expr2.size() == 0:
                    continue
                self.c16[driver] = self.model.addLConstr(expr2 <= 1, name=f"c16_{driver}")
        time2 = time.time()
        print(f"Constraint 16 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c16.keys())}")

    def generate_constraint_17(self):
        time1 = time.time()
        for (train, driver) in self.y.keys():


            expr1 = self.y[train, driver]

            if (train, driver) not in self.delta.keys():
                self.model.remove(self.y[train, driver])
                continue

            expr2 = self.delta[train, driver]
            self.c17[train, driver] = self.model.addLConstr(expr1 <= expr2, name=f"c17_{train}_{driver}")
        time2 = time.time()
        print(f"Constraint 17 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c17.keys())}")

    def generate_constraint_18(self):
        time1 = time.time()
        self.model.update()
        for driver, trains in self.trains_break_backward_t_d.items():
            if driver == "all_trains":
                continue
            for train, trains_to_be_blocked in trains.items():
                if (train, driver) not in self.y.keys():
                    continue
                var = self.y[train, driver]
                for t in trains_to_be_blocked:
                    if (t, driver) not in self.delta.keys():
                        continue
                    expr2 = var + self.delta[t, driver]
                    self.c18[driver, train, t] = self.model.addLConstr(expr2 <= 1,
                                                              name=f"c18_{driver}_{train}_{t}")
        time2 = time.time()
        print(f"Constraint 18 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c18.keys())}")

    def generate_constraint_19(self):
        time1 = time.time()

        for driver, trains in self.trains_d_pruned.items():
            for train in trains:
                if self.model.getVarByName(f"delta_{train}_{driver}") is None:
                    continue

                trains_shift_beginning = list(self.trains_shift_beginning_t_d[driver][train])
                expr1 = self.delta[train, driver]
                # terms1 = [self.delta[i, driver] for i in common_beginnings if (i, driver) in self.delta.keys() and self.model.getVarByName(f"delta_{i}_{driver}") is not None]
                # coefficients1 = [1 for _ in range(len(terms1))]
                # expr1 = grb.LinExpr(coefficients1, terms1)

                terms = [self.y[t, driver] for t in trains_shift_beginning if (t, driver) in self.y.keys() and self.model.getVarByName(f"y_{t}_{driver}") is not None]
                coefficients = [1 for _ in range(len(terms))]
                expr2 = grb.LinExpr(coefficients, terms)
                # if expr2.size() == 0:
                #     self.implicit_bounds.append([[f"delta_{train}_{driver}"], 0])
                self.c19[train, driver] = self.model.addLConstr(expr1 <= expr2, name=f"c19_{driver}_{train}")
        time2 = time.time()
        print(f"Constraint 19 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c19.keys())}")

    def generate_constraint_20(self):
        time1 = time.time()
        self.model.update()
        for driver, trains in self.trains_break_forward_t_d.items():
            if driver == "all_trains":
                continue
            for train, trains_to_be_blocked in trains.items():
                if (train, driver) not in self.v.keys():
                    continue
                var = self.v[train, driver]
                for t in trains_to_be_blocked:
                    if (t, driver) not in self.delta.keys():
                        continue
                    expr2 = var + self.delta[t, driver]
                    self.c20[driver, train, t] = self.model.addLConstr(expr2 <= 1,
                                                              name=f"c20_{driver}_{train}_{t}")
        time2 = time.time()
        print(f"Constraint 20 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c20.keys())}")

    def generate_constraint_21(self):
        time1 = time.time()
        for driver, trains in self.trains_d_pruned.items():

            for train in trains:
                if self.model.getVarByName(f"v_{train}_{driver}") is None:
                    continue
                expr1 = self.v[train, driver]
                trains_y = self.trains_shift_beginning_t_d[driver][train]
                trains_y = set(trains_y).union({train})
                # trains_v = self.common_ends_t_d[driver][train]

                # terms = [self.v[t1, driver] for t1 in trains_v if (t1, driver) in self.v.keys() if self.model.getVarByName(f"v_{t1}_{driver}") is not None]
                # coefficients = [1 for _ in range(len(terms))]
                # expr1 = grb.LinExpr(coefficients, terms)
                #
                # if expr1.size() == 0:
                #     continue


                terms2 = [self.y[t2, driver] for t2 in trains_y if (t2, driver) in self.y.keys() if self.model.getVarByName(f"y_{t2}_{driver}") is not None]
                coefficients2 = [1 for _ in range(len(terms2))]
                expr2 = grb.LinExpr(coefficients2, terms2)

                self.c21[driver, train] = self.model.addLConstr(
                    expr1,
                    grb.GRB.LESS_EQUAL,
                    expr2,
                    name=f"c21_{driver}_{train}")

        time2 = time.time()
        print(f"Constraint 21 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c21.keys())}")
        return 0

    def generate_constraint_22(self):
        time1 = time.time()
        for driver, trains in self.trains_d_pruned.items():

            for train in trains:
                if self.model.getVarByName(f"delta_{train}_{driver}") is None:
                    continue
                expr1 = self.delta[train, driver]

                trains_v = set(self.trains_shift_end_t_d[driver][train]).union({train})



                terms2 = [self.v[t2, driver] for t2 in trains_v if (t2, driver) in self.v.keys() if self.model.getVarByName(f"v_{t2}_{driver}") is not None]
                coefficients2 = [1 for _ in range(len(terms2))]
                expr2 = grb.LinExpr(coefficients2, terms2)
                self.c22[driver, train] = self.model.addLConstr(
                    expr1,
                    grb.GRB.LESS_EQUAL,
                    expr2,
                    name=f"c22_{driver}_{train}")
        time2 = time.time()
        print(f"Constraint 22 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c22.keys())}")
        return 0

    def generate_constraint_23(self):
        time1 = time.time()
        for (train, driver) in self.z.keys():

            if (train, driver) not in self.v.keys():
                continue
            self.c23[train, driver] = self.model.addLConstr(self.z[train, driver] <= self.v[train, driver],
                                                           name=f"c23_{driver}_{train}")
        time2 = time.time()
        print(f"Constraint 23 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c23.keys())}")

    def generate_constraint_24(self):
        time1 = time.time()
        self.model.update()
        for driver, trains in self.trains_break_35h_t_d.items():
            if driver == "all_trains":
                continue
            for train, trains_to_be_blocked in trains.items():
                if (train, driver) not in self.z.keys():
                    continue
                var = self.z[train, driver]
                for t in trains_to_be_blocked:
                    if (t, driver) not in self.delta.keys():
                        continue
                    expr2 = var + self.delta[t, driver]
                    self.c24[driver, train, t] = self.model.addLConstr(expr2 <= 1,
                                                              name=f"c24{driver}_{train}_{t}")
        time2 = time.time()
        print(f"Constraint 24 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c24.keys())}")


    def generate_constraint_25(self):
        time1 = time.time()
        for driver, trains_dict in self.train_to_week_attribution.items():
            for week, trains in trains_dict.items():
                list_z = self.trains_week_w_d[driver][week]
                for t in trains:
                    if (t, driver) not in self.delta.keys(): #self.model.getVarByName(f"delta_{t}_{driver}") is None:
                        continue
                    expr1 = self.delta[t, driver]#self.model.getVarByName(f"delta_{t}_{driver}")
                    terms = [self.z[t_z, driver] for t_z in list_z if (t_z, driver) in self.z.keys()]
                    coefficients = np.ones(len(terms))
                    expr2 = grb.LinExpr(coefficients, terms)
                    if expr2.size() == 0:
                        continue
                    self.c25[driver, week, t] = self.model.addLConstr(
                        expr1,
                        grb.GRB.LESS_EQUAL,
                        expr2,
                        name=f"c25_{driver}_{week}_{t}")

        time2 = time.time()
        print(f"Constraint 25 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c25.keys())}")

        return 0

    def generate_constraint_26(self):
        time1 = time.time()
        index = 0
        for driver, trains_dict in self.trains_sunday_w_d.items():

            for week, trains in trains_dict.items():

                for t in trains:
                    if (t, driver) in self.delta.keys():
                        self.c26[driver, week, t] = self.model.addLConstr(
                            self.delta[t, driver] <= self.h[driver, week],
                            name=f"c26_{driver}_{t}"
                        )
                        index += 1
        time2 = time.time()
        print(f"Constraint 26 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c26.keys())}")
        return 0

    def generate_constraint_27(self):
        time1 = time.time()
        drivers = set([item[0] for item in self.h_index_list])

        for driver in drivers:
            self.c27[driver] = self.model.addLConstr(self.h.sum(driver, "*") <= 3, name=f"c27_{driver}")
        time2 = time.time()
        print(f"Constraint 27 generated in {time2 - time1:.2f} seconds, # of constraints: {len(self.c27.keys())}")


    def generate_constraint_N1(self):
        time_start_N1 = time.time()

        omega_keys = dict()
        for train, driver in self.alpha.keys():
            if self.model.getVarByName(f"alpha_{train}_{driver}") is None:
                continue
            if driver not in omega_keys.keys():
                omega_keys[driver] = set([j for j, d in self.omega.keys() if d == driver])

            relevant_omega_keys = set(filter(lambda k: int(k) >= int(train), omega_keys[driver]))
            # variables = [self.omega[j, driver] for j in relevant_omega_keys]
            # length_of_coeffs = len(variables)
            # coefficients = [1] * length_of_coeffs
            expr2 = grb.LinExpr(np.ones(len(relevant_omega_keys)), [self.omega[j, driver] for j in relevant_omega_keys])
            self.cN1[train, driver] = self.model.addLConstr(self.alpha[train, driver] <= expr2,
                                                            name=f"cN1_{train}_{driver}")
        time_end_N1 = time.time()
        time_lapsed_N1 = time_end_N1 - time_start_N1
        print(f"Constraint N1 generated in {time_lapsed_N1:.2f} seconds, # of constraints: {len(self.cN1.keys())}")


    def generate_constraint_N2(self):
        time_start_N2 = time.time()
        drivers = set([d1 for (t1, d1) in self.alpha.keys()])


        for d in drivers:
            expr1 = grb.quicksum(self.model.getVarByName(f"alpha_{t}_{d1}") for (t, d1) in self.alpha.keys() if
                                 d1 == d and self.model.getVarByName(f"alpha_{t}_{d}") is not None)
            expr2 = grb.quicksum(self.model.getVarByName(f"omega_{t}_{d1}") for (t, d1) in self.omega.keys() if
                                 d1 == d and self.model.getVarByName(f"omega_{t}_{d}") is not None)
            self.cN2[d] = self.model.addLConstr(expr1 == expr2, name=f"cN2_{d}")
        time_end_N2 = time.time()
        time_lapsed_N2 = time_end_N2 - time_start_N2
        print(f"Constraint N2 generated in {time_lapsed_N2:.2f} seconds, # of constraints: {len(self.cN2.keys())}")


    def generate_constraint_N3(self):
        time_start_N3 = time.time()
        for t, d in self.v.keys():
            if self.model.getVarByName(f"v_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is not None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"v_{t}_{d}") <= self.model.getVarByName(f"delta_{t}_{d}"), name=f"cN3_v_{t}_{d}")
            if self.model.getVarByName(f"v_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"v_{t}_{d}") <= 0, name=f"cN3_v_{t}_{d}")

        for t, d in self.omega.keys():
            if self.model.getVarByName(f"omega_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is not None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"omega_{t}_{d}") <= self.model.getVarByName(f"delta_{t}_{d}"), name=f"cN3_omega_{t}_{d}")
            if self.model.getVarByName(f"omega_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"omega_{t}_{d}") <= 0, name=f"cN3_omega_{t}_{d}")

        for t, d in self.alpha.keys():
            if self.model.getVarByName(f"alpha_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is not None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"alpha_{t}_{d}") <= self.model.getVarByName(f"delta_{t}_{d}"), name=f"cN3_alpha_{t}_{d}")
            if self.model.getVarByName(f"alpha_{t}_{d}") is not None and self.model.getVarByName(f"delta_{t}_{d}") is None:
                self.cN3["v", t, d] = self.model.addLConstr(self.model.getVarByName(f"alpha_{t}_{d}") <= 0, name=f"cN3_alpha_{t}_{d}")


        # if self.z_indicator:
        #     for t, d in self.z.keys():
        #         if self.model.getVarByName(f"z_{t}_{d}") is not None and self.model.getVarByName(
        #                 f"delta_{t}_{d}") is not None:
        #             self.cN3["z", t, d] = self.model.addLConstr(
        #                 self.model.getVarByName(f"z_{t}_{d}") <= self.model.getVarByName(f"delta_{t}_{d}"),
        #                 name=f"cN3_z_{t}_{d}")
        #         if self.model.getVarByName(f"z_{t}_{d}") is not None and self.model.getVarByName(
        #                 f"delta_{t}_{d}") is None:
        #             self.cN3["z", t, d] = self.model.addLConstr(self.model.getVarByName(f"z_{t}_{d}") <= 0,
        #                                                         name=f"cN3_z_{t}_{d}")


        time_end_N3 = time.time()
        time_lapsed_N3 = time_end_N3 - time_start_N3
        print(f"Constraint N3 generated in {time_lapsed_N3:.2f} seconds, # of constraints: {len(self.cN3.keys())}")


    def generate_coupling_constraints(self):
        time1 = time.time()
        locos_t = dict()
        for t in self.all_trains:
            locos_t[t] = set([item[2] for item in self.f.keys() if item[0] == t])

        for (train, driver) in self.delta:
            relevant_locos_driver = set(self.locos_d[driver])
            relevant_locos_route = locos_t[train]

            relevant_locos_route = list(relevant_locos_route)
            if relevant_locos_route[0][0:5] == "ES64F" or relevant_locos_route[0][0:3] == "59E" \
                    or relevant_locos_route[0][0:5] == "BR232":

                self.cC1[train, driver] = self.model.addLConstr(self.delta[train, driver] <= self.f.sum("*", train, "*"),
                                                               name=f"cC1_{train}_{driver}")

            else:

                relevant_fs = []
                for t_prev in self.network.predecessors(train):
                    for l1 in relevant_locos_driver:
                        if (t_prev, train, l1) in self.f.keys():
                            relevant_fs.append([t_prev, train, l1])

                expr2 = grb.quicksum(self.f[t11, t22, l11] for [t11, t22, l11] in relevant_fs)

                self.cC1[train, driver] = self.model.addLConstr(self.delta[train, driver] <= expr2, name=f"cC1_{train}_{driver}")

        print(f"Constraint Coupling1 generated in {time.time()-time1:.2f} seconds,  # of constraints: {len(self.cC1)}")
        time2 = time.time()
        for t1, t2, loco_type in self.f.keys():
            if t1 == "ALPHA":
                continue
            f_var = self.f[t1, t2, loco_type]
            if " - " in loco_type:
                loco_type1 = loco_type.split(" - ")[0]
                drivers_t = set([item for item in self.drivers_t[t1]])
                drivers_l_1 = self.drivers_l[translate_loco_type(loco_type1)]
                relevant_drivers = drivers_t.intersection(drivers_l_1)
                expr2 = grb.quicksum(self.delta[t1, d] for d in relevant_drivers)
                if expr2.size() == 0:
                    continue
                self.cC2[t1, loco_type1] = self.model.addLConstr(f_var,
                                                                grb.GRB.LESS_EQUAL,
                                                                expr2,
                                                                name=f"cC2_{t1}_{loco_type1}")

            else:
                drivers_t = set([item for item in self.drivers_t[t1]])
                drivers_l_1 = self.drivers_l[translate_loco_type(loco_type)]

                relevant_drivers = drivers_t.intersection(drivers_l_1)
                expr2 = grb.quicksum(self.delta[t1, d] for d in relevant_drivers)
                if expr2.size() == 0:
                    continue
                self.cC2[t1, loco_type] = self.model.addLConstr(f_var, grb.GRB.LESS_EQUAL, expr2, name=f"cC2_{t1}_{loco_type}")

        print(
            f"Constraint Coupling2 generated in {time.time() - time2:.2f} seconds,  # of constraints: {len(self.cC2)}")


    def generate_model(self):


        self.model.setObjective(self.delta.sum("*", "*"), grb.GRB.MAXIMIZE)

        self.generate_constraint_1()
        self.generate_constraint_3()
        self.generate_constraint_13()
        self.generate_constraint_14()
        self.generate_constraint_15()
        self.generate_constraint_16()
        self.generate_constraint_17()
        self.generate_constraint_18()
        self.generate_constraint_19()
        self.generate_constraint_20()
        self.generate_constraint_21()
        self.generate_constraint_22()
        self.generate_constraint_N1()

        self.generate_constraint_N3()
        self.generate_coupling_constraints()

        if self.z_indicator == 1:
            self.generate_constraint_24()
            self.generate_constraint_25()


        if self.h_indicator == 1:

            self.generate_constraint_26()
            self.generate_constraint_27()

        self.model.update()

        time_end = time.time()
        print(f"Constraints generated in {time_end - self.init_time:.2f} seconds")
        return self.model, []
import gurobipy as grb
import time

class DriverModelVariablesGenerator:

    def __init__(self, driver_region, station_region, sets_dict, time_perspective):
        self.init_time = time.time()
        # initiate the model
        self.model1 = grb.Model()
        self.variable_structures = dict()
        # load the sets prepared
        self.driver_region = driver_region
        self.station_region = station_region

        self.variable_structures["driver_region"] = self.driver_region
        self.variable_structures["station_region"] = self.station_region

        self.neighborhood_set = sets_dict["neighborhood_set"]
        self.long_trains_d = sets_dict["long_trains_d"]
        self.long_trains_d_pruned = sets_dict["long_trains_d_pruned"]
        self.trains_week_w_d = sets_dict["trains_week_w_d"]
        self.trains_previous_t_d = sets_dict["trains_previous_t_d"]
        self.trains_next_t_d = sets_dict["trains_next_t_d"]
        self.trains_after_break_t_d = sets_dict["trains_after_break_t_d"]
        self.trains_before_break_t_d = sets_dict["trains_before_break_t_d"]
        self.trains_shift_beginning_t_d = sets_dict["trains_shift_beginning_t_d"]
        self.trains_shift_end_t_d = sets_dict["trains_shift_end_t_d"]

        self.delta_list = sets_dict["delta"]
        self.y_list = sets_dict["y"]

        self.delta = grb.tupledict()
        self.y = grb.tupledict()
        self.z = grb.tupledict()
        self.v = grb.tupledict()
        self.h = grb.tupledict()
        self.alpha = grb.tupledict()
        self.omega = grb.tupledict()

        self.delta_index_list = []
        self.lmbda_index_list = []
        self.y_index_list = []
        self.z_index_list = []
        self.v_index_list = []
        self.h_index_list = []
        self.alpha_index_list = []
        self.omega_index_list = []

        self.variables_dict = dict()

        if time_perspective == "monthly":
            self.z_controller = 1
            self.h_controller = 1
        if time_perspective == "weekly":
            self.z_controller = 1
            self.h_controller = 0
        if time_perspective == "daily":
            self.z_controller = 0
            self.h_controller = 0

    def generate_alpha_omega_variables(self):
        # alpha and omega variables
        time1 = time.time()

        for driver, trains in self.long_trains_d_pruned.items():
            # i4 += 1
            driver_region_list = [item[1] for item in self.driver_region if item[0] == driver]
            driver_region = set(driver_region_list)

            for train in trains:
                train_id = train[0]
                train_origin_station = train[3]
                train_arrival_station = train[5]
                t_o_region = set([item[1] for item in self.station_region if item[0] == train_origin_station])
                t_a_region = set([item[1] for item in self.station_region if item[0] == train_arrival_station])

                if (t_o_region == driver_region) or (driver_region == {"I"}):
                    self.alpha[train_id, driver] = self.model1.addVar(vtype=grb.GRB.BINARY,
                                                                      name=f"alpha_{train_id}_{driver}")
                    self.alpha_index_list.append([train_id, driver, f"alpha_{train_id}_{driver}"])

                    self.variables_dict[f"alpha_{train_id}_{driver}"] = 0

                if (t_a_region == driver_region) or (driver_region == {"I"}):
                    self.omega[train_id, driver] = self.model1.addVar(vtype=grb.GRB.BINARY,
                                                                      name=f"omega_{train_id}_{driver}")
                    self.omega_index_list.append([train_id, driver, f"omega_{train_id}_{driver}"])

                    self.variables_dict[f"omega_{train_id}_{driver}"] = 0

        self.variable_structures["alpha_index_list"] = self.alpha_index_list
        self.variable_structures["omega_index_list"] = self.omega_index_list
        self.variable_structures["alpha"] = self.alpha
        self.variable_structures["omega"] = self.omega
        time2 = time.time()
        print(f"Generation of alpha and omega variables took {time2 - time1:.2f} seconds")

    def generate_y_v_z_variables(self):
        # y, z, v variables
        i1 = 0

        time3 = time.time()
        for item in self.y_list:
            train = item[0]
            driver = item[1]
            i1 += 1

            # assert1 = len(self.trains_before_break_t_d[driver][train]) != 0
            # assert2 = len([item for item in self.alpha_index_list if item[0] == train and item[1] == driver]) != 0
            #
            # if assert1 or assert2:
            self.y[train, driver] = self.model1.addVar(vtype=grb.GRB.BINARY, name=f"y_{train}_{driver}")
            self.y_index_list.append([train, driver, f"y_{train}_{driver}"])

            self.variables_dict[f"y_{train}_{driver}"] = 0

            # expr3 = 0
            # i3 = self.trains_after_break_t_d[driver][train]
            # for i in i3:
            #     if (i, driver) in self.y.keys():
            #         expr3 += 1
            #         break
            # assert3 = expr3 != 0
            #
            # assert4 = len([item for item in self.omega_index_list if item[0] == train and item[1] == driver]) != 0
            #
            # expr5 = 0
            # for t in self.trains_shift_beginning_t_d[driver][train]:
            #     if (t, driver) in self.y.keys():
            #         expr5 += 1
            #         break
            # assert5 = expr5 != 0

            # if assert5 and (assert3 or assert4):
            self.v[train, driver] = self.model1.addVar(vtype=grb.GRB.BINARY, name=f"v_{train}_{driver}")
            self.v_index_list.append([train, driver, f"v_{train}_{driver}"])
            if self.z_controller == 1:
                self.z[train, driver] = self.model1.addVar(vtype=grb.GRB.BINARY, name=f"z_{train}_{driver}")
                self.z_index_list.append([train, driver, f"z_{train}_{driver}"])

            self.variables_dict[f"v_{train}_{driver}"] = 0
            if self.z_controller == 1:
                self.variables_dict[f"z_{train}_{driver}"] = 0

        self.variable_structures["y_index_list"] = self.y_index_list
        self.variable_structures["v_index_list"] = self.v_index_list
        self.variable_structures["y"] = self.y
        self.variable_structures["v"] = self.v
        if self.z_controller == 1:
            self.variable_structures["z_index_list"] = self.z_index_list
            self.variable_structures["z"] = self.z
        else:
            self.variable_structures["z_index_list"] = []
            self.variable_structures["z"] = []

        time4 = time.time()
        if self.z_controller == 1:
            print(f"Generation of y, v and z variables took {time4-time3:.2f} seconds")
        if self.z_controller == 0:
            print(f"Generation of y and v variables took {time4-time3:.2f} seconds")

    def generate_delta_variables(self):
        # delta variables
        i = 0
        time5 = time.time()
        for [train, driver] in self.delta_list:
            i += 1

            # expr1 = len([item for item in self.v_index_list if item[0] == train and item[1] == driver])
            # if expr1 == 0:
            #     try:
            #         expr2 = len(self.trains_next_t_d[driver][train])
            #     except KeyError:
            #         continue
            #         # condition 1
            #     else:
            #         pass
            #
            # expr3 = len([item for item in self.y_index_list if item[0] == train and item[1] == driver])
            # if expr3 == 0:
            #     try:
            #         expr4 = len(self.trains_previous_t_d[driver][train])
            #     except KeyError:
            #         # condition 2
            #
            #         continue
            #     else:
            #         pass

            # NEW PREPROCESSING TECHNIQUES
            # expr5 = 0
            # for t in self.trains_shift_beginning_t_d[driver][train]:
            #     if (t, driver) in self.y.keys():
            #         expr5 += 1
            #         break
            #     # continue
            #
            # expr6 = 0
            # for t in self.trains_shift_end_t_d[driver][train]:
            #     if (t, driver) in self.v.keys():
            #         expr6 += 1
            #         break
            #     # continue

            # Added 17112020
            # if (train, driver) not in self.v.keys() and len(self.trains_next_t_d[driver][train]) == 0:
            #     # condition 4
            #     continue

            # if (train, driver) not in self.v.keys() and len(self.trains_shift_end_t_d[driver][train]) == 0:
            #     if train in {"14", "57"}:
            #         print(f"{train} Condition 4")
            #     continue

            self.delta[train, driver] = self.model1.addVar(vtype=grb.GRB.BINARY, name=f"delta_{train}_{driver}")
            self.delta_index_list.append([train, driver, f"delta_{train}_{driver}"])
            self.variables_dict[f"delta_{train}_{driver}"] = 0

        # added 31082020
        # delta_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0:5] == "delta"]
        # print(delta_vars)
        self.model1.update()
        # delta_keys = [[i[0], i[1]] for i in self.delta_index_list]
        # v_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0] == "v"]
        # z_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0] == "z"]
        # y_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0] == "y"]
        # alpha_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0:5] == "alpha"]
        # omega_vars = [v.VarName for v in self.model1.getVars() if v.VarName[0:5] == "omega"]
        #
        # for v in v_vars:
        #     _, t_v, d_v = v.split("_")
        #     if [t_v, d_v] not in delta_keys:
        #         self.model1.remove(self.model1.getVarByName(v))
        #         self.v_index_list.remove([t_v, d_v, f"v_{t_v}_{d_v}"])
        #         if (t_v, d_v) in self.v.keys():
        #             del self.v[t_v, d_v]
        #
        # for z in z_vars:
        #     _, t_z, d_z = z.split("_")
        #     if [t_z, d_z] not in delta_keys:
        #         self.model1.remove(self.model1.getVarByName(z))
        #         self.z_index_list.remove([t_z, d_z, f"z_{t_z}_{d_z}"])
        #         if (t_z, d_z) in self.z.keys():
        #             del self.z[t_z, d_z]
        # for y in y_vars:
        #     _, t_y, d_y = y.split("_")
        #     if [t_y, d_y] not in delta_keys:
        #         self.model1.remove(self.model1.getVarByName(y))
        #         self.y_index_list.remove([t_y, d_y, f"y_{t_y}_{d_y}"])
        #         if (t_y, d_y) in self.y.keys():
        #             del self.y[t_y, d_y]
        #
        # for alpha in alpha_vars:
        #     _, t_alpha, d_alpha = alpha.split("_")
        #     if [t_alpha, d_alpha] not in delta_keys:
        #         if d_alpha in {"Driver058", "Driver142"} and t_alpha == "57":
        #             print(f"alpha_{t_alpha}_{d_alpha} removed")
        #         self.model1.remove(self.model1.getVarByName(alpha))
        #         self.alpha_index_list.remove([t_alpha, d_alpha, f"alpha_{t_alpha}_{d_alpha}"])
        #         if (t_alpha, d_alpha) in self.alpha.keys():
        #             del self.alpha[t_alpha, d_alpha]
        #
        # for omega in omega_vars:
        #     _, t_omega, d_omega = omega.split("_")
        #     if [t_omega, d_omega] not in delta_keys:
        #         self.model1.remove(self.model1.getVarByName(omega))
        #         self.omega_index_list.remove([t_omega, d_omega, f"omega_{t_omega}_{d_omega}"])
        #         if (t_omega, d_omega) in self.omega.keys():
        #             del self.omega[t_omega, d_omega]

        self.variable_structures["delta_index_list"] = self.delta_index_list
        self.variable_structures["delta"] = self.delta

        self.model1.update()
        time6 = time.time()
        print(f"Generation of delta variables took {time6-time5:.2f} seconds")

    def generate_h_variables(self):
        time7 = time.time()
        for driver, weeks_trains in self.trains_week_w_d.items():

            for week in weeks_trains.keys():
                self.h[driver, week] = self.model1.addVar(vtype=grb.GRB.BINARY, name=f"h_{driver}_{week}")
                self.h_index_list.append([driver, week, f"h_{driver}_{week}"])

                self.variables_dict[f"h_{driver}_{week}"] = 0

        self.variable_structures["h_index_list"] = self.h_index_list
        self.variable_structures["h"] = self.h
        time8 = time.time()
        print(f"Generation of h variables took {time8-time7:.2f} seconds")

    def generate_variables(self):
        self.generate_alpha_omega_variables()
        self.generate_y_v_z_variables()
        self.generate_delta_variables()
        if self.h_controller == 1:
            self.generate_h_variables()

    def get_model_and_variables(self):
        self.variable_structures["variables_dict"] = self.variables_dict
        self.model1.update()
        return self.model1, self.variable_structures

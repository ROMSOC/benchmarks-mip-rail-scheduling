# -*- coding: utf-8 -*-

import csv
import time

from set_generation.driver_compatibility_set_generator import generate_neighbourhood_set, \
    generate_compatibility_set_driver
from set_generation.loco_compatibility_set_generator import gen_comp_set_loco
from set_generation.loco_sets_generators import generate_long_trains_l, generate_trains_next_t_l
from set_generation.trains_break_sets_generator import generate_trains_break_backward_t_d, \
    generate_trains_break_35h_t_d, generate_trains_break_forward_t_d
from set_generation.trains_prev_next_generator import generate_trains_next_t_d
from set_generation.trains_pruned_generator import generate_trains_d_pruned, generate_long_trains_d_pruned
from set_generation.trains_shift_beginning_end_generator import generate_trains_prev_shift_beginning_end_t_d
from set_generation.trains_time_conflict import generate_trains_time_conflict_init
from set_generation.trains_week_generator import generate_trains_week_w_d, generate_trains_sunday_w_d, \
    generate_train_to_week_attribution
from set_generation.trains_before_after_break_generator import generate_trains_before_after_break_t_d
from set_generation.generate_drivers_l import generate_drivers_l
from set_generation.alpha_omega_z_generator import generate_alpha_omega_variables, generate_z_index_list
from set_generation.cliques_generator import generate_trains_time_conflict_d, generate_set_for_constraint_c18, \
    generate_set_for_constraint_c20, generate_set_for_constraint_c24


class SetGenerator:
    """
    This class will generate all the sets and other data structures required for the model construction.

    Inputs: Raw files (after the manipulations agreed with the industrial partner)
    Output: Dictionary with the generated sets.
    """

    def __init__(self, trains, drivers, locos, distance, driver_region, station_region, period_begin=43862.0):
        self.time = time.time()
        with open(trains, encoding="utf-8") as file1:
            self.trains = list(csv.reader(file1))
        with open(locos, encoding="utf-8") as file3:
            self.locos = list(csv.reader(file3))
        with open(distance, encoding="utf-8") as file5:
            self.distance = list(csv.reader(file5))
        with open(drivers, encoding="utf-8-sig") as file6:
            self.drivers = list(csv.reader(file6))

        self.drivers_headers = self.drivers[0]
        self.drivers = self.drivers[1:]

        self.period_begin = period_begin

        self.station_region = station_region
        self.driver_region = driver_region

        self.train_headers = self.trains[0]
        self.trains = self.trains[1:]
        self.locos = self.locos[1:]
        self.distance = self.distance[1:]
        self.locos_master = ["Type8 - 7", "Type4 - 166", "Type5 - 52", "Type6 - 6495", "Type7 - 90"]
        self.locos_Type1 = [item[1] for item in self.locos if item[13] == "Type1"]
        self.locos_Type2 = [item[1] for item in self.locos if item[13] == "Type2"]
        self.locos_Type3 = [item[1] for item in self.locos if item[13] == "Type3"]
        self.long_trains_l = dict()
        self.drivers_l = dict()
        self.trains_next_t_l = dict()
        self.neighborhood_set = dict()
        self.trains_d = dict()
        self.locos_d = dict()
        self.long_trains_d = dict()
        self.long_locos_d = dict()
        self.all_trains = dict()
        self.delta = dict()
        self.y = dict()
        self.drivers_t = dict()
        self.long_drivers_t = dict()
        self.trains_d_pruned = dict()
        self.long_trains_d_pruned = dict()
        self.trains_time_conflict_init = dict()
        self.input_for_matrix_c3 = dict()
        self.trains_break_forward_t_d = dict()
        self.trains_break_35h_t_d = dict()
        self.trains_break_backward_t_d = dict()
        self.trains_week_w_d = dict()
        self.trains_sunday_w_d = dict()
        self.trains_previous_t_d = dict()
        self.trains_next_t_d = dict()
        self.trains_shift_beginning_t_d = dict()
        self.trains_shift_end_t_d = dict()
        self.common_beginnings_t_d = dict()
        self.common_ends_t_d = dict()
        self.train_to_week_attribution = dict()
        self.trains_before_break_t_d = dict()
        self.trains_after_break_t_d = dict()
        self.trains_time_conflict_d = dict()
        self.alpha_index_list, self.omega_index_list, self.z_index_list = [], [], []
        self.cliques = set()

    def generate_sets(self):
        self.long_trains_l = generate_long_trains_l(self.locos, self.trains)
        self.trains_next_t_l = generate_trains_next_t_l(self.locos_master, self.long_trains_l)
        self.neighborhood_set = generate_neighbourhood_set(self.distance)
        self.trains_d, self.locos_d, self.long_trains_d, self.long_locos_d = generate_compatibility_set_driver(
            self.trains, self.drivers, self.drivers_headers, self.locos)
        self.drivers_l = generate_drivers_l(self.locos, self.locos_d)
        self.all_trains, self.drivers_t, self.delta, self.drivers_t, self.long_drivers_t = gen_comp_set_loco(
            self.trains, self.drivers, self.drivers_headers)
        self.trains_d_pruned = generate_trains_d_pruned(self.trains_d, self.delta)

        self.long_trains_d_pruned = generate_long_trains_d_pruned(self.long_trains_d, self.trains_d_pruned)
        self.trains_time_conflict_init = generate_trains_time_conflict_init(self.trains, self.neighborhood_set,
                                                                            self.long_trains_d_pruned,
                                                                            self.trains_d_pruned)
        self.trains_break_forward_t_d = generate_trains_break_forward_t_d(self.trains, self.long_trains_d_pruned,
                                                                          self.neighborhood_set)
        self.trains_break_35h_t_d = generate_trains_break_35h_t_d(self.trains, self.long_trains_d_pruned,
                                                                  self.neighborhood_set)
        self.trains_break_backward_t_d = generate_trains_break_backward_t_d(self.trains,
                                                                            self.long_trains_d_pruned,
                                                                            self.neighborhood_set)
        self.trains_week_w_d = generate_trains_week_w_d(self.long_trains_d_pruned)

        self.trains_sunday_w_d = generate_trains_sunday_w_d(self.long_trains_d_pruned)
        # self.trains_previous_t_d = generate_trains_previous_t_d(self.long_trains_d_pruned, self.neighborhood_set)
        self.trains_next_t_d = generate_trains_next_t_d(self.long_trains_d_pruned, self.neighborhood_set)
        self.trains_shift_beginning_t_d, self.trains_shift_end_t_d, self.trains_previous_t_d = generate_trains_prev_shift_beginning_end_t_d(
            self.trains_d_pruned, self.trains_next_t_d, self.all_trains)
        self.train_to_week_attribution = generate_train_to_week_attribution(self.long_trains_d_pruned)

        self.trains_after_break_t_d, self.trains_before_break_t_d = generate_trains_before_after_break_t_d(
            self.long_trains_d_pruned, self.neighborhood_set)
        self.alpha_index_list, self.omega_index_list = generate_alpha_omega_variables(self.long_trains_d_pruned,
                                                                                      self.driver_region,
                                                                                      self.station_region)
        self.z_index_list = generate_z_index_list(self.trains_week_w_d)
        # self.trains_time_conflict_d, self.cliques = generate_trains_time_conflict_d(self.trains,
        #                                                                             self.long_trains_d_pruned,
        #                                                                             self.trains_time_conflict_init,
        #                                                                             self.cliques)
        # self.sets_for_c18_d, self.cliques = generate_set_for_constraint_c18(self.trains, self.trains_d_pruned,
        #                                                                     self.trains_break_backward_t_d,
        #                                                                     self.trains_time_conflict_init, self.delta,
        #                                                                     self.cliques)
        # self.sets_for_c20_d, self.cliques = generate_set_for_constraint_c20(self.trains, self.trains_d_pruned,
        #                                                                     self.trains_break_forward_t_d,
        #                                                                     self.trains_time_conflict_init, self.delta,
        #                                                                     self.cliques)
        # self.sets_for_c24_d, self.cliques = generate_set_for_constraint_c24(self.trains, self.trains_d_pruned,
        #                                                                     self.trains_break_35h_t_d,
        #                                                                     self.trains_time_conflict_init, self.delta,
        #                                                                     self.z_index_list, self.cliques)

    def get_sets(self):
        answer1 = dict(self.__dict__)
        time_end = time.time()
        print(f"Sets generated in {time_end - self.time:.2f} seconds")
        return answer1

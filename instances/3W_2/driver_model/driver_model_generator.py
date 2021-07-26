# import os
# from datetime import date

from driver_model.variable_generator_driver import DriverModelVariablesGenerator
# from driver_model.constraints_hybrid_driver import Constraints
from driver_model.graph_structures_generator import GraphStructures

import csv


class DriverModelGenerator:

    def __init__(self, driver_region_path, station_region_path, sets_dict, time_perspective):
        with open(driver_region_path, encoding="utf-8") as file3:
            self.driver_region = list(csv.reader(file3))

        with open(station_region_path, encoding="utf-8") as file4:
            self.station_region = list(csv.reader(file4))

        self.sets_dict = sets_dict
        self.time_perspective = time_perspective
        self.driver_model_vars = 0
        self.driver_model = 0
        self.variable_structures = 0
        self.constraint_generator = 0
        self.graph_structures = dict()

    def generate_driver_model_variables(self):
        dmvg = DriverModelVariablesGenerator(self.driver_region, self.station_region, self.sets_dict,
                                             self.time_perspective)
        dmvg.generate_variables()
        self.driver_model_vars, self.variable_structures = dmvg.get_model_and_variables()

    def generate_graph_structures(self):
        gs = GraphStructures(self.sets_dict, self.variable_structures, self.time_perspective)
        gs.generate_set_structures()
        self.graph_structures, self.cliques_for_cutting_planes = gs.get_graph_structures()

    # def generate_driver_model_constraints(self):
    #     self.constraint_generator = Constraints(self.driver_model_vars, self.sets_dict, self.variable_structures,
    #                                     self.graph_structures, self.time_perspective)
    #     self.driver_model = self.constraint_generator.generate_model()
    #
    # def generate_driver_model(self):
    #     self.generate_driver_model_variables()
    #     self.generate_graph_structures()
    #     self.generate_driver_model_constraints()
    #     dir_name = os.path.basename(os.getcwd())
    #     today = date.today()
    #     self.driver_model.setParam('SolFiles', f"solutions_{today}_{dir_name}_driver")
    #     self.driver_model.setParam('LogFile', f"gurobi_{today}_{dir_name}_driver.log")
    #     return self.driver_model, self.variable_structures, self.graph_structures, self.cliques_for_cutting_planes

    def generate_driver_model_variables_and_graph_structures(self):
        self.generate_driver_model_variables()
        self.generate_graph_structures()
        return self.driver_model_vars, self.variable_structures, self.graph_structures, self.cliques_for_cutting_planes

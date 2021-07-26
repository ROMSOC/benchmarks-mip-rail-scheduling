import sys
import pathlib
import csv
import gurobipy as grb
from datetime import datetime, date

from loco_model.loco_model_generator import LocosModelGenerator
from set_generation.sets_generator import SetGenerator
from driver_model.constraints_hybrid_driver import Constraints

path = str(pathlib.Path(__file__).parent.absolute())
today = date.today()
now = datetime.now()
dt_string = now.strftime("%H-%M-%S")

if len(sys.argv) < 3 or sys.argv[1] not in ["daily", "weekly", "monthly"] or sys.argv[2] not in ["write", "nowrite"]:
    raise Exception(
        'Usage: python main.py [daily,weekly,monthly] [write,nowrite]')

time_perspective = sys.argv[1]
writing = sys.argv[2]


def main(time_perspective_arg, writing_arg, driver_region_path=f"{path}/data/driver_region_mapping.csv",
         station_region_path=f"{path}/data/station_region_mapping.csv"):

    with open(driver_region_path, newline='', encoding='utf-8-sig') as file3:
        driver_region = list(csv.reader(file3))

    with open(station_region_path, newline='', encoding='utf-8-sig') as file4:
        station_region = list(csv.reader(file4))

    sg = SetGenerator(f"{path}/data/trains.csv", f"{path}/data/drivers.csv", f"{path}/data/unique_locos.csv",
                      f"{path}/data/distance_matrix.csv", driver_region,
                      station_region)
    sg.generate_sets()
    sets = sg.get_sets()

    delta1 = set([(i[0], i[1]) for i in sets["delta"]])

    lm = LocosModelGenerator(f"{path}/data/trains.csv", f"{path}/data/unique_locos.csv",
                             sets["trains_next_t_l"], delta_index_list=sets["delta"],
                             locos_d=sets["locos_d"], drivers_t=sets["drivers_t"], delta=delta1)

    l_model, f_index_list, _, lmbda_index_list, locos_dict, network = lm.generate_loco_model()

    f = grb.tupledict()
    for [t1, t2, l, var_name] in f_index_list:
        if l_model.getVarByName(var_name) is not None:
            f[t1, t2, l] = l_model.getVarByName(var_name)

    delta_index_list = sets["delta"]

    train_driver_combinations = dict()
    for (t, d, _) in delta_index_list:
        if t not in train_driver_combinations.keys():
            train_driver_combinations[t] = {d}
        else:
            train_driver_combinations[t].add(d)

    delta = grb.tupledict()
    delta_index_list = []
    v = grb.tupledict()
    v_index_list = []
    y = grb.tupledict()
    y_index_list = []
    z = grb.tupledict()
    z_index_list = []
    h = grb.tupledict()
    h_index_list = []
    alpha = grb.tupledict()
    alpha_index_list = []
    omega = grb.tupledict()
    omega_index_list = []

    driver_trains_dict = dict()
    omegas_driver_dict = dict()

    for t, drivers in train_driver_combinations.items():
        for d in drivers:
            delta[t, d] = l_model.addVar(vtype="B", name=f"delta_{t}_{d}")
            v[t, d] = l_model.addVar(vtype="B", name=f"v_{t}_{d}")
            y[t, d] = l_model.addVar(vtype="B", name=f"y_{t}_{d}")
            delta_index_list.append([t, d, f"delta_{t}_{d}"])
            v_index_list.append([t, d, f"v_{t}_{d}"])
            y_index_list.append([t, d, f"y_{t}_{d}"])
            if [t, d, f"alpha_{t}_{d}"] in sets["alpha_index_list"]:
                alpha[t, d] = l_model.addVar(vtype="B", name=f"alpha_{t}_{d}")
            if [t, d, f"omega_{t}_{d}"] in sets["omega_index_list"]:
                omega[t, d] = l_model.addVar(vtype="B", name=f"omega_{t}_{d}")
                if d not in omegas_driver_dict.keys():
                    omegas_driver_dict[d] = {t}
                else:
                    omegas_driver_dict[d].add(t)

            if d not in driver_trains_dict.keys():
                driver_trains_dict[d] = {t}
            else:
                driver_trains_dict[d].add(t)

    for driver, weeks in sets["trains_week_w_d"].items():
        for week_id, trains in weeks.items():
            for train in trains:
                if driver in driver_trains_dict.keys() and train in driver_trains_dict[driver]:
                    z[train, driver] = l_model.addVar(vtype="B", name=f"z_{train}_{driver}")
                    z_index_list.append([train, driver, f"z_{train}_{driver}"])

    if time_perspective_arg == "monthly":
        for driver, trains_dict in sets["trains_sunday_w_d"].items():
            if driver in driver_trains_dict.keys():
                for week in trains_dict.keys():
                    h[driver, week] = l_model.addVar(vtype="B", name=f"h_{driver}_{week}")
                    h_index_list.append([driver, week, f"h_{driver}_{week}"])

    else:
        h = grb.tupledict()
        h_index_list = []

    driver_model = Constraints(l_model, sets, time_perspective_arg, delta, delta_index_list, v, v_index_list, y,
                               y_index_list, alpha, alpha_index_list, omega, omega_index_list, z, z_index_list, h,
                               h_index_list, f, driver_trains_dict, locos_dict, network)
    d_model, _ = driver_model.generate_model()

    if writing_arg == "write":
        d_model.write("driver_model.lp")


if __name__ == "__main__":
    main(time_perspective, writing)

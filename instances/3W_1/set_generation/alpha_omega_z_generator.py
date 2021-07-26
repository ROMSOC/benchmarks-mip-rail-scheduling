import time

def generate_alpha_omega_variables(long_trains_d_pruned, driver_region, station_region):
    # alpha and omega variables
    time1 = time.time()
    alpha_index_list = []
    omega_index_list = []
    for driver, trains in long_trains_d_pruned.items():
        # i4 += 1
        driver_region_list = [item[1] for item in driver_region if item[0] == driver]
        driver_region_set = set(driver_region_list)

        for train in trains:
            train_id = train[0]
            train_origin_station = train[3]
            train_arrival_station = train[5]
            t_o_region = set([item[1] for item in station_region if item[0] == train_origin_station])
            t_a_region = set([item[1] for item in station_region if item[0] == train_arrival_station])

            if (t_o_region == driver_region_set) or (driver_region_set == {"I"}):

                alpha_index_list.append([train_id, driver, f"alpha_{train_id}_{driver}"])

            if (t_a_region == driver_region_set) or (driver_region_set == {"I"}):
                omega_index_list.append([train_id, driver, f"omega_{train_id}_{driver}"])



    time2 = time.time()
    print(f"Generation of alpha and omega lists took {time2 - time1:.2f} seconds")
    return alpha_index_list, omega_index_list

def generate_z_index_list(trains_week_w_d):
    z_index_list = []
    for driver, week_train_dict in trains_week_w_d.items():
        for week_id, trains in week_train_dict.items():
            for t in trains:
                z_index_list.append([t, driver])
    return z_index_list
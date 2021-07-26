import time
from set_generation.auxiliary_functions import merge_dicts


def generate_neighbourhood_set(distance):

    neighborhood_set = dict()
    time1 = time.time()
    stations = list(set(set([x[0] for x in distance]).union(set([x[1] for x in distance]))))

    for station in stations:
        n_hood1 = {item[1]: float(item[3]) for item in distance if station == item[0]}
        n_hood2 = {item[0]: float(item[3]) for item in distance if station == item[1]}
        n_hood3 = {station: 0}
        neighborhood_temp = merge_dicts(n_hood1, n_hood2)
        neighborhood = merge_dicts(neighborhood_temp, n_hood3)

        neighborhood_set[station] = neighborhood
    time2 = time.time()
    print(f"Neighborhood set generated in {time2 - time1:.2f} seconds")
    return neighborhood_set


def generate_compatibility_set_driver(trains, drivers, driver_headers, locos):

    time3 = time.time()
    headers = driver_headers
    trains_d = dict()
    locos_d = dict()
    long_trains_d = dict()
    long_locos_d = dict()

    for row in drivers:
        driver = row[2]
        driver_route_licenses = [item[0] for item in list(zip(headers, row))[5:119] if item[1] == "1"]
        driver_loco_licenses = [item[0] for item in list(zip(headers, row))[119:] if item[1] == "1"]

        trains_d[driver] = [item[0] for item in trains if item[9] in driver_route_licenses]
        locos_d[driver] = [item[1] for item in locos if item[13] in driver_loco_licenses]

        long_trains_d[driver] = [item for item in trains if item[9] in driver_route_licenses]
        long_locos_d[driver] = [item for item in locos if item[13] in driver_loco_licenses]
    time4 = time.time()
    print(f"Driver set generated in {time4 - time3:.2f} seconds")

    return trains_d, locos_d, long_trains_d, long_locos_d

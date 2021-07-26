import time


def generate_trains_d_pruned(trains_d, delta):
    t1 = time.time()
    trains_d_pruned = dict()
    for driver, trains in trains_d.items():
        trains_d_pruned[driver] = set([item[0] for item in delta if item[1] == driver])

    t2 = time.time() - t1
    print(f"trains_d_pruned: {t2:.2f}")
    return trains_d_pruned


def generate_long_trains_d_pruned(long_trains_d, trains_d_pruned):
    t1 = time.time()
    long_trains_d_pruned = dict()
    for driver, trains in long_trains_d.items():
        long_trains_d_pruned[driver] = [item for item in trains if item[0] in trains_d_pruned[driver]]
    t2 = time.time() - t1
    print(f"long_trains_d_pruned: {t2:.2f}")
    return long_trains_d
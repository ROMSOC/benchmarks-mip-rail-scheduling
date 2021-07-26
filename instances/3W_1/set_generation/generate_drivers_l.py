def generate_drivers_l(all_locos, locos_d):
    drivers_l = dict()
    for l in all_locos:
        drivers_l[l[1]] = [k for k, v in locos_d.items() if l[1] in v]
    return drivers_l
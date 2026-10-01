"""Shared path/naming helpers for livery scripts.

Layout: liveries/<livery>/<car-key>/{out,final,reference,archive}. Car keys are
<make>-<model>-<class> (LIVERY_GUIDE section 2).

    sys.path.insert(0, os.path.join(REPO, "tools")); import paths
    OUT = paths.out_dir(HERE, car_key)            # creates <livery>/<car-key>/out
    key = paths.pick_car(args, CARS, "bmw-m4-gt3")  # pops a leading car key from args
"""
import os
import sys

OLD_KEYS = {"bmw": "bmw-m4-gt3", "mclaren": "mclaren-720s-gt3", "ferrari": "ferrari-296-gt3",
            "lotus79": "lotus-79", "ir04": "formula-ir04", "valkyrie": "aston-martin-valkyrie-gtp"}


def out_dir(livery_dir, car_key):
    d = os.path.join(livery_dir, car_key, "out")
    os.makedirs(d, exist_ok=True)
    return d


def pick_car(args, cars, default):
    """Pop and return a leading car key from args, else the default. Old short keys are an error."""
    if args and args[0] in OLD_KEYS:
        sys.exit(f"'{args[0]}' is the old car key: use '{OLD_KEYS[args[0]]}'")
    return args.pop(0) if args and args[0] in cars else default

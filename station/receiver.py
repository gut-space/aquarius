import datetime
import logging
import os
import shutil
import sys
import typing

from matplotlib.pyplot import imread

from utils.functional import first
from utils.models import get_satellite
from utils.dates import from_iso_format
from utils.configuration import open_config
from submitobs import submit_observation, SubmitRequestData
from recipes import factory
from quality_ratings import get_rate_by_name


def move_to_satellite_directory(root: str, sat_name: str, path: str):
    now = datetime.datetime.utcnow()
    timestamp_dir = now.strftime(r"%Y-%m-%d")
    base = os.path.basename(path)
    new_dir = os.path.join(root, sat_name, timestamp_dir)
    new_path = os.path.join(new_dir, base)

    os.makedirs(new_dir, exist_ok=True)
    shutil.move(path, new_path)


config = open_config()


def get_rating_for_product(product_path: str, rate_name: typing.Optional[str]) \
        -> typing.Optional[float]:
    if rate_name is None:
        return None

    try:
        rate = get_rate_by_name(rate_name)
        img = imread(product_path)
        return rate(img)
    except Exception as _:
        logging.error("Error during rating the product", exc_info=True)
        return None


def cmd():
    _, name, los, *opts = sys.argv

    satellite = get_satellite(config, name)

    aos_datetime = datetime.datetime.utcnow()
    los_datetime = from_iso_format(los)

    results, tmp_directory = factory.execute_recipe(satellite, los_datetime)

    # Post-processing
    save_mode = satellite["save_to_disk"]
    should_submit = satellite["submit"]

    root_directory = config.get("obsdir")
    if root_directory is None:
        root_directory = "/tmp/observations"

    signal = first(results, lambda r: r[0] == "signal")
    products = filter(lambda r: r[0] == "product", results)

    if save_mode in ("SIGNAL", "ALL") and signal is not None:
        move_to_satellite_directory(root_directory, name, signal[1])

    if should_submit:
        product = first(products, lambda _: True)
        if product is not None:
            rating = get_rating_for_product(product[1], satellite.get("rating"))
            submit_observation(
                SubmitRequestData(
                    product[1], name, aos_datetime, aos_datetime,
                    los_datetime, "", rating
                )
            )
                

    if save_mode in ("PRODUCT", "ALL"):
        for _, path in products:
            move_to_satellite_directory(root_directory, name, path)

    shutil.rmtree(tmp_directory, ignore_errors=True)


if __name__ == '__main__':
    try:
        cmd()
    except:
        _, name, los, *opts = sys.argv
        logging.error("Failed receiver %s (LOS: %s)" % (name, los), exc_info=True)

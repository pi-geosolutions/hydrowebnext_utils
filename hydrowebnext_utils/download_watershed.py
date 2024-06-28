"""
Utility functions to retrieve a full watershed

This is not trivial, since hydroweb.next is not giving anymore the means
to filter based on a watershed name (or a station name)
"""

from datetime import datetime
from eodag import EODataAccessGateway, setup_logging
from fnmatch import fnmatch
import logging
import os
from shutil import rmtree, copy

from hydrowebnext_utils import get_name_from_hydrowebnext_filename

hydroweb_next_stac_url = os.environ.get("HYDROWEBNEXT_STAC_URL", "https://hydroweb.next.theia-land.fr/api/v1/rs-catalog/stac/")

setup_logging(0)  # 0: nothing, 1: only progress bars, 2: INFO, 3: DEBUG
# Add custom logger
custom_logger = logging.getLogger("Hydroweb.next")
custom_logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)-15s %(name)-32s [%(levelname)-8s] %(message)s')
handler = logging.StreamHandler()  # Use a different handler if needed
handler.setFormatter(formatter)
custom_logger.addHandler(handler)

custom_logger.info(f"Start retrieving data from hydroweb.next API")


def download_over_extent(product_name: str, basin_name: str, bbox_wkt: str, dest_folder: str):
    custom_logger.info(f"Start retrieving data from hydroweb.next API")
    os.makedirs(dest_folder, exist_ok=True)

    dag = EODataAccessGateway()

    # Set timeout to 30s
    # os.environ["EODAG__HYDROWEB_NEXT__SEARCH__TIMEOUT"] = "30"

    # Default search criteria when iterating over collection pages
    default_search_criteria = {
        "items_per_page": 2000,
    }

    # Set download directory
    tmpdir = os.environ.get("HYDROSAT_TEMP_DIR", "/tmp")
    hysope_results_download_path = f"{tmpdir}/hysope_results_{int(datetime.now().timestamp())}"
    os.makedirs(hysope_results_download_path, exist_ok=True)

    query_args = {
        "productType": product_name,
        "geom": bbox_wkt,
    }
    query_args.update(default_search_criteria)

    # Run a paginated search
    search_results = ([])

    for i, page_results in enumerate(dag.search_iter_page(**query_args)):
        custom_logger.info(f"{len(page_results)} product(s) found on page {i + 1}")
        search_results.extend(page_results)

    custom_logger.info(f"Hydroweb.next {product_name} -- total products found : {len(search_results)}")

    # document the mapping between the old station ID and the new URN-like ID
    # And filter-out stations that we are not interested in (keep only those in sv_dict)
    ids_mappings = {}
    for product in search_results:
        file_name = list(product.assets.data.keys())[0]
        station_name = get_name_from_hydrowebnext_filename(file_name)
        custom_logger.info(f"{station_name}      ({product.properties['id']})")
        ids_mappings[product.properties["id"]] = {
            "filename": file_name,
            "station_name": station_name
        }
    # Download all found products
    custom_logger.info(f"Downloading {len(search_results)} products...")
    downloaded_paths = dag.download_all(search_results, outputs_prefix=hysope_results_download_path)
    if downloaded_paths:
        distinct_values = list(set(downloaded_paths))
        # Check is distinct values length is equal to all results length
        if len(distinct_values) != len(search_results):
            custom_logger.warning(
                f"Distinct values length is not equal to all results length. {len(distinct_values)} != {len(search_results)}")
            custom_logger.warning(f"Some files have not been downloaded")
        else:
            custom_logger.info(f"All {len(search_results)} files have been successfully downloaded.")
    else:
        print(f"No files downloaded! Verify API-KEY and/or product search configuration.")

    # Process the downloaded datasets:
    # - filter on basin name
    # - copy selected files into dest_folder
    # - remove the temporary download folder
    # We have to handle separately lakes and rivers, because lakes still use the old format, not compatible with the new one

    count = 0

    # Rivers pattern
    filename_pattern = "hydroprd_R_*.txt"
    for path, subdirs, files in os.walk(hysope_results_download_path):
        for name in files:
            if fnmatch(name, filename_pattern):
                try:
                    with open(os.path.join(path, name), "r") as f:
                        if f"#BASIN:: {basin_name.upper()}" in f.read():
                            copy(os.path.join(path, name),
                                 os.path.join(dest_folder, get_name_from_hydrowebnext_filename(name)+".txt"))
                            count += 1
                except TypeError as e:
                    custom_logger.error(f"TypeError processing file {os.path.join(path, name)}. Skipping the file")
    # Lakes pattern
    filename_pattern = "hydroprd_L_*.txt"
    for path, subdirs, files in os.walk(hysope_results_download_path):
        for name in files:
            if fnmatch(name, filename_pattern):
                try:
                    with open(os.path.join(path, name), "r") as f:
                        header = f.readline()
                        # Should look like "lake=bamendjin;country=Cameroon;basin=Sanaga;lat=5.8;lon=10.55;date=2023.94951646;first_date=2010.71232877;last_date=2022.75858828;type=research;diff=public;id=1300000001576"
                        # We split this into a dict
                        header_dict = dict(item.strip().split('=')for item in header.split(';'))
                        if header_dict["basin"].lower() == basin_name.lower():
                            copy(os.path.join(path, name),
                                 os.path.join(dest_folder, get_name_from_hydrowebnext_filename(name)+".txt"))
                            count += 1
                except TypeError as e:
                    custom_logger.error(f"TypeError processing file {os.path.join(path, name)}. Skipping the file")

    custom_logger.info(f"Filtering to basin {basin_name}: {count} files copied to {dest_folder}")

    # Delete temporary download folder
    rmtree(hysope_results_download_path, ignore_errors=True)
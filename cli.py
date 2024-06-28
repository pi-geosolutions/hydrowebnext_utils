#!/usr/bin/python3
import click

from hydrowebnext_utils import download_watershed

# Default values
niger_bbox = "POLYGON((-11.60039306698639372 5.28531067974414803, -11.60039306698639372 23.95752330026016708, 15.88485121691020474 23.95752330026016708, 15.88485121691020474 5.28531067974414803, -11.60039306698639372 5.28531067974414803))"


@click.group()
def cli():
    pass


@cli.command()
@click.option('--hydroweb_product_names',
              help='Comma-separated list of Hydrowebnext product names',
              default="HYDROWEB_RIVERS_OPE,HYDROWEB_LAKES_OPE,HYDROWEB_RIVERS_RESEARCH,HYDROWEB_LAKES_RESEARCH")
@click.option('--basin', help='Basin name', default="NIGER")
@click.option('--bbox_wkt', help='WKT Polygon bounding the basin', default=niger_bbox)
@click.option('--dest_folder', help='Folder where the files will be written to', default="/tmp/niger_basin")
def download_on_watershed(hydroweb_product_names: str, basin: str, bbox_wkt: str, dest_folder: str):
    products = hydroweb_product_names.split(",")
    for product in products:
        download_watershed.download_over_extent(product, basin, bbox_wkt, dest_folder)


if __name__ == '__main__':
    cli(auto_envvar_prefix='HYDROWEBNEXT_SCRIPTS')
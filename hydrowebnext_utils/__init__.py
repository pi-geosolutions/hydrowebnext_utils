import re


def get_name_from_hydrowebnext_filename(filename) -> str:
    """
    On hydrowebnext, the station name is no more easy to get. It is using an URN-like ID almost everywhere, except on
    the file's name, which is based on the old name, the ones we have in config/hyseop_svs.yaml config file,
    but slightly different
    :param filename:
    :return: station name (str)
    """
    # drop prefix and suffix
    filename_format = r"^hydroprd_(?P<station_name>.*)_exp.txt$"
    if filename.startswith("hydroprd_L"):
        # It's a lake station. Pattern is different
        filename_format = r"^hydroprd_(?P<station_name>.*).txt$"
    filename_re = re.compile(filename_format)
    m = re.match(filename_re, filename)
    m_dict = m.groupdict()
    return m_dict.get("station_name", filename)

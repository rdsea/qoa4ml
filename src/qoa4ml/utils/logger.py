import logging

qoa_logger = logging.getLogger(f"qoa4ml---{__name__}")

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.INFO)
c_format = logging.Formatter(
    "%(module)s : %(asctime)s : %(levelname)s  - %(message)s",
    # datefmt="%d-%b-%y %H:%M:%S",
)
c_handler.setFormatter(c_format)
qoa_logger.addHandler(c_handler)

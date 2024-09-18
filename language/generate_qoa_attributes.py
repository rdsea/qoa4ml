import argparse
import json

from qoa4ml.lang.attributes import (
    QOA_ATTRIBUTES_NAME,
    QOA_ATTRIBUTES_VERSION,
    DataQualityEnum,
    MLModelQualityEnum,
    ServiceQualityEnum,
)


def enum_to_dict(enum_class):
    """Serialize an enum class to a dictionary where each key is the enum name and each value is a dictionary containing the value and description."""
    return {member.value: {"description": member.__doc__} for member in enum_class}


catalog = {
    "data": enum_to_dict(DataQualityEnum),
    "mlmodels": enum_to_dict(MLModelQualityEnum),
    "services": enum_to_dict(ServiceQualityEnum),
}


parser = argparse.ArgumentParser()
parser.add_argument(
    "--target-dir", help="Target directory to save the JSON file", default="."
)
args = parser.parse_args()

target_dir = args.target_dir

with open(
    f"{target_dir}/{QOA_ATTRIBUTES_NAME}-{QOA_ATTRIBUTES_VERSION}.json", "w"
) as f:
    f.write(json.dumps(catalog, indent=4))

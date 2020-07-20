import os
import re
import glob
from pathlib import Path
import pandas as pd
import cdblib
from loguru import logger


def main():
    dir_path = os.getcwd()
    cdbfiles = sorted(Path(dir_path).glob("D/*/*.cdb"))
    for file in cdbfiles:
        filename = os.path.basename(file).split(".")[0]
        logger.info(f"Reading cdb file for: {file}")
        with open(file, "r") as f:
            data = f.readlines()
        for i, text in enumerate(data):
            if "MATERIALS" in text:
                start_material = i
        material_data = [
            text.strip() for i, text in enumerate(data) if (i >= start_material)
        ]
        material_data_f = [re.split(",", l.strip()) for l in material_data[1:-8]]
        material_data_new = [i for i in material_data_f if "EX" in i or "DENS" in i]
        material_df = pd.DataFrame(
            material_data_new,
            columns=["A", "B", "C", "Material_name", "E", "F", "Final_value", "H"],
        )
        required_df = material_df[["Material_name", "Final_value"]]
        required_df["Final_value"] = required_df["Final_value"].astype(float)
        if not os.path.exists(f"{dir_path}/output"):
            os.makedirs(f"{dir_path}/output")
        logger.info(f"Exporting the required values...")
        required_df.to_csv(f"{os.getcwd()}/output/{filename}_material_values.csv")
    logger.success("DONE")


if __name__ == "__main__":
    main()

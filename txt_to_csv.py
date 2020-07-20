import os
import re
import glob
from pathlib import Path
import pandas as pd
from loguru import logger


dir_path = os.getcwd()
folders = sorted(Path(dir_path).glob("D/*.txt"))

for file in folders:
    with open(file, "r") as f:
        file_name = os.path.splitext(file)[0].split("/")[-1].replace(" ", "_")
        logger.info(f"Reading file: {file_name}")
        lines = f.readlines()
        final_lines = [re.split("\s+", l.strip()) for l in lines]
        df = pd.DataFrame(final_lines[1:], columns=final_lines[0])
        if not os.path.exists(f"{dir_path}/output"):
            os.makedirs(f"{dir_path}/output")
        df.to_csv(f"{dir_path}/output/{file_name}.csv")
        logger.info(f"Exported to csv for file: {file_name}")

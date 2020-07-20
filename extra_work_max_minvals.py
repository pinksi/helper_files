import pandas as pd
import os
import re
from pathlib import Path
from glob import glob
from loguru import logger
import numpy as np
import cdblib

# get current working directory
dir_path = os.getcwd()
folders = sorted(Path(dir_path).glob("D/*"))


def get_values_from_txtfile(folder):
    results = []
    try:
        # collecting all files inside the folder
        files = sorted(Path(folder).glob("*.TXT"))
        folder_name = str(folder).split("/")[-1]
        logger.info(f"Calculating values for folder: {folder_name} ...")
        for file in files:
            file_name = os.path.splitext(file.name)[0]  # eg. TRY_0
            angle = file_name.split("_")[-1]  # eg. 0 degree
            logger.info(f"Reading for file: {file_name} and angle: {angle}")
            with open(file, "r") as f:
                lines = f.readlines()
                del lines[:2]  # removing first two unwanted rows of txt file
                final_lines = [re.split("\s+", l.strip()) for l in lines]
                df = pd.DataFrame(final_lines[1:], columns=final_lines[0])
                values = [
                    angle,
                    int(
                        float(
                            df[
                                df["EQUIVALENTSTRESS"].astype("float64")
                                == df["EQUIVALENTSTRESS"].astype("float64").max()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["EQUIVALENTSTRESS"].astype("float64").max(),
                    int(
                        float(
                            df[
                                df["EQUIVALENTSTRESS"].astype("float64")
                                == df["EQUIVALENTSTRESS"].astype("float64").min()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["EQUIVALENTSTRESS"].astype("float64").min(),
                    int(
                        float(
                            df[
                                df["PRINCIPALSTRESS"].astype("float64")
                                == df["PRINCIPALSTRESS"].astype("float64").max()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["PRINCIPALSTRESS"].astype("float64").max(),
                    int(
                        float(
                            df[
                                df["PRINCIPALSTRESS"].astype("float64")
                                == df["PRINCIPALSTRESS"].astype("float64").min()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["PRINCIPALSTRESS"].astype("float64").min(),
                    int(
                        float(
                            df[
                                df["EQVSTRAIN"].astype("float64")
                                == df["EQVSTRAIN"].astype("float64").max()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["EQVSTRAIN"].astype("float64").max(),
                    int(
                        float(
                            df[
                                df["EQVSTRAIN"].astype("float64")
                                == df["EQVSTRAIN"].astype("float64").min()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["EQVSTRAIN"].astype("float64").min(),
                    int(
                        float(
                            df[
                                df["PRINCIPALSTRAIN"].astype("float64")
                                == df["PRINCIPALSTRAIN"].astype("float64").max()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["PRINCIPALSTRAIN"].astype("float64").max(),
                    int(
                        float(
                            df[
                                df["PRINCIPALSTRAIN"].astype("float64")
                                == df["PRINCIPALSTRAIN"].astype("float64").min()
                            ]["NODE"].iloc[0]
                        )
                    ),
                    df["PRINCIPALSTRAIN"].astype("float64").min(),
                ]
                logger.info(f"Values for angle: {angle} calculated!")
                results.append(values)
                #         sorting results on the basis of angle
                sorted_result = sorted(results, key=lambda x: int(x[0]))
        results_df = pd.DataFrame(
            sorted_result,
            columns=[
                "Angle",
                "NODE_EQUIVALENTSTRESS_max",
                "EQUIVALENTSTRESS_max",
                "NODE_EQUIVALENTSTRESS_min",
                "EQUIVALENTSTRESS_min",
                "NODE_PRINCIPALSTRESS_max",
                "PRINCIPALSTRESS_max",
                "NODE_PRINCIPALSTRESS_min",
                "PRINCIPALSTRESS_min",
                "NODE_EQVSTRAIN_max",
                "EQVSTRAIN_max",
                "NODE_EQVSTRAIN_min",
                "EQVSTRAIN_min",
                "NODE_PRINCIPALSTRAIN_max",
                "PRINCIPALSTRAIN_max",
                "NODE_PRINCIPALSTRAIN_min",
                "PRINCIPALSTRAIN_min",
            ],
        )
        return results_df
    except Exception as e:
        logger.error(f"Exception: {e} occurred!!")


def extract_data_from_cdb_file(cdb_file):
    with open(cdb_file[0], "r") as f:
        data = f.readlines()
    for i, text in enumerate(data):
        if "Elements" in text:
            start_element = i
        if "Component" in text:
            start_component = i
        if "MATERIALS" in text:
            start_material = i
        if "Nodes for the whole assembly" in text:
            start_nodes_xyz = i
    nodes_xyz_data = [
        text.strip()
        for i, text in enumerate(data)
        if (i >= start_nodes_xyz and i < start_element)
    ]
    element_data = [
        text.strip()
        for i, text in enumerate(data)
        if (i >= start_element and i < start_component)
    ]
    material_data = [
        text.strip() for i, text in enumerate(data) if (i >= start_material)
    ]

    # nodes and xyz value
    nodes_xyz_data = [re.split("\s+", l.strip()) for l in nodes_xyz_data[3:-2]]
    nodes_xyz_df = pd.DataFrame(
        nodes_xyz_data, columns=["NODE_PRINCIPALSTRAIN_max", "A", "B", "x", "y", "z"]
    )

    # material and nodes values
    element_data = [re.split("\s+", l.strip()) for l in element_data[4:-1]]
    element_df = pd.DataFrame(
        element_data,
        columns=[
            "Material_value",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "Node4",
            "Node3",
            "Node2",
            "Node1",
        ],
    )

    # material and final values
    material_data_f = [re.split(",", l.strip()) for l in material_data[1:-8]]
    material_data_new = [i for i in material_data_f if "EX" in i]
    material_df = pd.DataFrame(
        material_data_new,
        columns=["A", "B", "C", "D", "Material_value", "F", "Final_value", "H"],
    )

    return nodes_xyz_df, element_df, material_df


def extract_extra_node_from_xyz_range(nodes_xyz_df, principal_strain_df):
    logger.info(f"Extracting extra nodes for principal strain within range of xyz!")
    nodes_xyz_df["NODE_PRINCIPALSTRAIN_max"] = nodes_xyz_df[
        "NODE_PRINCIPALSTRAIN_max"
    ].astype(int)
    nodes_xyz_df["x"] = nodes_xyz_df["x"].astype(float)
    nodes_xyz_df["y"] = nodes_xyz_df["y"].astype(float)
    nodes_xyz_df["z"] = nodes_xyz_df["z"].astype(float)

    p_strain_xyz = pd.merge(
        principal_strain_df, nodes_xyz_df, on="NODE_PRINCIPALSTRAIN_max"
    )
    # extending range for nodes
    p_strain_xyz["x_max"] = p_strain_xyz["x"].astype(float) + 2
    p_strain_xyz["x_min"] = p_strain_xyz["x"].astype(float) - 2
    p_strain_xyz["y_max"] = p_strain_xyz["y"].astype(float) + 4
    p_strain_xyz["y_min"] = p_strain_xyz["y"].astype(float) - 4
    p_strain_xyz["z_max"] = p_strain_xyz["z"].astype(float) + 2
    p_strain_xyz["z_min"] = p_strain_xyz["z"].astype(float) - 2

    extra_principal_strain_node = [[]] * len(principal_strain_df)
    node_df_node = nodes_xyz_df["NODE_PRINCIPALSTRAIN_max"].values  # all nodes values
    node_df_x = nodes_xyz_df["x"].values
    node_df_y = nodes_xyz_df["y"].values
    node_df_z = nodes_xyz_df["z"].values
    x_max = p_strain_xyz["x_max"].values
    x_min = p_strain_xyz["x_min"].values
    y_max = p_strain_xyz["y_max"].values
    y_min = p_strain_xyz["y_min"].values
    z_max = p_strain_xyz["z_max"].values
    z_min = p_strain_xyz["z_min"].values

    for i in range(len(x_max)):
        for j in np.where(
            ((x_min[i] <= node_df_x) & (node_df_x <= x_max[i]))
            & ((y_min[i] <= node_df_y) & (node_df_y <= y_max[i]))
            & ((z_min[i] <= node_df_z) & (node_df_z <= z_max[i]))
        ):
            extra_principal_strain_node[i] = node_df_node[j]
    return extra_principal_strain_node


def extract_material_for_pstrain(element_df, all_nodes_p_strain):
    logger.info(f"Calculating material value for principal strain...")
    material_val = (element_df["Material_value"].astype(float).astype(int)).values
    nodes1 = (element_df["Node1"].astype(int)).values
    nodes2 = (element_df["Node2"].astype(int)).values
    nodes3 = (element_df["Node3"].astype(int)).values
    nodes4 = (element_df["Node4"].astype(int)).values

    node1_material_list = dict(zip(nodes1, material_val))
    node2_material_list = dict(zip(nodes2, material_val))
    node3_material_list = dict(zip(nodes3, material_val))
    node4_material_list = dict(zip(nodes4, material_val))

    material_values_list = []
    for row in all_nodes_p_strain:
        temp_list = []
        for item in row:
            try:
                temp_list.append(node1_material_list[item])
            except KeyError:
                try:
                    temp_list.append(node2_material_list[item])
                except KeyError:
                    try:
                        temp_list.append(node3_material_list[item])
                    except:
                        temp_list.append(node4_material_list[item])
        material_values_list.append(set(temp_list))
    return material_values_list


def calculate_final_value_from_material(material_df, material_p_strain):
    logger.info(f"Calculating final value...")
    material_value = material_df["Material_value"].astype(int).values
    final_value = material_df["Final_value"].astype(float).values

    material_final_val_list = dict(zip(material_value, final_value))
    final_value_list = []
    for row in material_p_strain:
        temp_list = []
        for items in row:
            temp_list.append(material_final_val_list[items])
        final_value_list.append(set(temp_list))
    return final_value_list


def get_p_strain(folder, node):
    p_strain_values = []
    files = sorted(Path(folder).glob("*.TXT"))
    folder_name = str(folder).split("/")[-1]
    logger.info(f"Calculating values for folder: {folder_name} ...")
    for file in files:
        file_name = os.path.splitext(file.name)[0]
        angle = file_name.split("_")[-1]
        logger.info(f"Reading for file: {file_name} and angle: {angle}")
        with open(file, "r") as f:
            lines = f.readlines()
            del lines[:2]
            final_lines = [re.split("\s+", l.strip()) for l in lines]
            df = pd.DataFrame(final_lines[1:], columns=final_lines[0])
            extra_node_strain = float(
                df[df["NODE"].astype(float).astype(int) == node][
                    "PRINCIPALSTRAIN"
                ].iloc[0]
            )
            p_strain_values.append((angle, extra_node_strain))
    sorted_p_values = sorted(p_strain_values, key=lambda x: int(x[0]))
    return sorted_p_values


def main():
    error_list = []
    # iterating for all folders
    for folder in folders:
        try:
            # checking if all the folders values are directory or not
            if os.path.isdir(folder):
                folder_name = str(folder).split("/")[-1]
                # values from all angles
                results_df = get_values_from_txtfile(folder)
            else:
                logger.error(f"This {folder} is not a directory")
                break
            principal_strain_df = results_df[
                ["NODE_PRINCIPALSTRAIN_max", "PRINCIPALSTRAIN_max"]
            ]
            logger.info("Extracting data from cdb file...")
            cdbfile = sorted(Path(folder).glob("*.cdb"))
            nodes_xyz_df, element_df, material_df = extract_data_from_cdb_file(cdbfile)
            extra_principal_strain_node = extract_extra_node_from_xyz_range(
                nodes_xyz_df, principal_strain_df
            )
            results_df["EXTRA_NODE_PRINCIPALSTRAIN"] = extra_principal_strain_node
            all_nodes_p_strain = [
                i.tolist() for i in results_df["EXTRA_NODE_PRINCIPALSTRAIN"].tolist()
            ]
            # adding node_principal_max to all_nodes_list
            nodes_p_strain_max = results_df["NODE_PRINCIPALSTRAIN_max"].values
            for i, val in enumerate(nodes_p_strain_max):
                all_nodes_p_strain[i].append(val)
            # removing duplicate nodes
            all_nodes_p_strain = [set(row) for row in all_nodes_p_strain]
            # update extra node principal strain
            results_df["EXTRA_NODE_PRINCIPALSTRAIN"] = all_nodes_p_strain
            material_values_list = extract_material_for_pstrain(
                element_df, all_nodes_p_strain
            )
            results_df["MATERIAL_PRINCIPALSTRAIN"] = material_values_list
            material_p_strain = results_df["MATERIAL_PRINCIPALSTRAIN"].values
            final_value_list = calculate_final_value_from_material(
                material_df, material_p_strain
            )
            results_df["FINAL_VALUE_PRINCIPAL_STRAIN"] = final_value_list
            if not os.path.exists(f"{dir_path}/output"):
                os.makedirs(f"{dir_path}/output")
            results_df.to_csv(f"{dir_path}/output/{folder_name}.csv")

            logger.info(f"Computing principal strain for extra nodes: ")
            unique_extra_nodes = set(
                [
                    n
                    for node in results_df["EXTRA_NODE_PRINCIPALSTRAIN"].values
                    for n in node
                ]
            )
            all_nodes_p_values = []
            for node in unique_extra_nodes:
                p_strain_values = get_p_strain(folder, node)
                all_nodes_p_values.append((node, p_strain_values))
            p_strain_df = pd.DataFrame(
                all_nodes_p_values, columns=["NODE", "ANGLE_PRINCIPAL_STRAIN"]
            )
            p_strain_df.to_csv(f"{dir_path}/output/{folder_name}_pstrain.csv")
        except Exception as e:
            logger.error(f"Exception {e} occured at file: {folder_name}")
            error_list.append(folder_name)


if __name__ == "__main__":
    main()

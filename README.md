This repository includes all the scripts created to extract data from different cdb files and text files and do some post-processing in them.

1. `extra_work_max_minvals.py`: 

    Input:
    ```
    D
     |_ AB029
        |_ 1.txt
        |_ 2.txt
        |_ ....txt
        |_ abc.cdb
    ```
    1. folder with different `.TXT` files [containing values and nodes for different sections]
    2. `.cdb` file [containing all the values of materials, elements for each node]

    Output:
    1. csv file with maximum and minimum values for these section, their corresponding nodes,elements, materials and their final values.
    ```
    CSV files headers:
    ---
    Angle |	NODE_EQUIVALENTSTRESS_max |	EQUIVALENTSTRESS_max | NODE_EQUIVALENTSTRESS_min | EQUIVALENTSTRESS_min |	NODE_PRINCIPALSTRESS_max | PRINCIPALSTRESS_max |	NODE_PRINCIPALSTRESS_min |	PRINCIPALSTRESS_min |	NODE_EQVSTRAIN_max |	EQVSTRAIN_max |	NODE_EQVSTRAIN_min |	EQVSTRAIN_min |	NODE_PRINCIPALSTRAIN_max |	PRINCIPALSTRAIN_max |	NODE_PRINCIPALSTRAIN_min |	PRINCIPALSTRAIN_min |	EXTRA_NODE_PRINCIPALSTRAIN |	MATERIAL_PRINCIPALSTRAIN |	FINAL_VALUE_PRINCIPAL_STRAIN
    ```
    2. csv file with node values for extra principal strain values
    ```
    NODE |	ANGLE_PRINCIPAL_STRAIN
```

2. `material_vals.py`: Extracting material_name and it's final_value from "Material" section of cdb file

     Input: `cdb file`

     Output: `csv file with material_name and it's value`
     `Material_name | Final_value`

3. `txt_to_csv.py`: Converting text file into csv files.

     Input: `txt file`

     Output: ``csv file`

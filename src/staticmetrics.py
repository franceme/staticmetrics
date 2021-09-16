#!/bin/env python3
import sys
import logging
import os
from pandas import DataFrame as df
from pathlib import Path
from radon.complexity import cc_visit

global_columns = [
    'File Qual Name',
    'Program Lines',
    'Total Lines',
    'Count of Imports',
    'CC Complexity'
]

VERSION = "0.0.1"
NAME = 'pythonmetrics'

#region FrontEnd
def get_output_types():
    output_type = {x.split("_")[-1]:x for x in dir(df) if x.startswith("to_")}

    for idx in range(len(output_type.keys())):
        keyz = list(output_type.keys())
        if keyz[idx] == 'excel':
            output_type['xlsx'] = output_type.pop('excel')
        if keyz[idx] == 'latex':
            output_type['tex'] = output_type.pop('latex')

    return output_type

def arguments(string_set):
    if '-h' in string_set:
        print(f"""{NAME} {VERSION}
        {NAME} Usage:
        ----------------------------------------------------
        ./{NAME}.py -v: Display the version
        ./{NAME}.py -h: Displays the help information

        > General Usage
        * []: Required
        * (): Optional

        ./{NAME}.py [Source Path](--OUTPUT=File.[certain type])
        * Source Path: The file or path of the code you want to scan
        * --OUTPUT: The file you want the output to be put to
          * The extension of the output has to be {', '.join(get_output_types().keys())}
        """)
        return 0
    elif '-v' in string_set:
        print(f"{NAME}: {VERSION}")
        return 0
    if len(string_set) < 2:
        logging.critical("Missing the source path")
        return 1
    elif not os.path.exists(string_set[1]):
        logging.critical(f"The source path {string_set[1]} does not exist")
        return 1
    input_logging = list(filter(lambda x: str(x).startswith('-V'), string_set))

    if os.path.isfile(string_set[1]):
        project_name = f"{os.path.basename(string_set[1]).replace('.py','')}"
    elif os.path.isdir(string_set[1]):
        project_name = f"{os.path.normpath(string_set[1]).split(os.sep)[-1]}"

    if len(string_set) == 2:
        output_file,output_type = f"{os.path.basename(string_set[1])}.csv","csv"
    else:
        try:
            output_file = string_set[2].replace('--OUTPUT=','')
            output_type = output_file.split(".")[-1]
            output_type_set = get_output_types()
            if output_type not in [str(x) for x in output_type_set.keys()]:
                output_file = output_file.replace(output_type, "csv")
                output_type = "csv"

        except:
            output_file,output_type = f"{os.path.basename(string_set[1])}.csv","csv"

    logging.debug(f"""Arguments: {{
        'Input Path': {string_set[1]},
        'Output File': {output_file},
        'Output Type': {output_type}
    }}""")
    return {
        'Input Path': string_set[1],
        'Output File': output_file,
        'Output Type': output_type
    }

def main(string):
    args_trimmed = arguments(string)
    if isinstance(args_trimmed, int):
        return args_trimmed

    output = gather_info(args_trimmed['Input Path'],
        args_trimmed['Output File'],
        args_trimmed['Output Type']
    )

    if (string[0] == '' or string[0].startswith('./')) and not isinstance(output, int):
        return 1
    print(output)
    return 0

def gather_info(path:str, output_file:str, output_type:str, write_out:bool=True) -> str:
    output_container = df(
        [],
        columns=global_columns
    )

    print("Starting Scan")
    if os.path.exists(path):
        if os.path.isfile(path):
            output_container=output_container.append(gather_information_from_single_file(path))
        else: #isdir(path)
            foils = list(Path(path).rglob("*.py"))
            logging.debug(f"The current foils: {foils}")
            for idx,file in enumerate(foils):
                print(f"{idx+1}/{len(foils)} :Scanning file {file}")
                output_container=output_container.append(gather_information_from_single_file(str(file)))

    output_container.set_index(global_columns[0], inplace=True)

    if write_out:
        output_container.__getattr__(get_output_types().get(output_type))(output_file)

    print("Done running")
    return output_file

def gather_information_from_single_file(path:str)->df:
    info = infor(path)

    return df(
        [[
            fully_qual_name(path),
            info['Program Lines'],
            info['Total Lines'],
            len(info['Imports']),
            info['MCC'],
        ]],
        columns=global_columns
    )

def fully_qual_name(path:str)->str:
    return str(path.replace("//",".").replace(".py",""))

def infor(my_foil: str) -> {}:
    total = -1
    no_cmt = -1
    imports = []
    mcc = -1

    try:
        with open(my_foil, 'r', errors='ignore') as foil:
            s_multi, d_multi,raw_lines = False, False,foil.readlines()
            for line in raw_lines:
                if "import" in line.strip().lower() and not line.strip().startswith("#") and not s_multi and not d_multi:
                    imports += [line.strip()]

                total += 1
                line = line.lstrip()

                if not s_multi and line.startswith("'''"):
                    s_multi = True
                    line = line.replace("'''", "")

                if not d_multi and line.startswith('"""'):
                    d_multi = True
                    line = line.replace('"""', '')

                if not line.startswith('#') and line != "" and not (s_multi or
                                                                    d_multi):
                    no_cmt += 1

                if s_multi and line.rstrip().endswith("'''"):
                    s_multi = False

                if d_multi and line.rstrip().endswith('"""'):
                    d_multi = False
            mcc = sum(x.complexity for x in cc_visit(''.join(raw_lines)))

    except:
        pass

    return {'Total Lines': total, 'Program Lines': no_cmt, 'Imports':imports, 'MCC':mcc}
#endregion

if __name__ == '__main__':
    sys.exit(main(sys.argv))

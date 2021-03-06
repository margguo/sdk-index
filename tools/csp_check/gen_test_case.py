import os
import json
import time
import logging
import random
import textwrap
from check_tools import execute_command


def gen_chip_test_case(json_path, mcu_config_path):
    generate_and_import_project(json_path, mcu_config_path)
    test_case = ''
    for chip_json in os.listdir(mcu_config_path):
        project_name = chip_json.split(".json")[0]
        test_case_example = """
                def test_{0}():
                    assert csp_test("{0}") is True
                """.format(project_name)
        test_case_format = textwrap.dedent(test_case_example)
        test_case += "\n" + test_case_format
        chip_json_path = os.path.join(mcu_config_path, chip_json)

        execute_command("rm -rf {0}".format(chip_json_path))
    with open("csp_test_case.py", "a") as f:
        f.write(test_case)


def find_mcu_in_json_file(json_path, mcu_config_path):
    with open(json_path, 'r') as f:
        data = f.read()
    parameter_dict = json.loads(data)
    os.mkdir(mcu_config_path)
    test_numbers = int(len(parameter_dict))
    if test_numbers > 100:
        test_numbers = 100
    mcu_dict = dict(random.sample(parameter_dict.items(), test_numbers))

    for mcu in mcu_dict:
        bare_metal_list = {"parameter": parameter_dict[mcu]["parameter"]}
        mcu_json = os.path.join(mcu_config_path, mcu + ".json")
        with open(mcu_json, "w") as f:
            f.write(str(json.dumps(bare_metal_list, indent=4)))
    os.remove(json_path)


def generate_and_import_project(json_path, mcu_config_path):
    find_mcu_in_json_file(json_path, mcu_config_path)
    begin_time = time.time()
    logging.info("Project generate start.")
    project_number = 0
    for chip_json in os.listdir(mcu_config_path):
        project_number += 1
        project_name = chip_json.split(".json")[0]
        json_path = os.path.join("mcu_config", chip_json)
        logging.info("number : {1}, Project name : {0}.".format(project_name, project_number))
        get_generate_result(json_path)
    logging.info("Project generate end, time consuming : {0}.".format(time.time() - begin_time))

    cmd_pre = r"/rt-thread/eclipse/eclipse -nosplash --launcher.suppressErrors "\
              r"-application org.eclipse.cdt.managedbuilder.core.headlessbuild " \
              r"-data '/rt-thread/eclipse/workspace'"
    cmd = cmd_pre + ' -importAll "file:/rt-thread/workspace" 2> /dev/null'

    logging.info("Project import start.")
    begin_time = time.time()
    os.system(cmd)
    logging.info("Project import end. time consuming : {0}.".format(time.time() - begin_time))


def get_generate_result(csp_json_path):
    execute_command("chmod 777 /RT-ThreadStudio/plugins/gener/prj_gen")
    # judge sdk update type (csp or bsp)
    try:
        check_type = os.environ['SDK_CHECK_TYPE']
    except Exception as e:
        logging.error(": {0}".format(e))

    logging.debug("project_json_info: {0}".format(check_type))
    os.system("cat {0}".format(csp_json_path))

    if check_type.find("csp_check") != -1:
        cmd = r"/RT-ThreadStudio/plugins/gener/prj_gen --csp_project=true --csp_parameter_file={0} -n xxx 2> generate.log".format(csp_json_path)
    else:
        cmd = r"/RT-ThreadStudio/plugins/gener/prj_gen --bsp_project=true --bsp_parameter_file={0} -n xxx 2> generate.log".format(csp_json_path)
    execute_command(cmd)

    try:
        with open("generate.log", "r") as f:
            log_info = f.readlines()
    except Exception as e:
        print("Error message : {0}".format(e))
    else:
        for line in log_info:
            if line.find("Error") != -1 or line.find("error") != -1 or line.find("ERROR") != -1:
                logging.error(line)
            else:
                logging.debug(line)

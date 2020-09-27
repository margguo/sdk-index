import os
import json
import logging
import subprocess
from check_tools import execute_command
from gen_bsp_json import gen_bsp_sdk_json
from gen_test_case import gen_chip_test_case


def bsp_check_test():
    with open('/rt-thread/sdk-index/tools/bsp_update_url.json', "r") as f:
        bsp_update_url = json.loads(f.read())[0]

    execute_command("wget -O /rt-thread/bsp.zip {0}".format(bsp_update_url))
    execute_command("unzip {0} -d /rt-thread/rt-thread-bsp".format("/rt-thread/bsp.zip"))
    execute_command("rm -rf /rt-thread/bsp.zip")
    prj_path = "/RT-ThreadStudio/plugins/gener/"
    if not os.path.exists(prj_path):
        os.makedirs(prj_path)

    execute_command("cp -r -f {0} {1}".format("prj_gen", "/RT-ThreadStudio/plugins/gener/"))

    # find bsp path
    real_bsp_path = None
    for dir in os.listdir("/rt-thread/rt-thread-bsp"):
        if dir.find("sdk-bsp") != -1:
            real_bsp_path = os.path.join("/rt-thread/rt-thread-bsp", dir)
            break
    if real_bsp_path is None:
        logging.error("can't find bsp path, please check it!")

    gen_bsp_sdk_json(real_bsp_path, "/rt-thread/sdk-index/", "/rt-thread/workspace/")
    # gen test case
    gen_chip_test_case("bsp_chips.json", "mcu_config")

    os.system("python csp_test_case.py")

    execute_command("exit")


if __name__ == "__main__":
    bsp_check_test()

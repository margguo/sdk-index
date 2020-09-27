import time
import json
import logging
import subprocess


def execute_command(cmd_string, cwd=None, shell=True):
    """Execute the system command at the specified address."""

    sub = subprocess.Popen(cmd_string, cwd=cwd, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, shell=shell, bufsize=4096)

    stdout_str = ''
    while sub.poll() is None:
        stdout_str += str(sub.stdout.read(), encoding="UTF-8")
        time.sleep(0.1)

    return stdout_str


def init_logger():
    log_format = "[%(filename)s %(lineno)d %(levelname)s] %(message)s "
    date_format = '%Y-%m-%d  %H:%M:%S %a '
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        datefmt=date_format,
                        )


def main():
    init_logger()
    execute_command("python -m pip install --upgrade pip")
    # get update csp url
    try:
        with open('/rt-thread/sdk-index/tools/csp_update_url.json', "r") as f:
            sdk_url = json.loads(f.read())[0]
        # csp ci check
        logging.info("csp check test!")
        exit(0)
    except Exception as e:
        logging.error("\nError message : {0}.".format(e))

    # get update bsp url
    try:
        with open('/rt-thread/sdk-index/tools/bsp_update_url.json', "r") as f:
            sdk_url = json.loads(f.read())[0]
        # bsp ci chck
        logging.info("bsp check test!")
        exit(0)
    except Exception as e:
        logging.error("\nError message : {0}.".format(e))
        exit(1)

if __name__ == "__main__":
    main()

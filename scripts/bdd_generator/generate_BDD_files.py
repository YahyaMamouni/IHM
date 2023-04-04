import sys
from datetime import datetime
import os
from generate_functions import (
    generate_bdd_files,
    get_info_from_conf,
    verify_git,
)
from time import sleep

root_var = "unused"


def main():
    (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_generate_bdd_problems,
        path_of_ivvq_folder,
        path_of_results,
    ) = get_info_from_conf(sys.argv[1])
    # is_ready_to_commit = verify_git(path_of_ivvq_folder)
    is_ready_to_commit = True
    if is_ready_to_commit:
        # initialization

        time_now = str(datetime.now())
        path_of_csv_folder = (
            path_of_results
            + "/"
            + str(time_now)[:19]
            + "_"
            + vivaldi_campaign.split("/")[-1]
        )

        if not os.path.exists(path_of_csv_folder):
            os.makedirs(path_of_csv_folder)

        generate_bdd_files(
            vivaldi_campaign,
            suite_bdd,
            test_py,
            path_of_csv_folder,
            path_of_csv_folder + csv_generate_bdd_problems,
            False,
            root_var,
            False,
        )

        if len(os.listdir(path_of_csv_folder)) == 0:
            os.rmdir(path_of_csv_folder)

        # To not close the terminal
    while True:
        sleep(3)


if __name__ == "__main__":
    main()

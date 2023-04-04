from generate_results_functions import (
    list_of_test_cases,
    import_from_config,
    verification_before_execution,
    importing_data_from_squish_to_vivaldi,
    verify_git,
)


from datetime import datetime
import os
import sys
import csv
from time import sleep


def main():
    version_under, soft_env, hard_env = (
        "version3.1",
        "Software Test Environment 1",
        "Hardware Test Environment 2",
    )
    (
        vivaldi_campaign,
        suite_bdd,
        squish_runner_path,
        xml_version,
        result_xml,
        path_of_results,
        csv_file_before_execution,
        path_of_ivvq_folder,
    ) = import_from_config(sys.argv[1])
    # is_ready_to_commit = verify_git(path_of_ivvq_folder)
    is_ready_to_commit = True
    is_bad_recorded = True
    if is_ready_to_commit:
        # initialization

        test_cases_line, test_cases_vivaldi = list_of_test_cases(vivaldi_campaign)
        line_of_execution = (
            squish_runner_path + suite_bdd + test_cases_line + xml_version + result_xml
        )
        xml_name = result_xml + "/results.xml"

        # Creating the folder of results
        time_now = datetime.now()
        campaign_name = vivaldi_campaign.split("/")[-1]
        path_of_time_folder = (
            path_of_results + "/" + str(time_now)[:19] + "_" + campaign_name
        )
        os.makedirs(path_of_time_folder)

        # calling functions
        with open(
            path_of_time_folder + csv_file_before_execution, "w", newline=""
        ) as csv_file:
            writer = csv.writer(
                csv_file, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL
            )
            vivaldi_files, ready_to_execute = verification_before_execution(
                suite_bdd, vivaldi_campaign, writer, test_cases_vivaldi, path_of_results
            )
            if ready_to_execute:
                print("\nExecuting Squish tests...\n")
                os.system(line_of_execution)
                print("\nSquish tests are executed\n")
                is_bad_recorded = importing_data_from_squish_to_vivaldi(
                    xml_name,
                    vivaldi_files,
                    path_of_time_folder,
                    version_under,
                    soft_env,
                    hard_env,
                )
            else:
                print("Execution failed : Check the results folder")

        file_path = path_of_time_folder + csv_file_before_execution
        if os.stat(file_path).st_size == 0:
            os.remove(file_path)
        if not is_bad_recorded:
            print("Execution of BDD tests and filling Vivaldi files succeeded")
        else:
            print("\nBDD files are not recorded correctly : " "Check CSV file\n")

    while True:
        sleep(3)


if __name__ == "__main__":
    main()

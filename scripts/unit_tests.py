# Keep in mind all the campaigns used in the unit tests contain one test each.
# Results of tests are found in tests/results_unit_tests
# /tempo_unit_test_results folder (since they're
# deleted after each assert it's empty)
# You can see the results if you comment the remove function in the tests
# We delete the results in order to avoid confusion and storage
# We can find the results we use to compare with in
# tests/results_for_the_predicted_tests
# The tests (Vivaldi) we use in order to run our unit tests can be
# found in tests/generate_bdd & tests/import_files

import filecmp
import csv
from bdd_generator.generate_functions import generate_bdd_files
from results_generator.generate_results_functions import (
    list_of_test_cases,
    verification_before_execution,
    importing_data_from_squish_to_vivaldi,
)

import os
import pytest
from lxml import etree
import shutil


# Main function of the Generation SCRIPT used in unit tests. We choose the given
# conf in the beginning by affecting
# variables. This function takes as an argument, campaign of Vivaldi
def is_bdd_generated(vivaldi_campaign):
    # Affecting variables we are going to use
    test_py = "../src/test.py"
    csv_error_file = "/generate_bdd_problems.csv"
    # Recovering test folders from Vivaldi campaign, starting with "tst"
    list_of_vivaldi_test_folder_names = [
        x for x in os.listdir(vivaldi_campaign + "/TestSuites") if x[0:3] == "tst"
    ]
    # Path of the folder going to contain the csv file (In case there are errors)
    bdd_results_folder = (
        "../tests/results_unit_tests" "/tempo_unit_test_results/generate_bdd"
    )

    # Calling generate_bdd_files function that is going to verify the tests and
    # decide either to create BDD files or no
    # This function returns a bool. True in case the BDD files are generated and
    # False if not
    is_generated = generate_bdd_files(
        vivaldi_campaign,
        bdd_results_folder,
        test_py,
        bdd_results_folder + csv_error_file,
        True,
        False,
        False,
    )
    # Returning bool result and the path of the squish folder containing the results
    return is_generated, list_of_vivaldi_test_folder_names[0]


# Main function of the import SCRIPT used in unit tests. We choose the given conf
# in the beginning by affecting
# variables. This function takes as an argument, campaign of Vivaldi
def is_xml_file_imported(vivaldi_campaign):
    # Affecting variables we are going to use
    version_under, soft_env, hard_env = (
        "version3.1",
        "Software Test Environment 1",
        "Hardware Test Environment 2",
    )
    suite_bdd = "../tests/suite_bdd"
    squish_runner_path = (
        "~/squish-for-qt-7.0.0/bin/squishrunner --host 172.17.0.1 --testsuite "
    )
    xml_version = " --reportgen xml3.5,"
    result_xml = "/tmp/results"
    csv_file_before_execution = "/beforeExecution.csv"
    # Recovering test cases in order to execute the tests and fill the XML files
    test_cases_line, test_cases_vivaldi = list_of_test_cases(vivaldi_campaign)
    # Line of execution which we are going to use in order to execute the tests
    line_of_execution = (
        squish_runner_path + suite_bdd + test_cases_line + xml_version + result_xml
    )
    # Recovering the xml file, actual time and the campaign name
    xml_name = result_xml + "/results.xml"
    # Creating the result folder taking the name : time_test_name
    filled_files_folder = (
        "../tests/results_unit_tests/" "tempo_unit_test_results/import_files"
    )
    # Opening the csv file of errors
    with open(
        filled_files_folder + csv_file_before_execution, "w", newline=""
    ) as csv_file:
        # Defining the writer we are going to use for the csv file
        writer = csv.writer(
            csv_file, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL
        )
        # Verifying before starting the execution if all conditions are respected
        # including : Format, name of steps and
        # tests
        vivaldi_files, ready_to_execute = verification_before_execution(
            suite_bdd, vivaldi_campaign, writer, test_cases_vivaldi
        )
        # If the verification is valid we execute the tests and, we start the
        # import operation
        if ready_to_execute:
            os.system(line_of_execution)
            importing_data_from_squish_to_vivaldi(
                xml_name,
                vivaldi_files,
                filled_files_folder,
                version_under,
                soft_env,
                hard_env,
            )
            # is_xml_imported equal True means that the import operation went good
            is_xml_imported = True
        else:
            print("Execution failed : Check the results folder")
            # is_xml_imported equal False means the import operation failed due to
            # errors that can be found in the
            # csv file
            is_xml_imported = False
    # csv file path, checking if it's empty. In case if it's empty we delete it.
    # Else we keep it
    file_path = filled_files_folder + csv_file_before_execution
    if os.stat(file_path).st_size == 0:
        os.remove(file_path)
    print("Closing...")
    # Returning the bool result and the folder of results
    return is_xml_imported


# Function to initialize the filled XML files (Initializing : Deleting time from
# the file)
def init_vivaldi_file(folder_path):
    # This is the location of the reformatted files, the XML filled files but without
    # a date (FreeColumn1)
    unit_test_folder = "../tests/results_unit_tests/unit_test_import_script/"
    # Parser used in order to keep the CDATA
    parser = etree.XMLParser(strip_cdata=False)
    # We return a list even though we are going to use only one element
    ivv_xml_files = [y for y in os.listdir(folder_path) if y[-7:] == "IVV.xml"]
    # Full path of the file we are going to use
    file_full_path = folder_path + "/" + ivv_xml_files[0]
    # Initializing this file into a tree
    file_tree = etree.parse(file_full_path, parser)
    # Initializing the tree
    for elem in file_tree.iter():
        if elem.text is None:
            elem.text = ""
    # Deleting time from the tree
    for elem in file_tree.iter("FreeColumn1"):
        if elem.text is not None:
            elem.text = ""
    for elem in file_tree.iter("LastRunDate"):
        if elem.text is not None:
            elem.text = ""
    # Writing the new adapted file in the unit_test_folder
    file_tree.write(
        unit_test_folder + ivv_xml_files[0], encoding="utf-8", standalone="yes"
    )
    # Returning the file path
    return unit_test_folder + ivv_xml_files[0]


def remove_folder_elements(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:  # pragma: no cover
            print("Failed to delete %s. Reason: %s" % (file_path, e))


# Update generate_bdd_elements_fail awaited result
@pytest.mark.parametrize(
    "vivaldi_campaign,awaited_result",
    [
        (
            "../tests/generate_bdd/generate_bdd_elements_fail",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_1",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_1"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_2",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_2"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_3",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_3"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_4",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_4"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_5",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_5"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_6",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_6"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_7",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_7"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_8",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_8"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_9",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_9"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_10",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_10"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_fail_11",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_fail_11"
            "/generate_bdd_problems.csv",
        ),
        (
            "../tests/generate_bdd/generate_bdd_elements_success_1",
            "../tests/results_for_the_predicted_tests/generate_bdd/test_success_1"
            "/test.feature",
        ),
    ],
)
def test_generate_bdd(vivaldi_campaign, awaited_result):
    bdd_results_folder = (
        "../tests/results_unit_tests" "/tempo_unit_test_results/generate_bdd"
    )
    csv_file = bdd_results_folder + "/generate_bdd_problems.csv"
    bool_result, test_name = is_bdd_generated(vivaldi_campaign)
    if not bool_result:
        assert filecmp.cmp(csv_file, awaited_result)
    else:
        test_path = bdd_results_folder + "/" + test_name + "/test.feature"
        assert filecmp.cmp(test_path, awaited_result)
    remove_folder_elements(bdd_results_folder)


@pytest.mark.parametrize(
    "vivaldi_campaign,awaited_result,result",
    [
        (
            "../tests/import_files/test_1",
            "../tests/results_for_the_predicted_tests/import_files/test_1",
            True,
        ),
        (
            "../tests/import_files/test_2",
            "../tests/results_for_the_predicted_tests/import_files/test_2",
            True,
        ),
        (
            "../tests/import_files/test_3",
            "../tests/results_for_the_predicted_tests/import_files/test_3",
            True,
        ),
        (
            "../tests/import_files/test_4",
            "../tests/results_for_the_predicted_tests/import_files/test_4",
            True,
        ),
        (
            "../tests/import_files/test_5",
            "../tests/results_for_the_predicted_tests/import_files/test_5",
            True,
        ),
        (
            "../tests/import_files/test_6",
            "../tests/results_for_the_predicted_tests/import_files/test_6",
            True,
        ),
        (
            "../tests/import_files/test_7",
            "../tests/results_for_the_predicted_tests/import_files/test_7",
            True,
        ),
        (
            "../tests/import_files/test_8",
            "../tests/results_for_the_predicted_tests/import_files/test_8",
            True,
        ),
        (
            "../tests/import_files/test_9_format_fail",
            "../tests/results_for_the_predicted_tests/import_files/test_9_format_fail",
            True,
        ),
        (
            "../tests/import_files/test_10_steps_fail",
            "../tests/results_for_the_predicted_tests/import_files/test_10_steps_fail",
            True,
        ),
        (
            "../tests/import_files/test_with_no_match",
            "../tests/results_for_the_predicted_tests/import_files/test_with_no_match",
            True,
        ),
        (
            "../tests/import_files/test_11",
            "../tests/results_for_the_predicted_tests/import_files/test_11",
            True,
        ),
        (
            "../tests/import_files/test_12",
            "../tests/results_for_the_predicted_tests/import_files/test_12",
            True,
        ),
    ],
)
# test_12 : case of missing vivaldi steps only
# test_11 : case of missing Squish steps only
# before running this part. All of these tests must have their BDD tests in suite_bdd
# Step 1: Run ../tests/import_files/import_files_pass in order to generate all the BDD
# files
# Step 2: Run the tests
def test_import_results(vivaldi_campaign, awaited_result, result):
    result_folder = (
        "../tests/results_unit_tests/" "tempo_unit_test_results/import_files"
    )
    is_xml_filled = is_xml_file_imported(vivaldi_campaign)
    if not is_xml_filled:
        assert (
            filecmp.cmp(
                result_folder + "/beforeExecution.csv",
                awaited_result + "/beforeExecution.csv",
            )
            == result
        )
    else:
        tree_1 = init_vivaldi_file(result_folder)
        tree_2 = init_vivaldi_file(awaited_result)
        assert filecmp.cmp(tree_1, tree_2) == result
    remove_folder_elements(result_folder)

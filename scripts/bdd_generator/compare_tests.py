import csv
import os
import subprocess
from datetime import datetime

from lxml import etree


import sys


def split_displayed_msg(displayed_message: str, writer: csv.writer) -> None:
    list_by_line = displayed_message.split("\n")
    for my_line in list_by_line:
        writer.writerow([my_line])
    writer.writerow("")


def then_given_error_list(i_ivv_tree):
    displayed_message = ""
    step_counter = 0
    for case in i_ivv_tree.xpath("./Cases/Case"):
        case_identifier = case.find("./Identification").text
        paragraph_identification = ""
        for step in case.xpath("./Steps/Step"):
            step_context = step.find("./Context").text
            step_identifier = step.find("./Identification").text
            if step_context != "" and step_context[0] == "P":
                paragraph_identification = step_context
            if step_identifier is None or step_identifier == "":
                step_identifier = step_context

            step_description = step.find("./StepDescription/StepDescription").text
            step_expected_result = step.find("./ExpectedResult/ExpectedResult").text
            step_counter += 1
            step_before_format = step_description + " " + step_expected_result
            step_after_format = " ".join(step_before_format.split())
            if ("(PR)" in step_after_format) and step_context != "X":
                # Removing "(PR)" from display
                problematic_step = (
                    "Step "
                    + str(step_counter)
                    + ";"
                    + "["
                    + case_identifier
                    + "-"
                    + paragraph_identification
                    + "-"
                    + step_identifier
                    + "]"
                    + ";Given "
                    + step_after_format.replace("(PR)", "")
                    + ";Type must be X\n"
                )
                displayed_message += (problematic_step.replace("--", "-")).replace(
                    "-]", "]"
                )
            elif step_context == "" and step_expected_result == "":
                problematic_step = (
                    "Step "
                    + str(step_counter)
                    + ";"
                    + "["
                    + case_identifier
                    + "-"
                    + paragraph_identification
                    + "-"
                    + step_identifier
                    + "]"
                    + ";Then "
                    + step_after_format
                    + ";Expected result must not be empty\n"
                )
                displayed_message += (problematic_step.replace("--", "-")).replace(
                    "-]", "]"
                )
    return displayed_message


# Equalizing Vivaldi & Squish missing steps lists, in order to display them in parallel
def equalize_lists(vivaldi_remaining_steps, squish_remaining_steps):
    vivaldi_len_list = len(vivaldi_remaining_steps)
    squish_len_list = len(squish_remaining_steps)
    difference_between_lens = abs(vivaldi_len_list - squish_len_list)

    if vivaldi_len_list > squish_len_list:
        squish_remaining_steps += difference_between_lens * [
            "(None) [None]Step doesn't exist"
        ]
    else:
        vivaldi_remaining_steps += difference_between_lens * [
            "(None) [None]Step doesn't exist"
        ]

    return vivaldi_remaining_steps, squish_remaining_steps


"""
def display_list_csv(writer, vivaldi_remaining_steps, squish_remaining_steps):
    vivaldi_len_list = len(vivaldi_remaining_steps)
    squish_len_list = len(squish_remaining_steps)
    list_length = max(vivaldi_len_list, squish_len_list)
    vivaldi_remaining_steps, squish_remaining_steps = equalize_lists(
        vivaldi_remaining_steps, squish_remaining_steps
    )
    writer.writerow(["Vivaldi"] + [""] + [""] + [""] + ["Squish"] + [""])
    writer.writerow([""])
    for i in range(list_length):
        vivaldi_element = vivaldi_remaining_steps[i].split(")")
        squish_element = squish_remaining_steps[i].split(")")
        vivaldi_element_identifier = str([vivaldi_element[1]]).split("]")[0] + "]"
        vivaldi_element_title = str([vivaldi_element[1]]).split("]")[1]
        squish_element_identifier = str([squish_element[1]]).split("]")[0] + "]"
        squish_element_title = str([squish_element[1]]).split("]")[1]
        writer.writerow(
            [vivaldi_element[0][1:]]
            + [vivaldi_element_identifier[3:]]
            + [vivaldi_element_title[:-1]]
            + [""]
            + [squish_element[0][1:]]
            + [squish_element_identifier[3:]]
            + [squish_element_title[:-1]]
        )
    writer.writerow([""])"""


def display_list_csv(writer, vivaldi_remaining_steps, squish_remaining_steps):
    vivaldi_len_list = len(vivaldi_remaining_steps)
    squish_len_list = len(squish_remaining_steps)
    list_length = max(vivaldi_len_list, squish_len_list)
    vivaldi_remaining_steps, squish_remaining_steps = equalize_lists(
        vivaldi_remaining_steps, squish_remaining_steps
    )
    writer.writerow(["Vivaldi"] + [""] + [""] + [""] + ["Squish"] + [""])
    writer.writerow([""])
    for i in range(list_length):
        vivaldi_element = vivaldi_remaining_steps[i]
        squish_element = squish_remaining_steps[i]
        vivaldi_element_identifier = ""
        squish_element_identifier = ""
        if vivaldi_element[0] == "[":
            vivaldi_element_identifier = vivaldi_element.split("]")[0] + "]"
            vivaldi_element_title = vivaldi_element.split("]")[1]
        else:
            vivaldi_element_title = vivaldi_element
        if squish_element[0] == "[":
            squish_element_identifier = squish_element.split("]")[0] + "]"
            squish_element_title = squish_element.split("]")[1]
        else:
            squish_element_title = squish_element
        writer.writerow(
            [vivaldi_element_identifier]
            + [vivaldi_element_title]
            + [""]
            + [squish_element_identifier]
            + [squish_element_title]
        )
    writer.writerow([""])


"""
def test_by_name(list_of_vivaldi_steps: list, list_of_squish_steps: list):
    list_of_squish_steps_missing = []
    list_of_vivaldi_steps_missing = []
    step_counter_squish = 0
    step_vivaldi_counter = 0
    for elem in list_of_vivaldi_steps:
        step_vivaldi_counter += 1
        paragraph_or_no = elem.split(" ")[0]
        if paragraph_or_no != "Paragraph":
            if step_counter_squish < len(list_of_squish_steps):
                if " ".join(elem.split("]")[1:]) != " ".join(
                    list_of_squish_steps[step_counter_squish].split("]")[1:]
                ):
                    list_of_vivaldi_steps_missing.append(
                        "(Step " + str(step_vivaldi_counter) + ") " + elem
                    )
                    list_of_squish_steps_missing.append(
                        "(Step "
                        + str(step_counter_squish + 1)
                        + ") "
                        + list_of_squish_steps[step_counter_squish]
                    )
            else:
                list_of_vivaldi_steps_missing.append(
                    "(Step " + str(step_vivaldi_counter) + ") " + elem
                )
            step_counter_squish += 1
    if step_counter_squish < len(list_of_squish_steps):
        for elem in list_of_squish_steps[step_counter_squish:]:
            list_of_squish_steps_missing.append(
                "(Step " + str(step_counter_squish + 1) + ") " + elem
            )
            step_counter_squish += 1
    return list_of_vivaldi_steps_missing, list_of_squish_steps_missing"""


def test_by_name(
    list_of_vivaldi_steps: list, list_of_squish_steps: list, path_of_results
):
    list_of_vivaldi_missing_steps = []
    list_of_squish_missing_steps = []
    list_of_squish_identifiers = []
    list_of_vivaldi_identifiers = []
    list_of_vivaldi_steps_no_identifier = []
    list_of_squish_steps_no_identifier = []
    # Opening files to write steps
    viv_file = open(path_of_results + "/viv_file", "w")
    sq_file = open(path_of_results + "/sq_file", "w")

    # Writing steps into files
    for elem in list_of_vivaldi_steps:
        if elem[0:9] != "Paragraph":
            vivaldi_id = elem.split("]")[0] + "]"
            list_of_vivaldi_identifiers.append(vivaldi_id)
            step = elem.split("]")[1]
            list_of_vivaldi_steps_no_identifier.append(step)
            viv_file.write(step.strip() + "\n")
    for elem in list_of_squish_steps:
        squish_id = elem.split("]")[0] + "]"
        step = elem.split("]")[1]
        list_of_squish_identifiers.append(squish_id)
        list_of_squish_steps_no_identifier.append(step)
        sq_file.write(step + "\n")

    # Closing files
    viv_file.close()
    sq_file.close()

    # Verifying differences
    os.chdir(path_of_results)

    # Thales version
    """
    git_diff_viv = subprocess.run(
        [
            "poetry",
            "run",
            "git",
            "diff",
            "--no-index",
            "-U1000",
            path_of_results + "/sq_file",
            path_of_results + "/viv_file",
        ],
        stdout=subprocess.PIPE,
    )"""

    #Personal version

    git_diff_viv = subprocess.run(
        [
            "git",
            "diff",
            "--no-index",
            "-U1000",
            path_of_results + "/sq_file",
            path_of_results + "/viv_file",
        ],
        stdout=subprocess.PIPE,
    )

    git_diff_viv_res = git_diff_viv.stdout.decode("utf-8")
    print(git_diff_viv_res)

    # Thales version
    """
    git_diff_sq = subprocess.run(
        [
            "poetry",
            "run",
            "git",
            "diff",
            "--no-index",
            "-U1000",
            path_of_results + "/viv_file",
            path_of_results + "/sq_file",
        ],
        stdout=subprocess.PIPE,
    )"""

    # Personal version
    git_diff_sq = subprocess.run(
        [
            "git",
            "diff",
            "--no-index",
            "-U1000",
            path_of_results + "/viv_file",
            path_of_results + "/sq_file",
        ],
        stdout=subprocess.PIPE,
    )

    git_diff_sq_res = git_diff_sq.stdout.decode("utf-8")
    print(git_diff_sq_res)

    if git_diff_viv_res != "" and git_diff_sq_res != "":
        # Removing the first 5 lines of the result
        result_of_git_diff_viv = git_diff_viv_res.split("\n", 5)[5]
        result_of_git_diff_sq = git_diff_sq_res.split("\n", 5)[5]

        print(result_of_git_diff_viv)

        # Transforming the result into a list
        list_of_vivaldi_missing_steps = result_of_git_diff_viv.splitlines()
        list_of_squish_missing_steps = result_of_git_diff_sq.splitlines()

        # Adding the identifiers
        for i in range(len(list_of_vivaldi_missing_steps)):
            if (
                list_of_vivaldi_missing_steps[i] != ""
                and list_of_vivaldi_missing_steps[i][0] != "-"
            ):
                list_of_vivaldi_missing_steps[i] = (
                    list_of_vivaldi_identifiers[0]
                    + list_of_vivaldi_missing_steps[i][1:]
                )
                del list_of_vivaldi_identifiers[0]
        for j in range(len(list_of_squish_missing_steps)):
            if (
                list_of_squish_missing_steps[j] != ""
                and list_of_squish_missing_steps[j][0] != "-"
            ):
                list_of_squish_missing_steps[j] = (
                    list_of_squish_identifiers[0] + list_of_squish_missing_steps[j][1:]
                )
                del list_of_squish_identifiers[0]

    return list_of_vivaldi_missing_steps, list_of_squish_missing_steps


def get_info_from_conf_comp(conf_file):
    (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_file_check_if_tests_exist,
        path_of_results,
        path_of_ivvq_folder,
    ) = ("", "", "", "", "", "")
    my_file = open(conf_file, "r")
    for line in my_file:
        if "vivaldi_campaign" in line:
            vivaldi_campaign = line.split()[1]
        elif "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]

    suite_bdd = path_of_ivvq_folder + "/tests/suite_bdd"
    test_py = path_of_ivvq_folder + "/src/test.py"
    csv_file_check_if_tests_exist = "/csv_file_check_if_tests_exist.csv"
    path_of_results = path_of_ivvq_folder + "/results"
    return (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_file_check_if_tests_exist,
        path_of_results,
    )


def is_vivaldi_test_exist(list_of_squish_test_names, vivaldi_test_name):
    if vivaldi_test_name not in list_of_squish_test_names:
        is_existing = False
    else:
        is_existing = True
    return is_existing


def verify_names_of_tests(vivaldi_campaign, suite_bdd):
    path_of_vivaldi_tests = vivaldi_campaign + "/TestSuites"
    path_of_squish_tests = suite_bdd
    list_of_existing_vivaldi_tests = []
    list_of_unexistant_vivaldi_tests = []
    list_of_vivaldi_test_names = [
        x for x in os.listdir(path_of_vivaldi_tests) if x[0:3] == "tst"
    ]
    list_of_squish_test_names = [
        x for x in os.listdir(path_of_squish_tests) if x[0:3] == "tst"
    ]

    for vivaldi_test in list_of_vivaldi_test_names:
        if is_vivaldi_test_exist(list_of_squish_test_names, vivaldi_test):
            list_of_existing_vivaldi_tests.append(vivaldi_test)
        else:
            list_of_unexistant_vivaldi_tests.append(vivaldi_test)
    return list_of_existing_vivaldi_tests, list_of_unexistant_vivaldi_tests


def test_unexistant_result(vivaldi_test_name, writer):
    writer.writerow([vivaldi_test_name] + ["Doesn't exist in the suite BDD folder"])
    writer.writerow([""])


def error_file_format(vivaldi_test):
    error_message = ""
    parser = etree.XMLParser(strip_cdata=False)
    ivv_file = [y for y in os.listdir(vivaldi_test) if y[-7:] == "IVV.xml"][0]
    ivv_tree = etree.parse(vivaldi_test + "/" + ivv_file, parser)

    for elem in ivv_tree.iter():
        if elem.text is None:
            elem.text = ""
    format_message = then_given_error_list(ivv_tree)
    if format_message != "":
        error_message = vivaldi_test.split("/")[-1] + "\n" + format_message
    return error_message


def get_vivaldi_steps(vivaldi_test):
    parser = etree.XMLParser(strip_cdata=False)
    ivv_file = [y for y in os.listdir(vivaldi_test) if y[-7:] == "IVV.xml"][0]
    ivv_tree = etree.parse(vivaldi_test + "/" + ivv_file, parser)

    for elem in ivv_tree.iter():
        if elem.text is None:
            elem.text = ""

    list_of_step_names = []
    temp_string = ""

    for case in ivv_tree.xpath("./Cases/Case"):
        case_identifier = case.find("./Identification").text
        paragraph_identifier = ""
        for step in case.xpath("./Steps/Step"):
            if (
                step.find("./Context").text != ""
                and step.find("./Context").text[0] == "P"
            ):
                temp_string += "Paragraph "
                paragraph_identifier = step.find("./Context").text

            step_identifier = step.find("./Identification").text
            if step_identifier is None or step_identifier == "":
                step_identifier = step.find("./Context").text
            step_description = step.find("./StepDescription/StepDescription").text
            expected_result = step.find("./ExpectedResult/ExpectedResult").text
            # Initializing step description depending on its type
            if "(PR)" in step_description:
                step_description = step_description.replace("(PR)", "")
                step_description = "Given " + step_description.strip()
            elif "(PR)" not in step_description and (
                expected_result is None or expected_result == ""
            ):
                step_description = "When " + step_description.strip()
            elif "(PR)" not in step_description and (expected_result is not None):
                step_description = "Then " + step_description.strip()
            problematic_step = (
                "["
                + case_identifier
                + "-"
                + paragraph_identifier
                + "-"
                + step_identifier
                + "]"
                + " ".join(step_description.split())
               # + " "
               # + step.find("./ExpectedResult/ExpectedResult").text
            )
            temp_string += (problematic_step.replace("--", "-")).replace("-]", "]")
            my_string = " ".join(temp_string.split())
            list_of_step_names.append(my_string)
            temp_string = ""
    print(list_of_step_names)
    return list_of_step_names


def get_squish_steps(squish_test):
    list_of_steps = []
    line_number = 0
    # opening a BDD file
    test_case_bdd_files = open(squish_test + "/test.feature", "r")
    # recovering all lines of the file
    lines_of_bdd_files = test_case_bdd_files.readlines()
    # going through each line and testing which type of step
    for line in lines_of_bdd_files:
        line_number += 1
        my_string = " ".join(line.split())
        if "#" not in my_string and (
            "Given" in my_string or "When" in my_string or "Then" in my_string
        ):
            line_number_str = "[Line : " + str(line_number) + "]"
            list_of_steps.append(line_number_str + my_string)
    return list_of_steps


def verifying_steps(
    vivaldi_test_steps, squish_test_steps, existent_test, writer, path_of_results
):
    vivaldi_remaining_steps, squish_remaining_steps = test_by_name(
        vivaldi_test_steps, squish_test_steps, path_of_results
    )
    is_no_remaining_steps = True
    if squish_remaining_steps or vivaldi_remaining_steps:
        writer.writerow([existent_test] + ["Exists but steps aren't the same"])
        writer.writerow([""])
        display_list_csv(writer, vivaldi_remaining_steps, squish_remaining_steps)
        is_no_remaining_steps = False
    return is_no_remaining_steps


def filling_csv_file(
    list_of_existing_vivaldi_tests,
    list_of_unexistant_vivaldi_tests,
    writer,
    path_of_vivaldi_tests,
    suite_bdd,
    path_of_results,
):
    is_all_steps_are_matched = True
    for unexistant_test in list_of_unexistant_vivaldi_tests:
        test_unexistant_result(unexistant_test, writer)
        is_all_steps_are_matched = False
    for existent_test in list_of_existing_vivaldi_tests:
        vivaldi_test_path = path_of_vivaldi_tests + existent_test
        squish_test_path = suite_bdd + "/" + existent_test
        error_message = error_file_format(vivaldi_test_path)
        if error_message != "":
            split_displayed_msg(error_message, writer)
            is_all_steps_are_matched = False
        else:
            vivaldi_test_steps = get_vivaldi_steps(vivaldi_test_path)
            squish_test_steps = get_squish_steps(squish_test_path)
            is_all_steps_are_matched *= verifying_steps(
                vivaldi_test_steps,
                squish_test_steps,
                existent_test,
                writer,
                path_of_results,
            )
    return is_all_steps_are_matched


def main():
    # initialization
    (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_file_check_if_tests_exist,
        path_of_results,
    ) = get_info_from_conf_comp(sys.argv[1])

    time_now = datetime.now()
    campaign_name = vivaldi_campaign.split("/")[-1]
    path_of_time_folder = (
        path_of_results + "/" + str(time_now)[:19] + "_" + campaign_name
    )
    os.makedirs(path_of_time_folder)

    path_of_vivaldi_tests = vivaldi_campaign + "/TestSuites/"
    with open(
        path_of_time_folder + csv_file_check_if_tests_exist, "w", newline=""
    ) as csv_file:
        writer = csv.writer(
            csv_file, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL
        )
        (
            list_of_existing_vivaldi_tests,
            list_of_unexistant_vivaldi_tests,
        ) = verify_names_of_tests(vivaldi_campaign, suite_bdd)
        is_all_steps_matched = filling_csv_file(
            list_of_existing_vivaldi_tests,
            list_of_unexistant_vivaldi_tests,
            writer,
            path_of_vivaldi_tests,
            suite_bdd,
            path_of_results,
        )
        if is_all_steps_matched:
            print("All tests exist and their steps are matched")
        else:
            print("One or many tests aren't good. Check CSV file")


if __name__ == "__main__":
    main()

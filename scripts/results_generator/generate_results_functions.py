# Libraries used
import os
import csv
import subprocess
from lxml import etree, objectify
import lxml
from datetime import date
from datetime import datetime
import re


# Removes the xmlns tag temporarily while parsing
def remove_xmlns(root: etree._Element) -> None:
    for elem in root.getiterator():
        if not hasattr(elem.tag, "find"):
            continue  # guard for Comment tags # pragma: no cover
        i = elem.tag.find("}")
        if i >= 0:
            elem.tag = elem.tag[i + 1 :]
    objectify.deannotate(root, cleanup_namespaces=True)


# Transform a string to a date format
def string_to_date(string_date: str) -> datetime.date:
    date_format = date(
        int(string_date[0:4]), int(string_date[5:7]), int(string_date[8:10])
    )
    return date_format


# Gives the number of days between dates
def days_between_dates(first_date, second_date):
    difference_between_dates = second_date - first_date
    return difference_between_dates.days


# Transform a date to days
def date_to_days(my_date: datetime.date) -> int:
    initial_date = date(1899, 12, 30)
    return days_between_dates(initial_date, my_date)


# Transform a string directly to a number of days
def string_date_to_days(date_str: str) -> str:
    date_format = string_to_date(date_str)
    days_format = date_to_days(date_format)
    return str(days_format)


# Parser specified, so it won't modify CDATA format into normal text format
parser = etree.XMLParser(strip_cdata=False)


# Initializes Vivaldi files
def init_vivaldi_trees(
    list_of_vivaldi_files: list,
    list_of_vivaldi_trees: list,
    k: int,
) -> None:
    for this_file in list_of_vivaldi_files:
        list_of_vivaldi_trees.append(etree.parse(this_file, parser))
        k = k + 1
    for this_tree in list_of_vivaldi_trees:
        for elem in this_tree.iter():
            if elem.text is None:
                elem.text = ""


# Transforms a string into time
def string_to_time(time_str: str):
    test_str = time_str
    regex = (
        r"([0-9]{4})-([0-9]{2})-([0-9]{2})([a-aA-Z]{1})([0-9]{2}):([0-9]{2}):([0-9]{2})"
    )
    matches = re.finditer(regex, test_str, re.MULTILINE)
    my_list = []
    for matchNum, match in enumerate(matches, start=1):
        my_list.append(":".join((match.group(5), match.group(6), match.group(7))))
    return datetime.strptime(my_list[0], "%H:%M:%S")


# Returning the duration of execution
def squish_execution_duration(timeBeforeExecution: str, timeAfterExecution: str) -> str:
    days = int(string_date_to_days(timeAfterExecution)) - int(
        string_date_to_days(timeBeforeExecution)
    )

    time_after = string_to_time(timeAfterExecution)
    time_before = string_to_time(timeBeforeExecution)
    duration_time = time_after - time_before
    execution_duration = str(days) + "Days " + str(duration_time)
    return execution_duration


# Filling the conf elements
def conf_setup_in_vivaldi(
    version_under, soft_env, hard_env, tree_in_vivaldi: lxml.etree._Element
) -> None:
    tree_in_vivaldi.find(
        "./Summary/VersionUnderTest/VersionUnderTest"
    ).text = etree.CDATA(version_under)

    tree_in_vivaldi.find("./Summary/SoftwareEnvironment").text = etree.CDATA(soft_env)
    tree_in_vivaldi.find("./Summary/HardwareEnvironment").text = etree.CDATA(hard_env)


# Returning all the prolog information
def prolog_information(
    squish_step: lxml.etree._Element,
) -> (lxml.etree._Element, lxml.etree._Element, str, str):
    (
        prolog_of_squish_step,
        prolog_name_of_squish_step,
        message_error_of_squish_step,
        prolog_name_text_of_squish_step,
    ) = (None, None, None, None)

    if squish_step.find("prolog") is not None:
        prolog_of_squish_step = squish_step.find("prolog")
        prolog_name_of_squish_step = squish_step.find("prolog/name")
        prolog_name_text_of_squish_step = prolog_name_of_squish_step.text
    else:
        prolog_name_text_of_squish_step = squish_step.find("./name").text
    message_error_of_squish_step = squish_step.find("message")
    return (
        prolog_of_squish_step,
        prolog_name_of_squish_step,
        message_error_of_squish_step,
        prolog_name_text_of_squish_step,
    )


# Treating a then step
def then_step_treatment(
    message_error_of_squish_step: lxml.etree._Element,
    list_of_results: list,
    squish_step: lxml.etree._Element,
) -> str:
    if message_error_of_squish_step is not None:
        message_error_text_of_squish_step = (
            message_error_of_squish_step.find("text")
        ).text
        result_of_squish_step = "FAIL Error " + message_error_text_of_squish_step
        list_of_results.append(result_of_squish_step)
    else:
        scripted_verification_result = squish_step.find(
            "verification/scriptedVerificationResult"
        )
        type_of_scripted_verification_result = scripted_verification_result.get("type")
        text_of_scripted_verification_result = scripted_verification_result.find(
            "detail"
        ).text
        result_of_squish_step = (
            str(type_of_scripted_verification_result)
            + " "
            + text_of_scripted_verification_result
        )
        list_of_results.append(result_of_squish_step)
    return result_of_squish_step


# Treating a when step
def when_step_treatment(
    message_error_of_squish_step: lxml.etree._Element, list_of_results: list
) -> str:
    if message_error_of_squish_step is not None:
        message_error_text_of_squish_step = message_error_of_squish_step.find(
            "text"
        ).text
        result_of_squish_step = "NOTE Error " + message_error_text_of_squish_step
        list_of_results.append(result_of_squish_step)
    else:
        result_of_squish_step = "NOTE Step passed"
        list_of_results.append(result_of_squish_step)
    return result_of_squish_step


# Treating a given step
def given_step_treatment(
    message_error_of_squish_step: lxml.etree._Element,
    list_of_results: list,
    list_of_dates: list,
    prolog_of_squish_step: lxml.etree._Element,
    squish_step: lxml.etree._Element,
) -> str:
    list_of_dates.append(prolog_of_squish_step.get("time"))
    if message_error_of_squish_step is not None:
        message_error_text_of_squish_step = message_error_of_squish_step.find(
            "text"
        ).text
        result_of_squish_step = "NOTE Error " + message_error_text_of_squish_step
        list_of_results.append(result_of_squish_step)
    else:
        scripted_verification_result = squish_step.find(
            "verification/scriptedVerificationResult"
        )
        text_of_scripted_verification_result = scripted_verification_result.find(
            "detail"
        ).text
        result_of_squish_step = "NOTE" + " " + text_of_scripted_verification_result
        list_of_results.append(result_of_squish_step)
    return result_of_squish_step


# Treating a skipped step
def skipped_step_treatment(
    list_of_dates: list, squish_step: lxml.etree._Element, list_of_results: list
) -> str:
    list_of_dates.append(squish_step.get("time"))
    result_of_squish_step = "NOTE Step skipped"
    list_of_results.append(result_of_squish_step)
    return result_of_squish_step


# Setting up the runner,run date and run duration in the summary section
def setup_runner_run_date_duration(
    list_of_vivaldi_trees: list, tgi: str, run_date: str, run_duration: str, k: int
) -> None:
    (list_of_vivaldi_trees[k].find("./Summary/Runner/Last/Name")).text = etree.CDATA(
        tgi
    )
    (list_of_vivaldi_trees[k].find("./Summary/RunDate/LastRunDate")).text = etree.CDATA(
        run_date
    )
    (list_of_vivaldi_trees[k].find("./Summary/LastRunDuration")).text = etree.CDATA(
        run_duration
    )


# Filling a vivaldi step depending on if it's a when, then or given & skip if paragraph
def filling_vivaldi_step(
    step: lxml.etree._Element,
    list_of_dates: list,
    tgi: str,
    list_of_results: list,
    i: int,
    j: int,
) -> (int, int):
    context_of_vivaldi_step = step.find("./Context").text
    if (context_of_vivaldi_step == "X") or (
        context_of_vivaldi_step == ""
    ):  # skip if a paragraph else it's good
        step_hours = step.find("./FreeColumn1/FreeColumn1")
        # hours added
        list_of_dates_element = str(list_of_dates[i])
        step_hours.text = etree.CDATA(list_of_dates_element[11:])
        step.find("./LastRunner").text = etree.CDATA(tgi)
        step.find("./LastRunDate").text = etree.CDATA(
            string_date_to_days(list_of_dates[i])
        )
        step_result = list_of_results[j]
        last_run_result = step.find("./LastRunResult")
        nature_of_test = step_result[0:4]
        if nature_of_test == "PASS":
            last_run_result.text = etree.CDATA("OK")
        elif nature_of_test == "NOTE":
            last_run_result.text = ""
        else:
            last_run_result.text = etree.CDATA("KO")
        step.find("./CommentOnResult/CommentOnResult").text = etree.CDATA(
            step_result[5:]
        )
        j = j + 1
        i = i + 1
    return i, j


# Returning the names of vivaldi steps
def vivaldi_step_names(list_of_vivaldi_trees: list) -> list:
    list_of_step_names = []
    list_of_steps_by_folder = []
    temp_string = ""
    for vivaldi_tree in list_of_vivaldi_trees:
        for case in vivaldi_tree.xpath("./Cases/Case"):
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
                # Initializing step description depending on its type
                step_description = step.find("./StepDescription/StepDescription").text
                expected_result = step.find("./ExpectedResult/ExpectedResult").text
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
                #    + " "
                #    + step.find("./ExpectedResult/ExpectedResult").text
                )
                temp_string += (problematic_step.replace("--", "-")).replace("-]", "]")
                my_string = " ".join(temp_string.split())
                list_of_step_names.append(my_string)
                temp_string = ""
        list_of_steps_by_folder.append(list_of_step_names)
        list_of_step_names = []
    return list_of_steps_by_folder


# Returns also list of tuples, list of test cases (names), list of steps (names)
def squish_step_names_by_folder(list_of_squish_path: list) -> list:
    list_of_steps = []
    list_of_tests = []
    line = ""
    line_number = 0
    # Recovering the list of test cases in Squish
    for test_case in list_of_squish_path:
        # opening a BDD file
        test_case_bdd_files = open(test_case + "/test.feature", "r")
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
        list_of_tests.append(list_of_steps)
        list_of_steps = []
        if not line:
            break  # pragma: no cover
    return list_of_tests


"""
# Return names of vivaldi files that ends with IVV.xml
def vivaldi_files_and_test_suite_names(vivaldi_folder: str) -> (list, list):
    # Initialization of lists
    list_of_vivaldi_files = []
    list_of_test_suite_names = []
    # Test suite path
    path_of_test_suites = vivaldi_folder + "/TestSuites"
    # Stocking all Test suite folders in a list
    list_of_vivaldi_test_suite_folders = [
        x for x in os.listdir(path_of_test_suites) if x[0:3] == "tst"
    ]
    # for each Test suite folder stock its name and the IVV.xml file
    for vivaldi_test_suite_folder in list_of_vivaldi_test_suite_folders:
        list_of_test_suite_names.append(vivaldi_test_suite_folder)
        vivaldi_xml_files = [
            y
            for y in os.listdir(path_of_test_suites + "/" + vivaldi_test_suite_folder)
            if y[-7:] == "IVV.xml"
        ]
        for vivaldi_xml_file in vivaldi_xml_files:
            list_of_vivaldi_files.append(
                vivaldi_folder
                + "/TestSuites"
                + "/"
                + vivaldi_test_suite_folder
                + "/"
                + vivaldi_xml_file
            )
    return list_of_test_suite_names, list_of_vivaldi_files
"""


def vivaldi_files_and_test_suite_names_version_2(
    vivaldi_folder: str, test_cases_vivaldi
) -> (list, list):
    # Initialization of lists
    list_of_vivaldi_files = []
    # Test suite path
    path_of_test_suites = vivaldi_folder + "/TestSuites"
    # Stocking all Test suite folders in a list

    # for each Test suite folder stock its name and the IVV.xml file
    for vivaldi_test_suite_folder in test_cases_vivaldi:
        vivaldi_xml_files = [
            y
            for y in os.listdir(path_of_test_suites + "/" + vivaldi_test_suite_folder)
            if y[-7:] == "IVV.xml"
        ]
        for vivaldi_xml_file in vivaldi_xml_files:
            list_of_vivaldi_files.append(
                vivaldi_folder
                + "/TestSuites"
                + "/"
                + vivaldi_test_suite_folder
                + "/"
                + vivaldi_xml_file
            )
    return test_cases_vivaldi, list_of_vivaldi_files


"""
# If the name exist in both lists we delete it from both of them
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
    return list_of_vivaldi_steps_missing, list_of_squish_steps_missing
"""


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
    for elem in list_of_vivaldi_steps:
        if "(PR)" in elem:
            elem = elem.replace("(PR)", "")
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

    # Personal version
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

    if git_diff_viv_res != "" and git_diff_sq_res != "":
        # Removing the first 5 lines of the result
        result_of_git_diff_viv = git_diff_viv_res.split("\n", 5)[5]
        result_of_git_diff_sq = git_diff_sq_res.split("\n", 5)[5]

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
    writer.writerow([""])
"""


def display_list_csv(writer, vivaldi_remaining_steps, squish_remaining_steps):
    vivaldi_len_list = len(vivaldi_remaining_steps)
    squish_len_list = len(squish_remaining_steps)
    list_length = max(vivaldi_len_list, squish_len_list)
    vivaldi_remaining_steps, squish_remaining_steps = equalize_lists(
        vivaldi_remaining_steps, squish_remaining_steps
    )
    writer.writerow(["Vivaldi"] + [""] + [""] + ["Squish"] + [""])
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


def verifying_names_by_folder(
    list_of_vivaldi_tests, list_of_squish_tests, test_names, writer, path_of_results
):
    length = len(list_of_squish_tests)
    do_steps_match = True
    for i in range(length):
        vivaldi_remaining_steps, squish_remaining_steps = test_by_name(
            list_of_vivaldi_tests[i], list_of_squish_tests[i], path_of_results
        )
        vivaldi_remaining_steps, squish_remaining_steps = equalize_lists(
            vivaldi_remaining_steps, squish_remaining_steps
        )
        if vivaldi_remaining_steps or squish_remaining_steps:
            # writer.writerow([test_names[i]] + ["Steps not matched in Vivaldi"])
            writer.writerow([test_names[i]])
            writer.writerow([""])
            writer.writerow(["Steps with no match"])
            writer.writerow([""])
            display_list_csv(writer, vivaldi_remaining_steps, squish_remaining_steps)
            do_steps_match = False
            writer.writerow([""])
    return do_steps_match


def do_all_tests_exist_in_squish(squish_folder, test_cases_vivaldi, writer):
    list_of_test_squish_path = []
    list_of_unexistant_tests = []
    do_all_tests_exists_in_squish = True

    test_cases_squish = list_of_test_cases_of_squish(squish_folder)
    for testcase in test_cases_vivaldi:
        if testcase not in test_cases_squish:
            list_of_unexistant_tests.append(testcase)
            do_all_tests_exists_in_squish = False
        else:
            list_of_test_squish_path.append(squish_folder + "/" + testcase)
    if list_of_unexistant_tests:
        writer.writerow(["These tests exist in Vivaldi but not in Squish"])
        writer.writerow([""])
        for element in list_of_unexistant_tests:
            writer.writerow([element])
    writer.writerow([""])
    return do_all_tests_exists_in_squish, list_of_test_squish_path


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


def split_displayed_msg(displayed_message: str, writer: csv.writer) -> None:
    list_by_line = displayed_message.split("\n")
    for my_line in list_by_line:
        writer.writerow([my_line])
    writer.writerow("")


# This function does all the verification and affords
# a csv file if something is wrong before the execution
def recovering_information_before_execution(
    list_of_vivaldi_files: list,
    list_of_vivaldi_trees: list,
    squish_folder: str,
    vivaldi_folder_list: list,
    writer,
    test_cases_vivaldi,
    path_of_results,
) -> bool:

    # bad tests will be used in the ihm when we update status
    # we will update to error only tests that are in this list
    bad_tests = []
    k = 0
    general_condition_state = True
    (
        do_all_tests_exists_in_squish,
        list_of_test_squish_path,
    ) = do_all_tests_exist_in_squish(squish_folder, test_cases_vivaldi, writer)

    if do_all_tests_exists_in_squish:
        init_vivaldi_trees(list_of_vivaldi_files, list_of_vivaldi_trees, k)
        test_name_counter = 0
        for i_ivv_tree in list_of_vivaldi_trees:
            displayed_message = then_given_error_list(i_ivv_tree)
            if displayed_message:
                displayed_message = (
                    vivaldi_folder_list[test_name_counter] + "\n" + displayed_message
                )

                general_condition_state = False

                split_displayed_msg(displayed_message, writer)
            test_name_counter += 1
        if general_condition_state:
            list_of_squish_step_names = squish_step_names_by_folder(
                list_of_test_squish_path
            )

            list_of_vivaldi_step_names = vivaldi_step_names(list_of_vivaldi_trees)

            # list of folders with no matching
            general_condition_state = verifying_names_by_folder(
                list_of_vivaldi_step_names,
                list_of_squish_step_names,
                vivaldi_folder_list,
                writer,
                path_of_results,
            )

    else:
        general_condition_state = False

    return general_condition_state


# Returns the summary information from squish
def recovering_summary_information_from_squish(
    squish_tree: lxml.etree._Element, squish_root: lxml.etree._Element
) -> (str, str, str, str, str):
    tgi = squish_root.get("executedBy")
    time_before_execution = (squish_tree.find("/test/prolog")).get("time")
    time_after_execution = (squish_tree.find("/test/epilog")).get("time")

    vivaldi_run_duration = squish_execution_duration(
        time_before_execution, time_after_execution
    )
    vivaldi_run_date = string_date_to_days(time_before_execution)
    return (
        tgi,
        time_before_execution,
        time_after_execution,
        vivaldi_run_duration,
        vivaldi_run_date,
    )


def list_of_test_cases(path_vivaldi_campaign):
    test_cases = ""
    path_of_tests = path_vivaldi_campaign + "/TestSuites"
    list_of_vivaldi_test_folder_names = [
        x for x in os.listdir(path_of_tests) if x[0:3] == "tst"
    ]
    for test_case in list_of_vivaldi_test_folder_names:
        test_cases += " --testcase " + test_case
    return test_cases, list_of_vivaldi_test_folder_names


def list_of_test_cases_of_squish(path_suite_bdd):
    list_of_squish_test_folder_names = [
        x for x in os.listdir(path_suite_bdd) if x[0:3] == "tst"
    ]
    return list_of_squish_test_folder_names


def import_from_config(conf_file: str):  # pragma: no cover
    (
        vivaldi_campaign,
        suite_bdd,
        squish_runner_path,
        xml_version,
        results_xml,
        path_of_ivvq_folder,
    ) = ("", "", "", "", "", "")
    my_file = open(conf_file, "r")
    for line in my_file:
        if "vivaldi_campaign" in line:
            vivaldi_campaign = line.split()[1]
        elif "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]
    my_file.close()
    suite_bdd = path_of_ivvq_folder + "/tests/suite_bdd"
    squish_runner_path = (
        "~/squish-for-qt-7.0.0/bin/squishrunner --host 172.17.0.1 --testsuite "
    )
    xml_version = " --reportgen xml3.5,"
    path_of_results = path_of_ivvq_folder + "/results"
    results_xml = "/tmp/results"
    csv_file_before_execution = "/beforeExecution.csv"
    return (
        vivaldi_campaign,
        suite_bdd,
        squish_runner_path,
        xml_version,
        results_xml,
        path_of_results,
        csv_file_before_execution,
        path_of_ivvq_folder,
    )


def get_csv_before_exec(conf_file):  # pragma: no cover
    csv_file_before_execution = ""
    my_file = open(conf_file, "r")
    for line in my_file:
        if "csv_file_before_execution" in line:
            csv_file_before_execution = line.split()[1]
    return csv_file_before_execution


def get_csv_after_exec(conf_file):  # pragma: no cover
    csv_file_after_execution = ""
    my_file = open(conf_file, "r")
    for line in my_file:
        if "csv_file_after_execution" in line:
            csv_file_after_execution = line.split()[1]
    return csv_file_after_execution


def get_path_of_results(conf_file):  # pragma: no cover
    path_of_results = ""
    my_file = open(conf_file, "r")
    for line in my_file:
        if "path_of_results" in line:
            path_of_results = line.split()[1]
    return path_of_results


def get_path_of_ivvq(conf_file):
    path_of_ivvq = ""
    my_file = open(conf_file, "r")
    for line in my_file:
        if "path_of_ivvq_folder" in line:
            path_of_ivvq = line.split()[1]
    return path_of_ivvq


def verify_git(path_of_ivvq):
    is_ready_to_commit = True
    os.chdir(path_of_ivvq)
    git_status = subprocess.run(
        ["poetry", "run", "git", "status", "-s", path_of_ivvq], stdout=subprocess.PIPE
    )
    git_status_result = git_status.stdout.decode("utf-8")
    if git_status_result == "":
        print("Files are committed")
    else:
        is_ready_to_commit = False
        print("Files not committed yet :\n", git_status_result)
    return is_ready_to_commit


def verification_before_execution(
    squish_folder: str, vivaldi_folder: str, writer, test_cases_vivaldi, path_of_results
) -> (list, bool):
    # Booleans deciding either the execution will start or no + initialization of lists
    ready_to_execute = False
    list_of_vivaldi_trees = []

    # returning the names and the paths of vivaldi tests

    """vivaldi_folder_list, list_of_vivaldi_files = vivaldi_files_and_test_suite_names(
        vivaldi_folder
    )"""
    (
        vivaldi_folder_list,
        list_of_vivaldi_files,
    ) = vivaldi_files_and_test_suite_names_version_2(vivaldi_folder, test_cases_vivaldi)

    # returning true or false depending on the conditions
    condition_state = recovering_information_before_execution(
        list_of_vivaldi_files,
        list_of_vivaldi_trees,
        squish_folder,
        vivaldi_folder_list,
        writer,
        test_cases_vivaldi,
        path_of_results,
    )
    if condition_state:
        ready_to_execute = True
    return list_of_vivaldi_files, ready_to_execute


def verification_before_execution_by_test(
    squish_folder: str, vivaldi_folder: str, writer, vivaldi_test, path_of_results
) -> (list, bool):
    # Booleans deciding either the execution will start or no + initialization of lists
    ready_to_execute = False
    list_of_vivaldi_trees = []

    # returning the names and the paths of vivaldi tests

    """vivaldi_folder_list, list_of_vivaldi_files = vivaldi_files_and_test_suite_names(
        vivaldi_folder
    )"""
    (
        vivaldi_folder_list,
        list_of_vivaldi_files,
    ) = vivaldi_files_and_test_suite_names_version_2(vivaldi_folder, [vivaldi_test])

    # returning true or false depending on the conditions
    condition_state = recovering_information_before_execution(
        list_of_vivaldi_files,
        list_of_vivaldi_trees,
        squish_folder,
        vivaldi_folder_list,
        writer,
        [vivaldi_test],
        path_of_results,
    )
    if condition_state:
        ready_to_execute = True
    #return ready_to_execute
    return list_of_vivaldi_files, ready_to_execute


# Recovering all the necessary data from Squish
def recovering_data_from_squish(
    squish_tree: etree._Element,
    list_of_dates: list,
    list_of_results: list,
    writer: csv.writer,
) -> bool:
    # initializing step number and case number
    result_of_squish_step = ""
    step_number = 1
    test_case_number = 1
    is_bad_recorded = False
    # Going through all steps
    for squish_case in squish_tree.xpath(".//*[@type = 'testcase']"):
        # recovering the name of the test case
        name_of_test_case = squish_case.find("./prolog/name").text
        writer.writerow(["Test Case : " + name_of_test_case])
        writer.writerow([""])
        test_case_number += 1
        bad_recorded_test_message = squish_case.find("./message")
        if bad_recorded_test_message is not None:
            writer.writerow([bad_recorded_test_message.find("detail").text])
            is_bad_recorded = True
        else:
            for squish_step in squish_case.xpath(".//*[@type='step']"):
                # recovering all the prolog information
                (
                    prolog_of_squish_step,
                    prolog_name_of_squish_step,
                    message_error_of_squish_step,
                    prolog_name_text_of_squish_step,
                ) = prolog_information(squish_step)
                # Then or When step
                if (
                    prolog_of_squish_step is not None
                    and prolog_name_of_squish_step.text[0:5] != "Given"
                ):
                    list_of_dates.append(prolog_of_squish_step.get("time"))
                    if prolog_name_text_of_squish_step[0:4] == "Then":
                        result_of_squish_step = then_step_treatment(
                            message_error_of_squish_step, list_of_results, squish_step
                        )
                    elif prolog_name_text_of_squish_step[0:4] == "When":
                        result_of_squish_step = when_step_treatment(
                            message_error_of_squish_step, list_of_results
                        )
                # Given step
                elif (
                    prolog_of_squish_step is not None
                    and prolog_name_of_squish_step.text[0:5] == "Given"
                ):
                    result_of_squish_step = given_step_treatment(
                        message_error_of_squish_step,
                        list_of_results,
                        list_of_dates,
                        prolog_of_squish_step,
                        squish_step,
                    )
                # Skipped step
                elif squish_step.get("time") is not None:
                    result_of_squish_step = skipped_step_treatment(
                        list_of_dates, squish_step, list_of_results
                    )
                # Writing the summary of the actual step

                writer.writerow(
                    ["Step " + str(step_number)]
                    + [prolog_name_text_of_squish_step]
                    + [result_of_squish_step]
                )
                step_number += 1
            writer.writerow([""])
            step_number = 1
    return is_bad_recorded


# Filling Vivaldi Files with the Data recovered from Squish
def filling_vivaldi_files(
    version_under,
    soft_env,
    hard_env,
    path_of_folder_time: str,
    list_of_vivaldi_files: list,
    list_of_dates: list,
    list_of_results: list,
    tgi: str,
    run_date: str,
    run_duration: str,
    list_of_vivaldi_trees: list,
    i: int,
    j: int,
    k: int,
) -> None:

    for arg in list_of_vivaldi_files:
        # Setting up runner, run date, run duration and conf
        setup_runner_run_date_duration(
            list_of_vivaldi_trees, tgi, run_date, run_duration, k
        )
        conf_setup_in_vivaldi(
            version_under, soft_env, hard_env, list_of_vivaldi_trees[k]
        )
        # Going through each case
        for case in list_of_vivaldi_trees[k].xpath("./Cases/Case"):
            # Setting up the runner of each case
            (case.find("./LastRunner")).text = etree.CDATA(tgi)
            for step in case.xpath("./Steps/Step"):
                # filling each vivaldi step
                i, j = filling_vivaldi_step(
                    step, list_of_dates, tgi, list_of_results, i, j
                )
        # Writing the new vivaldi files in a folder called "new"
        list_of_vivaldi_trees[k].write(
            path_of_folder_time + "/" + arg.split("/")[-1],
            encoding="utf-8",
            standalone="yes",
        )
        k = k + 1


# This function calls the functions mentioned
# above in order to execute the importing process
def importing_data_from_squish_to_vivaldi(
    squish: str,
    list_of_vivaldi_files: list,
    path_of_folder_time: str,
    version_under,
    soft_env,
    hard_env,
) -> bool:
    # Initialization
    i = 0
    j = 0
    k = 0
    list_of_vivaldi_trees = []
    list_of_dates = []
    list_of_results = []
    squish_tree = etree.parse(squish, parser)
    squish_root = squish_tree.getroot()
    init_vivaldi_trees(list_of_vivaldi_files, list_of_vivaldi_trees, k)
    csv_file_after_execution = "/afterExecution.csv"

    # Removing the XMLNS tag
    remove_xmlns(squish_root)

    # recover de TGI, timeBeforeExecution, timeAfterExecution,
    # vivaldiRunDuration, vivaldiRunDate
    (
        TGI,
        timeBeforeExecution,
        timeAfterExecution,
        vivaldiRunDuration,
        vivaldiRunDate,
    ) = recovering_summary_information_from_squish(squish_tree, squish_root)
    # starting the import process
    with open(
        path_of_folder_time + csv_file_after_execution,
        "w",
        newline="",
    ) as csv_file:
        writer = csv.writer(
            csv_file, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL
        )

        # Parsing XML file and recovering data
        print("\nRecovering Data...\n")
        is_bad_recorded = recovering_data_from_squish(
            squish_tree, list_of_dates, list_of_results, writer
        )
        print("\nData Recovered\n")
        # Filling Vivaldi files
        if not is_bad_recorded:
            print("\nFilling files...\n")
            filling_vivaldi_files(
                version_under,
                soft_env,
                hard_env,
                path_of_folder_time,
                list_of_vivaldi_files,
                list_of_dates,
                list_of_results,
                TGI,
                vivaldiRunDate,
                vivaldiRunDuration,
                list_of_vivaldi_trees,
                i,
                j,
                k,
            )
            print("\nVivaldi files are filled !\n")

    return is_bad_recorded

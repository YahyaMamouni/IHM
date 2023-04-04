import os
import subprocess

from lxml import etree
import csv
import sys
import shutil
from tkinter import *
import re
from tkinter import messagebox

# Parser specified, so it won't modify CDATA format into normal text format
parser = etree.XMLParser(strip_cdata=False)
backup_tests_path = "/home/t0042377/Bureau/Yahya/GenerationBDDFiles/backup_tests"


def atoi(text):
    return int(text) if text.isdigit() else text

# Checking if a char exists in a list of str
def search_char_in_string(list_of_char, my_string):
    is_existing = False
    for elem in list_of_char:
        if elem in my_string:
            is_existing = True
    return is_existing

def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]

# Turn list of lists into a list
def flatten(l):
    return [item for sublist in l for item in sublist]

# Returns expected result formatted
def split_expected_result(expected_result : str) -> str:
    if expected_result != "":
        three_tabs = "\t\t\t"
        split_list = expected_result.split("-")
        expected_result_splitted = "\n" + three_tabs + "\"\"\"\n"
        for elem in split_list:
            expected_result_splitted +=three_tabs + "- " + elem.strip() + "\n"
        expected_result_splitted += three_tabs + "\"\"\""
        return expected_result_splitted
    else:
        return ""

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


# Writing the BDD files
def writing_file(
    squish_folder_path: str, title_of_file: str, objectives: str, list_of_steps: list
) -> None:
    my_file = open(squish_folder_path + "/test.feature", "w")
    my_file.write("Feature: " + title_of_file + "\n\n")
    my_file.write("\t" + objectives.replace("\n", "\n\t") + "\n\n")
    my_file.write("\tScenario: " + title_of_file + "\n\n")
    for line in list_of_steps:
        my_file.write("\t\t" + line + "\n")
    my_file.close()


# Recovering a list of step names by folder
def vivaldi_step_names(list_of_vivaldi_trees: list) -> (list,list):
    is_bad_description = False
    list_of_step_case_parag = []
    list_by_folder = []
    # List of steps with bad description
    list_of_steps_bad_description = []
    temp_list_bad_description = []
    # Bad elements
    list_of_bad_elements = ["\"", "[", "]"]
    for vivaldi_tree in list_of_vivaldi_trees:
        for case in vivaldi_tree.xpath("./Cases/Case"):
            # recovering case title
            case_title = case.find("./Title").text
            list_of_step_case_parag.append("#" + case_title)
            # if it's a given case
            for step in case.xpath("./Steps/Step"):
                step_description = step.find("./StepDescription/StepDescription").text
                # Returning boolean to check if the step description is bad or no
                is_bad_description = search_char_in_string(list_of_bad_elements, step_description)
                if is_bad_description:
                    temp_list_bad_description.append(step_description)
                if "(PR)" in step_description:
                    # Foramatting the expected result
                    temp_string = (
                        step_description.replace("(PR)", "")
                        + " "
                        + split_expected_result(step.find("./ExpectedResult/ExpectedResult").text)
                    )
                    my_string = " ".join(temp_string.split())
                    list_of_step_case_parag.append("Given " + my_string)
                # if it's a normal case
                else:
                    context_of_vivaldi_step = step.find("./Context").text
                    temp_string = step.find("./StepDescription/StepDescription").text
                    my_string = " ".join(temp_string.split())
                    if context_of_vivaldi_step == "X":  # ignore paragraphs
                        list_of_step_case_parag.append("When " + my_string)
                    elif context_of_vivaldi_step == "":
                        # Formatting the expected result
                        list_of_step_case_parag.append(
                            "Then "
                            + my_string
                            + " "
                            + split_expected_result(step.find("./ExpectedResult/ExpectedResult").text)
                        )
                    elif context_of_vivaldi_step[0] == "P":
                        list_of_step_case_parag.append("## " + my_string)
            list_of_step_case_parag.append("\n")

        list_of_steps_bad_description.append(temp_list_bad_description)
        list_by_folder.append(list_of_step_case_parag)
        list_of_step_case_parag = []
        temp_list_bad_description = []
    return list_by_folder, list_of_steps_bad_description


# Recovering the title of the test
def recovering_title(doors_file: etree._Element) -> str:
    return doors_file.find("./Title").text


def recovering_objectives(doors_file: etree._Element) -> str:
    return doors_file.find("./Objective").text


# Returns a list of ivv XML files
def ivv_files(path_of_tests: str, vivaldi_folder: str) -> list:
    ivv_xml_files = [
        y
        for y in os.listdir(path_of_tests + "/" + vivaldi_folder)
        if y[-7:] == "IVV.xml"
    ]
    return ivv_xml_files


# Returns a list of doors XML files
def doors_files(path_of_tests: str, vivaldi_folder: str) -> list:
    doors_xml_files = [
        y
        for y in os.listdir(path_of_tests + "/" + vivaldi_folder)
        if y[-9:] == "DOORS.xml"
    ]
    return doors_xml_files


# Assigning the full path of Vivaldi XML files (doors and ivv)
def file_full_path(
    list_of_files: list, path_of_tests: str, vivaldi_folder: str
) -> list:
    stock_list = []
    for xml_file in list_of_files:
        stock_list.append(path_of_tests + "/" + vivaldi_folder + "/" + xml_file)
    return stock_list


# Returns a list of folder names, doors tree, step names, ivv tree
def get_ivv_doors_data(path_of_tests: str) -> (list, list, list, list):
    # Initialization

    list_of_vivaldi_ivv_files = []
    list_of_vivaldi_doors_files = []
    list_of_vivaldi_trees_ivv = []
    list_of_vivaldi_trees_doors = []
    list_of_steps_bad_description = []

    k = 0
    j = 0

    # List of Vivaldi folder names (tst_case-1 ... etc)
    list_of_vivaldi_test_folder_names = [
        x for x in os.listdir(path_of_tests) if x[0:3] == "tst"
    ]

    for vivaldi_folder in list_of_vivaldi_test_folder_names:
        # Recovering _ivv files, _door files
        ivv_xml_files = ivv_files(path_of_tests, vivaldi_folder)
        doors_xml_files = doors_files(path_of_tests, vivaldi_folder)
        # Adding full path to each file (_ivv, _doors)
        list_of_vivaldi_ivv_files += file_full_path(
            ivv_xml_files, path_of_tests, vivaldi_folder
        )
        list_of_vivaldi_doors_files += file_full_path(
            doors_xml_files, path_of_tests, vivaldi_folder
        )

    # Initialization of trees for ivv and doors
    init_vivaldi_trees(
        list_of_vivaldi_ivv_files,
        list_of_vivaldi_trees_ivv,
        k,
    )
    init_vivaldi_trees(
        list_of_vivaldi_doors_files,
        list_of_vivaldi_trees_doors,
        j,
    )

    # Returns a list of step names by folder
    list_of_step_names_by_folder, list_of_steps_bad_description = vivaldi_step_names(list_of_vivaldi_trees_ivv)
    return (
        list_of_vivaldi_test_folder_names,
        list_of_vivaldi_trees_doors,
        list_of_step_names_by_folder,
        list_of_vivaldi_trees_ivv,
        list_of_steps_bad_description
    )

def get_doors_ivv(path_of_tests):
    list_of_test_id = []
    list_of_vivaldi_ivv_files = []
    list_of_vivaldi_trees_ivv = []
    list_of_vivaldi_doors_files = []
    list_of_vivaldi_trees_doors = []
    k = 0
    j = 0
    list_of_test_id = [
        x for x in os.listdir(path_of_tests) if x[0:3] == "tst"
    ]
    list_of_test_id.sort(key=natural_keys)

    for vivaldi_folder in list_of_test_id:
        # Recovering _ivv files, _door files
        ivv_xml_files = ivv_files(path_of_tests, vivaldi_folder)
        doors_xml_files = doors_files(path_of_tests, vivaldi_folder)
        # Adding full path to each file (_ivv, _doors)
        list_of_vivaldi_ivv_files += file_full_path(
            ivv_xml_files, path_of_tests, vivaldi_folder
        )
        list_of_vivaldi_doors_files += file_full_path(
            doors_xml_files, path_of_tests, vivaldi_folder
        )

    # Initialization of trees for ivv and doors
    init_vivaldi_trees(
        list_of_vivaldi_ivv_files,
        list_of_vivaldi_trees_ivv,
        k,
    )
    init_vivaldi_trees(
        list_of_vivaldi_doors_files,
        list_of_vivaldi_trees_doors,
        j,
    )
    return list_of_test_id, list_of_vivaldi_trees_ivv, list_of_vivaldi_trees_doors

# Given result in csv file in case of fail
def given_fail_message(step_counter, case_identifier, paragraph_identification, step_identifier, step_after_format):
    return "Step " + str(step_counter) + ";" + "[" + case_identifier + "-" + paragraph_identification + "-" + step_identifier + "]" + ";Given " + step_after_format.replace("(PR)", "") + ";Type must be X\n"

# Then result in csv file in case of fail
def then_fail_message(step_counter,case_identifier,paragraph_identification,step_identifier,step_after_format):
    return "Step " + str(step_counter) + ";" + "[" + case_identifier + "-" + paragraph_identification + "-" + step_identifier + "]" + ";Then " + step_after_format + ";Expected result must not be empty\n"


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
                problematic_step = given_fail_message(step_counter, case_identifier, paragraph_identification, step_identifier, step_after_format)
                displayed_message += (problematic_step.replace("--", "-")).replace(
                    "-]", "]"
                )
            elif step_context == "" and step_expected_result == "":
                problematic_step = then_fail_message(step_counter,case_identifier,paragraph_identification,step_identifier,step_after_format)
                displayed_message += (problematic_step.replace("--", "-")).replace(
                    "-]", "]"
                )
    return displayed_message


# Returns a list of all the elements that we are going to test in an etree._Element form
def list_of_elements(i_doors_tree: etree._Element, i_ivv_tree: etree._Element) -> list:
    test_type = None
    title = i_doors_tree.find("./Title")
    objective = i_doors_tree.find("./Objective")
    method = i_doors_tree.find("./Method")
    for extra_attribute in i_doors_tree.xpath("./ExtraAttributes/ExtraAttribute"):
        if extra_attribute.find("./Name").text == "Test type":
            test_type = extra_attribute.find("./Value")
    last_writer = i_ivv_tree.find("./Summary/Writer/Last/Name")
    writing_status = i_ivv_tree.find("./Summary/WritingStatus")
    description = i_ivv_tree.find("./Summary/Description/Description")

    list_of_elements_to_verify = [
        title,
        objective,
        method,
        test_type,
        last_writer,
        writing_status,
        description,
    ]
    return list_of_elements_to_verify


# Tests the <WritingStatus> and <Title> of each folder
def status_and_title_verification(
    list_of_elements_to_verify: list, identificator: str
) -> (bool, list, list, str):

    condition_to_start = True
    displayed_message = ""
    title_index = 0
    status_index = 5
    test_type_auto = "(AUTO)"

    current_test_type = list_of_elements_to_verify[title_index].text[0:6]
    test_status = list_of_elements_to_verify[status_index].text


    # List of elements that will be verified in the tst_case_verification() function
    list_of_names = ["objective", "method", "test_type", "last_writer", "description"]
    displayed_message += identificator + "\n"

    if test_status != "WrittenAndReviewedOK":
        condition_to_start = False
        displayed_message += (
            "WritingStatus;Got '" + test_status + "' expected 'WrittenAndReviewedOK'\n"
        )

    if current_test_type != test_type_auto:
        displayed_message += (
            "TITLE;'"
            + list_of_elements_to_verify[title_index].text
            + "' Doesn't start with (AUTO)\n"
        )
        condition_to_start = False

    del list_of_elements_to_verify[5]
    del list_of_elements_to_verify[0]

    return (
        condition_to_start,
        list_of_names,
        list_of_elements_to_verify,
        displayed_message,
    )


# Takes the message string containing all the errors and splits it in order to
# write in an organized way in the csv file
def split_displayed_msg(displayed_message: str, writer: csv.writer) -> None:
    list_by_line = displayed_message.split("\n")
    writer.writerow([list_by_line[0]])
    writer.writerow([""])
    for my_line in list_by_line[1:]:
        writer.writerow([my_line])
    writer.writerow("")


# Verifying if the test case folder satisfies all conditions
def tst_case_verification(
    list_of_elements_to_verify: list,
    writer: csv.writer,
    identificator: str,
    displayed_message_1: str,
) -> bool:
    (
        condition_to_start,
        list_of_names,
        list_of_elements_to_verify,
        displayed_message_0,
    ) = status_and_title_verification(list_of_elements_to_verify, identificator)
    list_length = len(list_of_elements_to_verify)
    for i in range(list_length):

        if (
            list_of_elements_to_verify[i] is None
            or list_of_elements_to_verify[i].text == ""
        ):
            displayed_message_0 += list_of_names[i] + ";IS NONE\n"
            condition_to_start *= False
    displayed_message = displayed_message_0 + displayed_message_1
    # If there is no problem with the givens and thens this string normally
    # should be empty
    if displayed_message_1 != "":
        condition_to_start = False
    # Writing the errors in the csv file
    if not condition_to_start:
        split_displayed_msg(displayed_message, writer)

    return condition_to_start


# Displays the yes/no interface for either keeping the folder or deleting it
def query_yes_no(
    question: str, root_tk, is_root_used, default="yes"
):  # pragma: no cover
    if not is_root_used:
        valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input().lower()
            if default is not None and choice == "":
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write(
                    "Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n"
                )
    else:
        # sys.stdout.write(question + "\n")
        print(question + "\n")
        root_tk.query_pop_up_text = question + "\n"
        root_tk.top = Toplevel(root_tk)
        root_tk.top.geometry("900x200")
        root_tk.top.title("Force generation")
        root_width = root_tk.winfo_screenwidth()
        root_height = root_tk.winfo_screenheight()
        root_tk.top.geometry(
            "+%d+%d" % ((root_width / 2) - 400, (root_height / 2) - 150)
        )

        root_tk.result = BooleanVar()

        answer_label = Label(root_tk.top, text=root_tk.query_pop_up_text)
        # answer_label.grid(row=0, column=0)
        answer_label.place(anchor=CENTER, relx=0.5, rely=0.3)

        def cancel_gen():
            root_tk.result.set(False)
            root_tk.top.destroy()

        root_tk.top.protocol("WM_DELETE_WINDOW", cancel_gen)

        def answer_yes_function(self):
            self.top.destroy()
            root_tk.result.set(True)

        def answer_no_function(self):
            self.top.destroy()
            root_tk.result.set(False)

        yes_answer = Button(
            root_tk.top, text="Yes", command=lambda: answer_yes_function(root_tk)
        )
        # yes_answer.grid(row=1, column=0, pady=10)
        yes_answer.place(anchor=CENTER, rely=0.6, relx=0.4)
        no_answer = Button(
            root_tk.top, text="No", command=lambda: answer_no_function(root_tk)
        )
        # no_answer.grid(row=1, column=1, pady=10)
        no_answer.place(anchor=CENTER, rely=0.6, relx=0.6)
        root_tk.wait_variable(root_tk.result)
        return root_tk.result.get()

# Function verifies elements
def verify_elements(vivaldi_tree_ivv, vivaldi_tree_doors, writer):
    to_display = True
    i_identificator = vivaldi_tree_doors.find("./Identification").text
    displayed_message = then_given_error_list(vivaldi_tree_ivv)
    list_of_elements_to_verify = list_of_elements(vivaldi_tree_doors, vivaldi_tree_ivv)
    # Testing if all elements exist
    to_display = tst_case_verification(
        list_of_elements_to_verify, writer, i_identificator, displayed_message
    )
    return to_display

# Verify step descriptions
def verify_step_description(bad_step_description, to_display, test_name, writer):
    condition_to_start = True
    if bad_step_description:
        condition_to_start = False
        if to_display:  # If to_display == False => test name is already written
            writer.writerow([test_name])
            writer.writerow([])
        writer.writerow(["Step"])
        writer.writerow([])
        for elem in bad_step_description:
            writer.writerow([elem.strip()] + ["The step description contains one of :  {\", [, ]}"])
        writer.writerow([])
        writer.writerow([])
    return condition_to_start


def create_squish_folder(squish_bdd, folder, list_of_existing_folders, list_of_existing_folders_paths):
    is_existing = False
    squish_folder_path = squish_bdd + "/" + folder
    # Stocking the existing folders, to decide later if we will delete or keep them
    if os.path.isdir(squish_folder_path):
        list_of_existing_folders.append(folder)
        list_of_existing_folders_paths.append(squish_folder_path)
        is_existing = True
    return is_existing

def force_delete(list_of_existing_folders_paths):
    # copy_tree(squish_bdd, backup_tests_path)
    [
        shutil.rmtree(folder_path)
        for folder_path in list_of_existing_folders_paths
    ]
    return True

def write_existing_tests_in_csv(list_of_existing_folders, writer):
    writer.writerow(["Tests already exist in Squish directory"])
    writer.writerow([""])
    for test_directory in list_of_existing_folders:
        writer.writerow([test_directory])

# We pass all the doors and ivv files in order to test if each one of
# them satisfies the conditions
def is_verification_ok(
    list_of_vivaldi_trees_doors: list,
    list_of_vivaldi_trees_ivv: list,
    writer: csv.writer,
    list_of_vivaldi_test_folder_names: list,
    squish_bdd,
    force_permission: bool,
    root_tk,
    is_root_used,
    list_of_steps_bad_description
) -> (bool, csv.writer):  # pragma: no cover

    # Initializing
    list_of_existing_folders = []
    list_of_existing_folders_paths = []
    condition_to_start = True
    is_existing = False
    is_writing = False
    to_display = True
    number_of_folders = len(list_of_vivaldi_trees_doors)

    # Verifying if all the elements exist (Title, WritingStatus ...) & If all the step descriptions are well written
    for i in range(number_of_folders):
        # Verifying if all the elements exist (Title, WritingStatus ...)
        to_display = verify_elements(list_of_vivaldi_trees_ivv[i], list_of_vivaldi_trees_doors[i], writer)
        condition_to_start *= to_display
        # Testing if all step descriptions satisfy their verification
        condition_to_start *= verify_step_description(list_of_steps_bad_description[i], to_display, list_of_vivaldi_test_folder_names[i], writer)
    # If all elements exist, we verify if there are any existing folders
    if condition_to_start:
        for folder in list_of_vivaldi_test_folder_names:
            is_existing = create_squish_folder(squish_bdd, folder, list_of_existing_folders, list_of_existing_folders_paths)
        if is_existing and not force_permission:
            list_of_existing_folders.sort(key=natural_keys)
            is_deleting_folder = query_yes_no(
                "Warning!: These tests will be deleted\n("
                + "  ".join(list_of_existing_folders)
                + ")\nDo you want to force the generation and delete them ?",
                root_tk,
                is_root_used,
            )
            # Deleting the folders and continuing the process
            if is_deleting_folder:
                is_writing = force_delete(list_of_existing_folders_paths)
            # Keeping the folders and stopping the process because is_writing = False
            else:
                # Writing in the file of errors the existing tests
                write_existing_tests_in_csv(list_of_existing_folders, writer)
        elif force_permission:
            is_writing = force_delete(list_of_existing_folders_paths)
        elif not is_existing:
            is_writing = True
    return is_writing


def get_info_from_conf(conf_file):  # pragma: no cover
    vivaldi_campaign, path_of_ivvq_folder = ("", "")
    my_file = open(conf_file, "r")
    for line in my_file:
        if "vivaldi_campaign" in line:
            vivaldi_campaign = line.split()[1]
        elif "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]
    test_py = path_of_ivvq_folder + "/src/test.py"
    path_of_results = path_of_ivvq_folder + "/results"
    csv_generate_bdd_problems = "/generate_bdd_problems.csv"
    suite_bdd = path_of_ivvq_folder + "/tests/suite_bdd"
    return (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_generate_bdd_problems,
        path_of_ivvq_folder,
        path_of_results,
    )


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
        print("Files are committed\nContinuing...\n")
    else:
        is_ready_to_commit = False
        print("Files not committed yet : \n", git_status_result)
        print("Stopped")
    return is_ready_to_commit


# This function is responsible for generating the BDD files if there is
# no error. Else, it generates a CSV file
# Containing all the errors that need to be corrected
# Return True if file was generated; else return False
def generate_bdd_files(
    vivaldi_suite_campaign: str,
    squish_bdd: str,
    test_py_path: str,
    actual_results_folder: str,
    csv_generate_bdd_problems,
    force_permission: bool,
    root_tk,
    is_root_used,
) -> bool:
    # Recovering the path of test suites
    path_of_tests = vivaldi_suite_campaign + "/TestSuites"
    i = 0
    # Initializing trees of the Vivaldi files, recovering steps by each
    # folder and the test names
    (
        list_of_vivaldi_test_folder_names,
        list_of_vivaldi_trees_doors,
        list_of_step_names_by_folder,
        list_of_vivaldi_trees_ivv,
        list_of_steps_bad_description
    ) = get_ivv_doors_data(path_of_tests)
    # Initializing the CSV file
    try:
        with open(csv_generate_bdd_problems, "w", newline="") as csv_file:
            writer = csv.writer(
                csv_file, dialect="excel", delimiter=",", quoting=csv.QUOTE_MINIMAL
            )
            # Returns a bool, so we can either start filling files or stop the execution
            if is_verification_ok(
                list_of_vivaldi_trees_doors,
                list_of_vivaldi_trees_ivv,
                writer,
                list_of_vivaldi_test_folder_names,
                squish_bdd,
                force_permission,
                root_tk,
                is_root_used,
                list_of_steps_bad_description
            ):

                for folder in list_of_vivaldi_test_folder_names:
                    # Recovering the needed information, so we can create our folder
                    squish_folder_path = squish_bdd + "/" + folder

                    list_of_steps = list_of_step_names_by_folder[i]
                    title_of_file = recovering_title(list_of_vivaldi_trees_doors[i])
                    objectives = recovering_objectives(list_of_vivaldi_trees_doors[i])
                    # Creating and filling the Squish folder
                    os.mkdir(squish_folder_path)
                    shutil.copy(test_py_path, squish_folder_path)
                    # Writing the steps into the BDD file
                    writing_file(
                        squish_folder_path, title_of_file, objectives, list_of_steps
                    )
                    i += 1
                # If the csv file is empty delete it
                if os.stat(csv_generate_bdd_problems).st_size == 0:
                    os.remove(csv_generate_bdd_problems)
                # If everything went good, print Success
                print("\nGeneration of BDD files succeeded\n")
                if is_root_used:
                    if messagebox.askyesno(
                        "Success !",
                        "Generation of BDD files succeeded\nOpen Squish directory",
                    ):
                        os.system('xdg-open "%s"' % squish_bdd)
            else:
                # Else print Error
                print("\nGeneration of BDD files failed : Check CSV file\n")
                if is_root_used:
                    if messagebox.askyesno(
                        "Error", "Generation of BDD files failed\nCheck CSV file"
                    ):
                        os.system('xdg-open "%s"' % actual_results_folder)
                return False
    except EnvironmentError:  # pragma: no cover
        return False

    return True

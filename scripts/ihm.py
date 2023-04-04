import shutil
from datetime import datetime
import re
from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import csv
from bdd_generator.generate_functions import generate_bdd_files, verify_git, get_ivv_doors_data, get_doors_ivv
from results_generator.generate_results_functions import (
    verification_before_execution, verification_before_execution_by_test,
    importing_data_from_squish_to_vivaldi,
)
import sys
import os
import random
from tkinter import messagebox


from bdd_generator.compare_tests import (
    get_info_from_conf_comp,
    verify_names_of_tests,
    filling_csv_file,
)


# Personal PC init

if os.environ.get('DISPLAY','') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')


def get_vivaldi_campaign(conf):
    vivaldi_campaign = ""
    my_file = open(conf, "r")
    for line in my_file:
        if "vivaldi_campaign" in line:
            vivaldi_campaign = line.split()[1]
    return vivaldi_campaign


def get_result_folder(conf):
    result_folder = ""
    my_file = open(conf, "r")
    for line in my_file:
        if "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]
            result_folder = path_of_ivvq_folder + "/results"
    return result_folder


def get_test_folder(conf):
    test_folder = ""
    my_file = open(conf, "r")
    for line in my_file:
        if "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]
            test_folder = path_of_ivvq_folder + "/tests"
    return test_folder


def get_info_from_conf(conf_file):  # pragma: no cover
    vivaldi_campaign, path_of_ivvq_folder = (
        "",
        "",
    )
    my_file = open(conf_file, "r")
    for line in my_file:
        if "vivaldi_campaign" in line:
            vivaldi_campaign = line.split()[1]
        elif "path_of_ivvq_folder" in line:
            path_of_ivvq_folder = line.split()[1]

    suite_bdd = path_of_ivvq_folder + "/tests/suite_bdd"
    squish_runner_path = (
        "~/squish-for-qt-7.0.0/bin/squishrunner --host 172.17.0.1 --testsuite "
    )
    xml_version = " --reportgen xml3.5,"
    path_of_results = path_of_ivvq_folder + "/results"
    results_xml = "/tmp/results1"
    csv_file_before_execution = "/beforeExecution.csv"
    test_py = path_of_ivvq_folder + "/src/test.py"
    csv_generate_bdd_problems = "/generate_bdd_problems.csv"
    return (
        vivaldi_campaign,
        path_of_ivvq_folder,
        suite_bdd,
        squish_runner_path,
        xml_version,
        path_of_results,
        results_xml,
        csv_file_before_execution,
        test_py,
        csv_generate_bdd_problems,
    )

def get_treeview_values(path_of_tests, root):
    # Recovering Test id, Test name, Exec time & status from Vivaldi files
    # Test names list
    list_of_test_names = []
    # Test status list
    list_of_test_status = []
    # Exec time list
    list_of_exec_time = []
    # Test id list
    list_of_test_id = []

    # Initializing vivaldi files
    list_of_test_id, list_of_vivaldi_trees_ivv, list_of_vivaldi_trees_doors  = get_doors_ivv(path_of_tests)

    def get_test_name(vivaldi_doors):
        return vivaldi_doors.find("./Title").text
    def get_status(vivaldi_ivv):
        status = vivaldi_ivv.find("./Summary/LastRunResult/Consolidated").text
        if status == "OK":
            root.number_of_executed_tests_in_campaign += 1
            return "PASS"

        elif status == "KO":
            root.number_of_executed_tests_in_campaign += 1
            return "FAIL"

        else:
            return status

    def get_exec_time(vivaldi_ivv):
        exec_time = vivaldi_ivv.find("./Summary/LastRunDuration").text
        if exec_time == "" or exec_time is None:
            return "1h"
        else:
            return exec_time

    for vivaldi_doors in list_of_vivaldi_trees_doors:
        list_of_test_names.append(get_test_name(vivaldi_doors))

    for vivaldi_ivv in list_of_vivaldi_trees_ivv:
        list_of_test_status.append(get_status(vivaldi_ivv))
        list_of_exec_time.append(get_exec_time(vivaldi_ivv))


    return list_of_test_names, list_of_test_status, list_of_test_id, list_of_exec_time


# Open filedialog for vivaldi campaign
def select_files(self):
    if self.base_tab.event_running:
        return False
    # Lock event until it's finished
    self.base_tab.generate_bdd_button.config(state="disabled")
    self.base_tab.result_folder_button.config(state="disabled")
    self.base_tab.compare_tests_button.config(state="disabled")
    self.base_tab.event_running = True
    new_foldername = fd.askdirectory(title="Open files", initialdir=self.base_tab.test_folder)
    # To change

    # Destroying the old table
    #self.exec_tab.exec_tests_table.destroy


    if len(new_foldername) != 0:

        # Verifying if the chosen path is valid or no
        if not os.path.isdir(new_foldername + "/TestSuites"):
            print("\nInvalid test campaign\nPlease select a valid test campaign\n")
            messagebox.showerror(
                "Error", "Invalid test campaign\nPlease select a valid test campaign"
            )
        else:
            self.base_tab.foldername.set(new_foldername)
            updating_treeview_after_changing_campaign(self)

            # New checklist
            checklist(self)
    self.exec_tab.update()
    self.exec_tab.update_idletasks()

    self.base_tab.update()
    self.base_tab.update_idletasks()
    self.base_tab.generate_bdd_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.result_folder_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.compare_tests_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.update()
    self.base_tab.update_idletasks()


    # Release event handler
    self.base_tab.event_running = False
    return


def generate_bdd(self, conf):
    if self.base_tab.event_running:
        return False
        # Lock event until it's finished
    self.base_tab.result_folder_button.config(state="disabled")
    self.base_tab.compare_tests_button.config(state="disabled")
    self.base_tab.open_button.config(state="disabled")
    self.base_tab.event_running = True
    print(
        "------------------------------------------------------------------------------"
        "------------------------------"
    )
    print("\nScript launched : Generate BDD tests\n")
    # print(self.generate_bdd_button['state'])
    (
        vivaldi_campaign,
        path_of_ivvq_folder,
        suite_bdd,
        squish_runner_path,
        xml_version,
        path_of_results,
        results_xml,
        csv_file_before_execution,
        test_py,
        csv_generate_bdd_problems,
    ) = get_info_from_conf(conf)
    # Updating the arguments
    vivaldi_campaign = self.base_tab.foldername.get()
    print("Vivaldi campaign used :\n" + vivaldi_campaign + "\n")
    if os.path.exists(vivaldi_campaign + "/TestSuites"):
        # is_ready_to_commit = verify_git(path_of_ivvq_folder)
        is_ready_to_commit = True
        if is_ready_to_commit:
            # initialization

            time_now = str(datetime.now())
            self.base_tab.actual_results_folder = (
                path_of_results
                + "/"
                + str(time_now)[:19]
                + "_"
                + vivaldi_campaign.split("/")[-1]
            )

            if not os.path.exists(self.base_tab.actual_results_folder):
                os.makedirs(self.base_tab.actual_results_folder)

            generate_bdd_files(
                vivaldi_campaign,
                suite_bdd,
                test_py,
                self.base_tab.actual_results_folder,
                self.base_tab.actual_results_folder + csv_generate_bdd_problems,
                False,
                self.base_tab,
                True,
            )

            if len(os.listdir(self.base_tab.actual_results_folder)) == 0:
                os.rmdir(self.base_tab.actual_results_folder)
    else:
        messagebox.showerror(
            "Error", "\nInvalid test campaign\nPlease select a valid test campaign\n"
        )
        print("\nInvalid test campaign\nPlease select a valid test campaign\n")

    self.base_tab.update()
    self.base_tab.update_idletasks()
    self.base_tab.result_folder_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.compare_tests_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.open_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.update()
    self.base_tab.update_idletasks()
    # Release event handler
    self.base_tab.event_running = False
    return


def updating_treeview(root):
    # Deleting tests with status different than Error, because they are going to get updated
    # Error status must remain
    for item in root.exec_tab.tree_of_selected_tests.get_children():
        if root.exec_tab.tree_of_selected_tests.item(item)['values'][3] != "Error : Check CSV file":
            if root.exec_tab.tree_of_selected_tests.item(item)['values'][3] == "PASS" or root.exec_tab.tree_of_selected_tests.item(item)['values'][3] == "FAIL":
                root.exec_tab.number_of_selected_tests_executed -= 1
            root.exec_tab.number_of_selected_tests -= 1
            root.exec_tab.tree_of_selected_tests.delete(item)

    # Initializing counter of executed tests
    root.number_of_executed_tests_in_campaign = 0
    list_of_test_names, list_of_test_status, list_of_vivaldi_folder_names, list_of_exec_time = get_treeview_values(root.base_tab.foldername.get() + "/TestSuites", root)
    # Exec tests / total tests
    #print("Number of executed tests in the campaign : ", root.number_of_executed_tests_in_campaign, "/", len(list_of_vivaldi_folder_names))

    # Iterate through list of tests that are selected
    for checked_test in root.checked_tests:
        # For each test we check if doesn't exist in the treeview => it got deleted and it need to get updated
        items = root.exec_tab.tree_of_selected_tests.get_children()
        for item in items:
            item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
            if checked_test not in item_text:
                # recovering index of this test from the list of vivaldi files
                i = list_of_vivaldi_folder_names.index(checked_test)

                if list_of_test_status[i] == "PASS":
                    root.exec_tab.tree_of_selected_tests.insert(parent='', index='end', iid=i, text='',tag="PASS",
                                              values=(
                                                  list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                                  list_of_test_status[i]))
                    root.exec_tab.number_of_selected_tests_executed += 1
                    root.exec_tab.number_of_selected_tests += 1
                elif list_of_test_status[i] == "FAIL":
                    root.exec_tab.tree_of_selected_tests.insert(parent='', index='end', iid=i, text='',tag="FAIL",
                                              values=(
                                                  list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                                  list_of_test_status[i]))
                    root.exec_tab.number_of_selected_tests_executed += 1
                    root.exec_tab.number_of_selected_tests += 1
                else:
                    root.exec_tab.tree_of_selected_tests.insert(parent='', index='end', iid=i, text='',
                                              values=(
                                              list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i], list_of_test_status[i]))
                    root.exec_tab.number_of_selected_tests += 1
    root.exec_tab.counter_1.set(
        str(root.number_of_executed_tests_in_campaign) + "/" + str(len(list_of_vivaldi_folder_names)))
    root.exec_tab.counter_2.set(
        str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))
def updating_treeview_after_changing_campaign(root):
    # Deleting tests with status different than Error
    # Error status must remain
    for item in root.exec_tab.tree.get_children():
            root.exec_tab.tree.delete(item)
    # Initializing counters
    root.number_of_executed_tests_in_campaign = 0
    root.exec_tab.number_of_selected_tests_executed = 0
    root.exec_tab.number_of_selected_tests = 0

    list_of_test_names, list_of_test_status, list_of_vivaldi_folder_names, list_of_exec_time = get_treeview_values(root.base_tab.foldername.get() + "/TestSuites", root)

    # Disabled entry for number of tests with PASS/FAIL divided by number of total tests
    root.exec_tab.counter_1.set(str(root.number_of_executed_tests_in_campaign) + "/" + str(len(list_of_vivaldi_folder_names)))
    root.exec_tab.counter_2.set(str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))


    for i in range(len(list_of_vivaldi_folder_names)):
        if list_of_test_status[i] == "PASS":
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',tag="PASS",
                                      values=(
                                          list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                          list_of_test_status[i]))
        elif list_of_test_status[i] == "FAIL":
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',tag="FAIL",
                                      values=(
                                          list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                          list_of_test_status[i]))
        else:
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',
                                      values=(
                                      list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i], list_of_test_status[i]))

    # Clearing the treeview of selected tests
    if root.exec_tab.tree_of_selected_tests.get_children():
        root.exec_tab.tree_of_selected_tests.delete(*root.exec_tab.tree_of_selected_tests.get_children())

def update_tree_element_to_ongoing(root, vivaldi_test):
    # search in the list of tests vivaldi_test
    # recover its treeview element
    # Update it
    items = root.exec_tab.tree_of_selected_tests.get_children()
    for item in items:
        item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
        if vivaldi_test in item_text:
            selected_item_values = root.exec_tab.tree_of_selected_tests.item(item)['values']
            status = root.exec_tab.tree_of_selected_tests.item(item)["values"][3]
            if status == "PASS" or status == "FAIL":
                root.exec_tab.number_of_selected_tests_executed -= 1
                root.number_of_executed_tests_in_campaign -= 1
            # Modifying status into ONGOING
            selected_item_values[3] = "ONGOING"
            # updating values
            root.exec_tab.tree_of_selected_tests.item(item, values=selected_item_values, tag="ONGOING")
    # updating the counter
    root.exec_tab.counter_2.set(
        str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))
    root.exec_tab.counter_1.set(
        str(root.number_of_executed_tests_in_campaign) + "/" + str(
            len(root.exec_tab.exec_tests_table.list_of_int_var)))

def update_tree_element_to_error(root, vivaldi_test):
    # search in the list of tests vivaldi_test
    # recover its treeview element
    # Update it
    items = root.exec_tab.tree_of_selected_tests.get_children()
    for item in items:
        item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
        if vivaldi_test in item_text:
            selected_item_values = root.exec_tab.tree_of_selected_tests.item(item)['values']
            status = root.exec_tab.tree_of_selected_tests.item(item)["values"][3]
            if status == "PASS" or status == "FAIL":
                root.exec_tab.number_of_selected_tests_executed -= 1
                root.number_of_executed_tests_in_campaign -= 1
            # Modifying status into ERROR
            selected_item_values[3] = "Error : Check CSV file"
            #updating values
            root.exec_tab.tree_of_selected_tests.item(item,values=selected_item_values,tag="ERROR")
    #updating the counter
    root.exec_tab.counter_2.set(
        str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))
    root.exec_tab.counter_1.set(
        str(root.number_of_executed_tests_in_campaign) + "/" + str(len(root.exec_tab.exec_tests_table.list_of_int_var)))

def recover_checked_tests(root):
    items = root.exec_tab.tree_of_selected_tests.get_children()
    for item in items:
        item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
        index = root.base_tab.list_of_vivaldi_test_folder_names.index(item_text)
        if root.exec_tab.exec_tests_table.list_of_int_var[index].get():
            root.checked_tests.append(item_text)


def confirm_tests(root):
    #print(root.checked_tests)
    root.checked_tests = []
    # recovering the checked tests
    recover_checked_tests(root)

    print(root.checked_tests)

    if root.checked_tests:
        root.exec_tab.exec_tests_table.tests_confirmed.set(1)
    else:
        root.exec_tab.exec_tests_table.tests_confirmed.set(2)
    generate_results(root, root.conf)





def confirm_random_tests(root):
    root.checked_tests = []
    # recovering the checked tests
    recover_checked_tests(root)
    if root.checked_tests:
        rows = [(root.exec_tab.tree_of_selected_tests.item(item)['values'], root.exec_tab.tree_of_selected_tests.item(item)['tags']) for item in root.exec_tab.tree_of_selected_tests.get_children()]
        random.shuffle(rows)
        root.exec_tab.tree_of_selected_tests.delete(*root.exec_tab.tree_of_selected_tests.get_children())
        for row, tags in rows:
            root.exec_tab.tree_of_selected_tests.insert('', 'end', values=row, tags=tags)
        #print(root.checked_tests)
        #root.exec_tab.exec_tests_table.tests_confirmed.set(1)
    else:
        root.exec_tab.exec_tests_table.tests_confirmed.set(2)
    #generate_results(root, root.conf)
    #updating_treeview(root)

def verify_tests(root):
    root.checked_tests = []
    # recovering the checked tests
    recover_checked_tests(root)
    print(root.checked_tests)
    if root.checked_tests:
        root.exec_tab.exec_tests_table.tests_confirmed.set(1)
    else:
        root.exec_tab.exec_tests_table.tests_confirmed.set(2)
    verifying_selected_tests(root,root.conf)



# Human sorting
def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split(r"(\d+)", text)]


def list_of_test_cases(root, path_vivaldi_campaign):
    test_cases = ""

    # .grid(row=i, column=1, sticky="NEWS", padx=10, columnspan=2)

    def close_btn():
        root.exec_tab.exec_tests_table.tests_confirmed.set(3)

    if root.exec_tab.exec_tests_table.tests_confirmed.get() == 1:
        for test_case in root.base_tab.list_of_vivaldi_test_folder_names:
            test_cases += " --testcase " + test_case
        return test_cases, root.checked_tests
    else:
        return None, None


def generate_results(self, conf):
    if self.base_tab.event_running:
        return False
        # Lock event until it's finished
    self.base_tab.generate_bdd_button.config(state="disabled")
    self.base_tab.result_folder_button.config(state="disabled")
    self.base_tab.compare_tests_button.config(state="disabled")
    self.base_tab.open_button.config(state="disabled")
    self.base_tab.event_running = True
    print(
        "------------------------------------------------------------------------------"
        "------------------------------"
    )
    print("\nScript launched : Execute & Generate results\n")
    self.base_tab.version.set(self.base_tab.version.get())
    self.base_tab.soft.set(self.base_tab.soft.get())
    self.base_tab.hard.set(self.base_tab.hard.get())
    # Bool if verification done
    is_not_verified = True
    # list of tests that needs to be updated to error
    bad_update = []
    # Vivaldi files list
    vivaldi_files = []
    # Init ready_to_execute
    ready_to_execute = True

    (
        vivaldi_campaign,
        path_of_ivvq_folder,
        suite_bdd,
        squish_runner_path,
        xml_version,
        path_of_results,
        result_xml,
        csv_file_before_execution,
        test_py,
        csv_generate_bdd_problems,
    ) = get_info_from_conf(conf)

    vivaldi_campaign = self.base_tab.foldername.get()
    print("Vivaldi campaign used :\n" + vivaldi_campaign + "\n")
    if os.path.exists(vivaldi_campaign + "/TestSuites"):

        version_under, soft_env, hard_env = (
            self.base_tab.version.get(),
            self.base_tab.soft.get(),
            self.base_tab.hard.get(),
        )
        # is_ready_to_commit = verify_git(path_of_ivvq_folder)
        is_ready_to_commit = True
        if is_ready_to_commit:
            # initialization
            """
            test_cases_line, test_cases_vivaldi = list_of_test_cases(
                self, vivaldi_campaign
            )
            """
            # test_cases_vivaldi is self.checked_tests
            # if test_cases_line is not None:
            if self.exec_tab.exec_tests_table.tests_confirmed.get() == 1:
                # Creating the folder of results
                time_now = datetime.now()
                campaign_name = vivaldi_campaign.split("/")[-1]
                self.base_tab.actual_results_folder = (
                        path_of_results + "/" + str(time_now)[:19] + "_" + campaign_name
                )
                os.makedirs(self.base_tab.actual_results_folder)
                for test_case in self.checked_tests:

                    print("executing : ", test_case)
                    line_of_execution = (
                        squish_runner_path
                        + suite_bdd
                        #+ test_cases_line
                        + " --testcase " + test_case
                        + xml_version
                        + result_xml
                    )
                    xml_name = result_xml + "/results.xml"


                    if is_not_verified is True:
                        # calling functions
                        with open(
                                self.base_tab.actual_results_folder + csv_file_before_execution,
                                "w",
                                newline="",
                        ) as csv_file:
                            writer = csv.writer(
                                csv_file,
                                dialect="excel",
                                delimiter=",",
                                quoting=csv.QUOTE_MINIMAL,
                            )
                            # loop and verify each test
                            for test_case in self.checked_tests:
                                vivaldi_file, verified_test = verification_before_execution_by_test(
                                    suite_bdd,
                                    vivaldi_campaign,
                                    writer,
                                    test_case,
                                    path_of_results,
                                )
                                # we use index because vivaldi_file is a list of one element
                                vivaldi_files.append(vivaldi_file[0])
                                if not verified_test:
                                    bad_update.append(test_case)
                                    # this happens only for the first test since is_not_verified becomes false
                                    update_tree_element_to_error(self, test_case)
                                    ready_to_execute *= verified_test
                                    #print("Ready to execute :", ready_to_execute)



                            """
                            vivaldi_files, ready_to_execute = verification_before_execution(
                                suite_bdd,
                                vivaldi_campaign,
                                writer,
                                self.checked_tests,
                                path_of_results,
                            )
                            """
                            is_not_verified = False
                            # Returning a boxanswer
                            if not ready_to_execute:
                                print(ready_to_execute)
                                print("\nExecution failed : Check the results folder\n")
                                if messagebox.askyesno(
                                        "Error", "Execution failed : Check the results folder\n"
                                ):
                                    os.system('xdg-open "%s"' % self.base_tab.actual_results_folder)
                    if is_not_verified is False:
                        # Updating the status into ONGOING while executing
                        # status of this test turn to ongoing only if there are no bad tests recorded
                        if not bad_update:
                            update_tree_element_to_ongoing(self, test_case)
                        if ready_to_execute:
                            print("\nExecuting Squish tests...\n")
                            os.system(line_of_execution)
                            print("\nSquish tests are executed\n")
                            is_bad_recorded = importing_data_from_squish_to_vivaldi(
                                xml_name,
                                vivaldi_files,
                                self.base_tab.actual_results_folder,
                                version_under,
                                soft_env,
                                hard_env,
                            )
                            if not is_bad_recorded:
                                print(
                                    "\nExecution of BDD tests and filling Vivaldi files "
                                    "succeeded\n"
                                )
                                if messagebox.askyesno(
                                    "Success !",
                                    "Execution of BDD tests and filling Vivaldi files "
                                    "succeeded\nOpen results folder",
                                ):
                                    os.system('xdg-open "%s"' % self.base_tab.actual_results_folder)
                            else:
                                print(
                                    "\nBDD files are not recorded correctly : "
                                    "Check CSV file\n"
                                )
                                if messagebox.askyesno(
                                    "Error",
                                    "BDD files are not recorded correctly : "
                                    "Check CSV file\n",
                                ):
                                    os.system('xdg-open "%s"' % self.base_tab.actual_results_folder)
                        else:
                            # Testing if this actual test got errors
                            if test_case in bad_update:
                                update_tree_element_to_error(self, test_case)

                file_path = self.base_tab.actual_results_folder + csv_file_before_execution
                if os.stat(file_path).st_size == 0:
                    #os.remove(file_path)
                    shutil.rmtree(self.base_tab.actual_results_folder)

                    # Updating the treeview (mainly the status part)
                    updating_treeview(self)
            else:
                if self.exec_tab.exec_tests_table.tests_confirmed.get() != 3:
                    print("Please choose a test\n")
                    messagebox.showwarning("Warning", "Please choose a test")

    else:
        print("\nInvalid test campaign\nPlease select a valid test campaign\n")
        messagebox.showerror(
            "Error", "\nInvalid test campaign\nPlease select a valid test campaign\n"
        )

    self.base_tab.update()
    self.base_tab.update_idletasks()
    self.base_tab.generate_bdd_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.result_folder_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.compare_tests_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.open_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.update()
    self.base_tab.update_idletasks()
    # Release event handler
    self.base_tab.event_running = False
    return


def verifying_selected_tests(self, conf):
    if self.base_tab.event_running:
        return False
        # Lock event until it's finished
    self.base_tab.generate_bdd_button.config(state="disabled")
    self.base_tab.result_folder_button.config(state="disabled")
    self.base_tab.compare_tests_button.config(state="disabled")
    self.base_tab.open_button.config(state="disabled")
    self.base_tab.event_running = True
    print(
        "------------------------------------------------------------------------------"
        "------------------------------"
    )
    print("\nScript launched : Verifying selected tests\n")
    self.base_tab.version.set(self.base_tab.version.get())
    self.base_tab.soft.set(self.base_tab.soft.get())
    self.base_tab.hard.set(self.base_tab.hard.get())
    # Bool if verification done
    is_not_verified = True
    # list of tests that needs to be updated to error
    bad_update = []
    # Vivaldi files list
    vivaldi_files = []
    # Init ready_to_execute
    ready_to_execute = True

    (
        vivaldi_campaign,
        path_of_ivvq_folder,
        suite_bdd,
        squish_runner_path,
        xml_version,
        path_of_results,
        result_xml,
        csv_file_before_execution,
        test_py,
        csv_generate_bdd_problems,
    ) = get_info_from_conf(conf)

    vivaldi_campaign = self.base_tab.foldername.get()
    print("Vivaldi campaign used :\n" + vivaldi_campaign + "\n")
    if os.path.exists(vivaldi_campaign + "/TestSuites"):

        version_under, soft_env, hard_env = (
            self.base_tab.version.get(),
            self.base_tab.soft.get(),
            self.base_tab.hard.get(),
        )
        # is_ready_to_commit = verify_git(path_of_ivvq_folder)
        is_ready_to_commit = True
        if is_ready_to_commit:
            # test_cases_vivaldi is self.checked_tests
            # if test_cases_line is not None:
            if self.exec_tab.exec_tests_table.tests_confirmed.get() == 1:
                # Creating the folder of results
                time_now = datetime.now()
                campaign_name = vivaldi_campaign.split("/")[-1]
                self.base_tab.actual_results_folder = (
                        path_of_results + "/" + str(time_now)[:19] + "_" + campaign_name
                )
                os.makedirs(self.base_tab.actual_results_folder)
                for test_case in self.checked_tests:

                    if is_not_verified is True:
                        # calling functions
                        with open(
                                self.base_tab.actual_results_folder + csv_file_before_execution,
                                "w",
                                newline="",
                        ) as csv_file:
                            writer = csv.writer(
                                csv_file,
                                dialect="excel",
                                delimiter=",",
                                quoting=csv.QUOTE_MINIMAL,
                            )
                            # loop and verify each test
                            for test_case in self.checked_tests:
                                vivaldi_file, verified_test = verification_before_execution_by_test(
                                    suite_bdd,
                                    vivaldi_campaign,
                                    writer,
                                    test_case,
                                    path_of_results,
                                )
                                # we use index because vivaldi_file is a list of one element
                                vivaldi_files.append(vivaldi_file[0])
                                if not verified_test:
                                    bad_update.append(test_case)
                                    # this happens only for the first test since is_not_verified becomes false
                                    update_tree_element_to_error(self, test_case)
                                    ready_to_execute *= verified_test

                            is_not_verified = False
                            # Returning a boxanswer
                            if not ready_to_execute:
                                print("\nVerification failed : Check the results folder\n")
                                if messagebox.askyesno(
                                        "Error", "Verification failed : Check the results folder\n"
                                ):
                                    os.system('xdg-open "%s"' % self.base_tab.actual_results_folder)
                    if is_not_verified is False:
                        # Updating the status into ONGOING while executing
                        # status of this test turn to ongoing only if there are no bad tests recorded
                        #if not bad_update:
                            #update_tree_element_to_ongoing(self, test_case)

                        if not ready_to_execute:
                            # Testing if this actual test got errors
                            if test_case in bad_update:
                                update_tree_element_to_error(self, test_case)

                file_path = self.base_tab.actual_results_folder + csv_file_before_execution
                if os.stat(file_path).st_size == 0:
                    #os.remove(file_path)
                    shutil.rmtree(self.base_tab.actual_results_folder)

                    # Updating the treeview (mainly the status part)
                    updating_treeview(self)
            else:
                if self.exec_tab.exec_tests_table.tests_confirmed.get() != 3:
                    print("Please choose a test\n")
                    messagebox.showwarning("Warning", "Please choose a test")

    else:
        print("\n\n")
        messagebox.showerror(
            "Error", "\nInvalid test campaign\nPlease select a valid test campaign\n"
        )

    self.base_tab.update()
    self.base_tab.update_idletasks()
    self.base_tab.generate_bdd_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.result_folder_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.compare_tests_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.open_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.update()
    self.base_tab.update_idletasks()
    # Release event handler
    self.base_tab.event_running = False
    return


def compare_tests(self, conf):
    if self.base_tab.event_running:
        return False
        # Lock event until it's finished
    self.base_tab.result_folder_button.config(state="disabled")
    self.base_tab.generate_bdd_button.config(state="disabled")
    self.base_tab.open_button.config(state="disabled")
    self.base_tab.event_running = True
    print(
        "-----------------------------------------------------------------------------"
        "-------------------------------"
    )
    print("\nScript launched : Compare tests\n")
    # initialization
    (
        vivaldi_campaign,
        suite_bdd,
        test_py,
        csv_file_check_if_tests_exist,
        path_of_results,
    ) = get_info_from_conf_comp(conf)

    # Creating actual results folder
    time_now = datetime.now()
    campaign_name = vivaldi_campaign.split("/")[-1]
    path_of_time_folder = (
        path_of_results + "/" + str(time_now)[:19] + "_" + campaign_name
    )
    os.makedirs(path_of_time_folder)

    vivaldi_campaign = self.base_tab.foldername.get()
    print("Vivaldi campaign used :\n" + vivaldi_campaign + "\n")
    path_of_vivaldi_tests = vivaldi_campaign + "/TestSuites/"
    if os.path.exists(path_of_vivaldi_tests):
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
                if (
                    os.stat(path_of_time_folder + csv_file_check_if_tests_exist).st_size
                    == 0
                ):
                    shutil.rmtree(path_of_time_folder)
                messagebox.showinfo(
                    "Success !",
                    "All tests exist and their steps are matched",
                )
            else:
                print("One or many tests aren't good. Check CSV file")
                if messagebox.askyesno(
                    "Error", "One or many tests aren't good. Check CSV file"
                ):
                    os.system('xdg-open "%s"' % path_of_time_folder)

    else:
        print("\nInvalid test campaign\nPlease select a valid test campaign\n")
        messagebox.showerror(
            "Error", "\nInvalid test campaign\nPlease select a valid test campaign\n"
        )
    self.base_tab.update()
    self.base_tab.update_idletasks()
    self.base_tab.generate_bdd_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.result_folder_button.config(bg="#ffc8dd", state="normal")
    self.base_tab.open_button.config(bg="#ffc8dd", state="normal")
    # Release event handler
    self.base_tab.event_running = False
    return


def move_row_from_tree1_to_tree2(tree1, tree2, item):
    values = tree1.item(item)['values']
    tags = tree1.item(item)['tags']
    tree1.delete(item)
    tree2.insert('', 'end', values=values, tags=tags)


def open_result_folder(root, result_folder):
    if root.base_tab.event_running:
        return False
    root.base_tab.event_running = True
    os.system('xdg-open "%s"' % result_folder)
    root.base_tab.update()
    root.base_tab.update_idletasks()
    root.base_tab.event_running = False
    return


# https://stackoverflow.com/questions/18517084/how-to-redirect-stdout-to-a-tkinter-text-widget
class RedirectStd(object):
    def __init__(self, widget):
        self.widget = widget

    def flush(self):
        pass

    def write(self, string):
        self.widget.configure(state="normal")
        self.widget.insert("end", string)
        self.widget.see("end")
        self.widget.configure(state="disabled")
        self.widget.update_idletasks()


class NewTk(Tk):
    def __init__(self):
        super(NewTk, self).__init__()
        """
        self.foldername = None
        self.version = None
        self.soft = None
        self.hard = None
        self.entry_dir = None
        self.entry_ver = None
        self.entry_soft = None
        self.entry_hard = None
        self.query_pop_up_text = None
        self.pop_up_box = None
        self.warning_label = None
        self.result_folder = None
        self.actual_results_folder = None
        self.list_of_vivaldi_test_folder_names = []
"""

def config_label_setup(root, vivaldi_campaign):
    root.base_tab.foldername = tk.StringVar()
    root.base_tab.version = tk.StringVar()
    root.base_tab.soft = tk.StringVar()
    root.base_tab.hard = tk.StringVar()
    root.exec_tab.counter_1 = tk.StringVar()
    root.exec_tab.counter_2 = tk.StringVar()
    root.exec_tab.number_of_selected_tests = 0
    root.exec_tab.number_of_selected_tests_executed = 0

    # Initial vivaldi campaign folder
    root.base_tab.foldername.set(vivaldi_campaign)
    # Initial version
    root.base_tab.version.set("version3.1")
    # Initial software environment
    root.base_tab.soft.set("Software Test Environment 1")
    # Initial hardware environment
    root.base_tab.hard.set("Hardware Test Environment 2")
    # Conf label frame
    lf1 = LabelFrame(root.base_tab, text="Conf", relief=RAISED, borderwidth=3, bg="#a2d2ff")
    # lf1.place(anchor=CENTER, rely=0.25, relx=0.25)
    lf1.grid(row=0, column=0, sticky="NSEW")
    configure_rows_columns(lf1, 1, 4, 1)

    # Vivaldi campaign label & entry
    vivaldi_campaign_label = LabelFrame(
        lf1, relief=RAISED, text="Vivaldi campaign", bg="#a2d2ff"
    )
    configure_rows_columns(vivaldi_campaign_label, 1, 2, 1)
    vivaldi_campaign_label.grid(column=0, row=0, sticky="NEWS")

    root.base_tab.entry_dir = Entry(
        vivaldi_campaign_label, textvariable=root.base_tab.foldername, state=DISABLED
    )
    root.base_tab.entry_dir.grid(column=0, row=0, sticky="NEWS")
    vivaldi_campaign_label.grid_columnconfigure(index=0, weight=9)
    lf1.grid_columnconfigure(index=0, weight=3)

    # Version label & entry
    version_under_test_label = LabelFrame(
        lf1, text="Version under test", relief=RAISED, bg="#a2d2ff"
    )
    configure_rows_columns(version_under_test_label, 1, 1, 1)
    version_under_test_label.grid(column=1, row=0, sticky="NSEW")

    root.base_tab.entry_ver = Entry(version_under_test_label, textvariable=root.base_tab.version)
    root.base_tab.entry_ver.grid(column=0, row=0, sticky="NSEW")

    # Software environment label & entry
    software_env_label = LabelFrame(
        lf1, text="Software environment", relief=RAISED, bg="#a2d2ff"
    )
    configure_rows_columns(software_env_label, 1, 1, 1)
    software_env_label.grid(column=2, row=0, sticky="NSEW")

    root.base_tab.entry_soft = Entry(software_env_label, textvariable=root.base_tab.soft)
    root.base_tab.entry_soft.grid(column=0, row=0, sticky="NSEW")

    # Hardware environment label & entry
    hardware_env_label = LabelFrame(
        lf1, text="Hardware environment", relief=RAISED, bg="#a2d2ff"
    )
    configure_rows_columns(hardware_env_label, 1, 1, 1)
    hardware_env_label.grid(column=3, row=0, sticky="NSEW")

    root.base_tab.entry_hard = Entry(hardware_env_label, textvariable=root.base_tab.hard)
    root.base_tab.entry_hard.grid(column=0, row=0, sticky="NSEW")
    # open button
    root.base_tab.open_button = Button(
        vivaldi_campaign_label,
        text="Open folder",
        command=lambda: select_files(root),
        bg="#ffc8dd",
        fg="#023047",
        relief=SUNKEN,
    )

    root.base_tab.open_button.grid(column=1, row=0, sticky="NEWS")


    # Lab 2 : exec

    # Vivaldi campaign label & entry
    root.exec_tab.exec_vivaldi_campaign_label = LabelFrame(
        root.exec_tab, relief=RAISED, text="Vivaldi campaign", bg="#a2d2ff"
    )
    configure_rows_columns(root.exec_tab.exec_vivaldi_campaign_label, 1, 4, 1)
    root.exec_tab.exec_vivaldi_campaign_label.grid(column=0, row=0, sticky="NEWS")

    root.exec_tab.entry_dir = Entry(
        root.exec_tab.exec_vivaldi_campaign_label, textvariable=root.base_tab.foldername, state=DISABLED
    )
    root.exec_tab.entry_dir.grid(column=0, row=0, sticky="EW", ipady=10, ipadx=10, columnspan=2)
    lf1.grid_columnconfigure(index=0, weight=3)

    # counter_1
    root.exec_tab.entry_counter_1 = Entry(
        root.exec_tab.exec_vivaldi_campaign_label, textvariable=root.exec_tab.counter_1, state=DISABLED
    )
    root.exec_tab.entry_counter_1.grid(column=2, row=0, sticky="EW", padx=10, pady=10)

    # counter_2
    root.exec_tab.counter_2.set("0/0")
    root.exec_tab.entry_counter_2 = Entry(
        root.exec_tab.exec_vivaldi_campaign_label, textvariable=root.exec_tab.counter_2, state=DISABLED
    )
    root.exec_tab.entry_counter_2.grid(column=3, row=0, sticky="EW", padx=10, pady=10)

    # Table with tests

    # Label frame for the table
    root.exec_tab.exec_tests_table = LabelFrame(
        root.exec_tab, relief=RAISED, text="Tests table", bg="#a2d2ff"
    )

    # Init scrollbar
    root.scrollbar = Scrollbar(root.exec_tab.exec_tests_table)

    configure_rows_columns(root.exec_tab.exec_vivaldi_campaign_label, 1, 1, 1)
    root.exec_tab.exec_tests_table.grid(column=0, row=1, sticky="NEWS", rowspan=3)
    root.exec_tab.exec_tests_table.grid_columnconfigure(index=0, weight=1)

    # Verification button
    root.exec_tab.verification_button = Button(
        root.exec_tab.exec_tests_table,
        text="Verify selected tests",
        command=lambda: verify_tests(root),
        bg="#ffc8dd",
        fg="#023047",
    )
    root.exec_tab.verification_button.grid(column=1, row=2, sticky="W")

    path_of_tests = vivaldi_campaign + "/TestSuites"

    root.number_of_executed_tests_in_campaign = 0
    list_of_test_names, list_of_test_status, list_of_vivaldi_folder_names, list_of_exec_time = get_treeview_values(path_of_tests, root)
    # updating counter_1
    root.exec_tab.counter_1.set(str(root.number_of_executed_tests_in_campaign) + "/" + str(len(list_of_vivaldi_folder_names)))

    # Setting up the treeview of tests
    configure_rows_columns(root.exec_tab.exec_tests_table, 4, 5, 1)
    root.exec_tab.tree = ttk.Treeview(root.exec_tab.exec_tests_table, yscrollcommand=root.scrollbar.set)
    # Define the row colors with a tag
    root.exec_tab.tree.tag_configure("PASS", background="#d4d700")
    root.exec_tab.tree.tag_configure("FAIL", background="orange")
    root.exec_tab.tree.tag_configure("ONGOING", background="yellow")
    root.exec_tab.tree.tag_configure("ERROR", background="RED")
    root.exec_tab.tree['columns'] = ('Test ID', 'Test Name', 'Execution Time', 'Status')

    root.exec_tab.tree.column("#0", width=0, stretch=NO)
    root.exec_tab.tree.column("Test ID", anchor=CENTER, width=80)
    root.exec_tab.tree.column("Test Name", anchor=CENTER, width=80)
    root.exec_tab.tree.column("Execution Time", anchor=CENTER, width=80)
    root.exec_tab.tree.column("Status", anchor=CENTER, width=80)

    root.exec_tab.tree.heading("#0", text="", anchor=CENTER)
    root.exec_tab.tree.heading("Test ID", text="Test ID", anchor=CENTER)
    root.exec_tab.tree.heading("Test Name", text="Test Name", anchor=CENTER)
    root.exec_tab.tree.heading("Execution Time", text="Execution Time", anchor=CENTER)
    root.exec_tab.tree.heading("Status", text="Status", anchor=CENTER)
    for i in range(len(list_of_vivaldi_folder_names)):
        if list_of_test_status[i] == "PASS":
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',tag="PASS",
                                      values=(
                                          list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                          list_of_test_status[i]))
        elif list_of_test_status[i] == "FAIL":
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',tag="FAIL",
                                      values=(
                                          list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i],
                                          list_of_test_status[i]))
        else:
            root.exec_tab.tree.insert(parent='', index='end', iid=i, text='',
                                      values=(
                                      list_of_vivaldi_folder_names[i], list_of_test_names[i], list_of_exec_time[i], list_of_test_status[i]))
    root.exec_tab.tree.grid(column=2, row=1, columnspan=3, sticky="NEWS", padx=10)

    # Setting up the treeview of selected tests
    root.exec_tab.tree_of_selected_tests = ttk.Treeview(root.exec_tab.exec_tests_table, yscrollcommand=root.scrollbar.set)
    # Define the row colors with a tag
    root.exec_tab.tree_of_selected_tests.tag_configure("PASS", background="#d4d700")
    root.exec_tab.tree_of_selected_tests.tag_configure("FAIL", background="orange")
    root.exec_tab.tree_of_selected_tests.tag_configure("ONGOING", background="yellow")
    root.exec_tab.tree_of_selected_tests.tag_configure("ERROR", background="RED")
    root.exec_tab.tree_of_selected_tests['columns'] = ('Test ID', 'Test Name', 'Execution Time', 'Status')

    root.exec_tab.tree_of_selected_tests.column("#0", width=0, stretch=NO)
    root.exec_tab.tree_of_selected_tests.column("Test ID", anchor=CENTER, width=80)
    root.exec_tab.tree_of_selected_tests.column("Test Name", anchor=CENTER, width=80)
    root.exec_tab.tree_of_selected_tests.column("Execution Time", anchor=CENTER, width=80)
    root.exec_tab.tree_of_selected_tests.column("Status", anchor=CENTER, width=80)

    root.exec_tab.tree_of_selected_tests.heading("#0", text="", anchor=CENTER)
    root.exec_tab.tree_of_selected_tests.heading("Test ID", text="Test ID", anchor=CENTER)
    root.exec_tab.tree_of_selected_tests.heading("Test Name", text="Test Name", anchor=CENTER)
    root.exec_tab.tree_of_selected_tests.heading("Execution Time", text="Execution Time", anchor=CENTER)
    root.exec_tab.tree_of_selected_tests.heading("Status", text="Status", anchor=CENTER)

    root.exec_tab.tree_of_selected_tests.grid(column=2, row=0, columnspan=3, sticky="NEWS", padx=10)

# function to move an item up
def move_up(root):
    selected_item = root.exec_tab.tree_of_selected_tests.selection()
    if not selected_item:
        return
    selected_item = selected_item[0]
    prev_item = root.exec_tab.tree_of_selected_tests.prev(selected_item)
    if prev_item:
        prev_index = root.exec_tab.tree_of_selected_tests.index(prev_item)
        root.exec_tab.tree_of_selected_tests.move(selected_item, "", prev_index)

# function to move an item down
def move_down(root):
    selected_item = root.exec_tab.tree_of_selected_tests.selection()
    if not selected_item:
        return
    selected_item = selected_item[0]
    next_item = root.exec_tab.tree_of_selected_tests.next(selected_item)
    if next_item:
        next_index = root.exec_tab.tree_of_selected_tests.index(next_item)
        root.exec_tab.tree_of_selected_tests.move(selected_item, "", next_index)
        next_item = root.exec_tab.tree_of_selected_tests.next(selected_item)

def checklist(root):
    # Checklist
    root.checked_tests = []
    def reset_select_all(event, test_name,i):
        position_of_placement = 0
        root.base_tab.select_all.set(0)

        # If test is unchecked
        if not root.exec_tab.exec_tests_table.list_of_int_var[i].get():
            # decrementing number of selected tests
            root.exec_tab.number_of_selected_tests -= 1
            items = root.exec_tab.tree_of_selected_tests.get_children()
            for item in items:
                item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
                status = root.exec_tab.tree_of_selected_tests.item(item)["values"][3]
                if test_name in item_text:
                    # Updating counter_2
                    if status == "PASS" or status == "FAIL":
                        root.exec_tab.number_of_selected_tests_executed -= 1

                    move_row_from_tree1_to_tree2(root.exec_tab.tree_of_selected_tests, root.exec_tab.tree,
                                                 item)


        else:
            # incrementing number of selected tests
            root.exec_tab.number_of_selected_tests += 1
            # Search for test in treeview
            items = root.exec_tab.tree.get_children()
            for item in items:
                item_text = root.exec_tab.tree.item(item)["values"][0]
                status = root.exec_tab.tree.item(item)["values"][3]
                if test_name in item_text:
                    # Updating counter_2
                    if status == "PASS" or status == "FAIL":
                        root.exec_tab.number_of_selected_tests_executed += 1
                    # move the item to the top
                    move_row_from_tree1_to_tree2(root.exec_tab.tree, root.exec_tab.tree_of_selected_tests, item)
        root.exec_tab.counter_2.set(str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))


    root.exec_tab.exec_tests_table.tests_confirmed = IntVar()
    root.exec_tab.exec_tests_table.list_of_int_var = []


    number_of_tabs = 100 * "\t"
    path_of_tests = root.base_tab.foldername.get() + "/TestSuites"
    tempo_list = [x for x in os.listdir(path_of_tests) if x[0:3] == "tst"]
    tempo_list.sort(key=natural_keys)
    root.base_tab.list_of_vivaldi_test_folder_names = tempo_list

    # Init list of variables of checkbox
    for i in range(len(root.base_tab.list_of_vivaldi_test_folder_names)):
        x = IntVar()
        root.exec_tab.exec_tests_table.list_of_int_var.append(x)

    checklist = Text(root.exec_tab.exec_tests_table, width=40)
    checklist.grid(sticky="NS", column=0, row=0, rowspan=2, columnspan=2, ipadx=20)


    # Init scrollbar

    root.scrollbar.grid(row=0, column=5, sticky="NS")

    for i in range(len(root.base_tab.list_of_vivaldi_test_folder_names)):
        i_checkbutton = Checkbutton(
            checklist,
            #text='',
            text=root.base_tab.list_of_vivaldi_test_folder_names[i] + number_of_tabs,
            variable=root.exec_tab.exec_tests_table.list_of_int_var[i],
            command= lambda  e = root.base_tab.list_of_vivaldi_test_folder_names[i], i=i: reset_select_all(e,e,i),
            bg="white",
            relief=GROOVE,
        )

        i_checkbutton.bind('<MouseWheel>', lambda event: text.yview_scroll(int(-1 * (event.delta / 120)), "units"))
        checklist.window_create("end", window=i_checkbutton)
        checklist.insert("end", "\n")

    checklist.config(yscrollcommand=root.scrollbar.set)

    def viewall(*args):
        checklist.yview(*args)
        root.exec_tab.tree.yview(*args)


    root.scrollbar.config(command=viewall)

    # disable widget so user can't insert text
    checklist.configure(state=DISABLED)

def script_label_setup(root, result_folder):
    # storing conf in root variable
    root.conf = sys.argv[1]
    lf2 = LabelFrame(root.base_tab, text="Scripts", relief=RAISED, borderwidth=3, bg="#e9c46a")
    # lf2.place(anchor=CENTER, rely=0.25, relx=0.75)
    lf2.grid(row=1, column=0, sticky="NSEW")
    root.base_tab.generate_bdd_button = Button(
        lf2,
        text="Generate BDD tests",
        command=lambda: generate_bdd(root, sys.argv[1]),
        bg="#ffc8dd",
        fg="#023047",
    )
    root.base_tab.generate_bdd_button.grid(column=0, row=0, sticky="NSEW")

    configure_rows_columns(root.exec_tab, 4, 1, 1)

    Button(
        root.exec_tab.exec_tests_table, text="Normal execution", command=lambda: confirm_tests(root), bg="#e9c46a"
    ).grid(
        row=2,
        column=4,
        sticky="NSEW",
        pady=5,
        padx=10,
    )

    Button(
        root.exec_tab.exec_tests_table, text="Move up", command=lambda: move_up(root), bg="#e9c46a"
    ).grid(
        row=2,
        column=2,
        sticky="NSEW",
        pady=5,
        padx=10
    )

    Button(
        root.exec_tab.exec_tests_table,
        text="Randomize",
        command=lambda: confirm_random_tests(root),
        bg="#e9c46a"
    ).grid(
        row=2,
        column=3,
        sticky="NSEW",
        pady=5,
        padx=10
    )

    Button(
        root.exec_tab.exec_tests_table,
        text="Move down",
        command=lambda: move_down(root),
        bg="#e9c46a"
    ).grid(
        row=3,
        column=2,
        sticky="NSEW",
        pady=0,
        padx=10
    )

    root.base_tab.select_all = IntVar()

    def select_all_checked():
        if root.base_tab.select_all.get() == 1:
            # updating counter
            root.exec_tab.number_of_selected_tests_executed = root.number_of_executed_tests_in_campaign
            root.exec_tab.number_of_selected_tests = len(root.exec_tab.exec_tests_table.list_of_int_var)

            for k in range(len(root.base_tab.list_of_vivaldi_test_folder_names)):
                root.exec_tab.exec_tests_table.list_of_int_var[k].set(1)
                items = root.exec_tab.tree.get_children()
                for item in items:
                    item_text = root.exec_tab.tree.item(item)["values"][0]
                    if root.base_tab.list_of_vivaldi_test_folder_names[k] in item_text:
                        # move the item to the top
                        move_row_from_tree1_to_tree2(root.exec_tab.tree, root.exec_tab.tree_of_selected_tests, item)
        else:
            # updating counter
            root.exec_tab.number_of_selected_tests_executed = 0
            root.exec_tab.number_of_selected_tests = 0

            for k in range(len(root.base_tab.list_of_vivaldi_test_folder_names)):
                root.exec_tab.exec_tests_table.list_of_int_var[k].set(0)
                items = root.exec_tab.tree_of_selected_tests.get_children()
                for item in items:
                    item_text = root.exec_tab.tree_of_selected_tests.item(item)["values"][0]
                    if root.base_tab.list_of_vivaldi_test_folder_names[k] in item_text:
                        # move the item to the top

                        move_row_from_tree1_to_tree2( root.exec_tab.tree_of_selected_tests,root.exec_tab.tree, item)
        # updating counter
        root.exec_tab.counter_2.set(
            str(root.exec_tab.number_of_selected_tests_executed) + "/" + str(root.exec_tab.number_of_selected_tests))
    Checkbutton(
        root.exec_tab.exec_tests_table,
        text="Select All",
        variable=root.base_tab.select_all,
        command=select_all_checked,
        bg="#a2d2ff"
    ).grid(
        row=2,
        column=0,
        sticky="E",
        padx=10
    )

    checklist(root)

    root.base_tab.compare_tests_button = Button(
        lf2,
        text="Compare tests",
        command=lambda: compare_tests(root, sys.argv[1]),
        bg="#ffc8dd",
        fg="#023047",
    )
    root.base_tab.compare_tests_button.grid(column=1, row=0, sticky="NSEW")

    root.base_tab.event_running = False
    root.base_tab.result_folder_button = Button(
        lf2,
        text="Show results",
        command=lambda: open_result_folder(root, result_folder),
        bg="#ffc8dd",
        fg="#023047",
    )
    root.base_tab.result_folder_button.grid(column=2, row=0, sticky="NSEW")

    configure_rows_columns(lf2, 1, 3, 1)


def terminal_label_setup(root):
    tlog = Text(root, wrap="word", relief=RAISED, borderwidth=3, state="disabled")
    # tlog.configure(height=15, width=150)
    # tlog.place(anchor="s", rely=1, relx=0.5)
    tlog.grid(row=2, column=0, sticky="NEWS")
    sys.stdout = RedirectStd(tlog)
    sys.stderr = RedirectStd(tlog)


def configure_rows_columns(root, row_number, column_number, weight):
    for i in range(row_number):
        root.grid_rowconfigure(index=i, weight=weight)
    for j in range(column_number):
        root.grid_columnconfigure(index=j, weight=weight)


# Continue here
class Table:

    def __init__(self, root, total_rows, total_columns):
        # Make a list inside the table class
        # : self.list_of_tests[] ...
        self.list_of_entries = []
        # code for creating table
        for i in range(total_rows):
            for j in range(total_columns):
                self.e = Entry(root.exec_tab.exec_tests_table, width=20, fg='blue',
                               font=('Arial', 16, 'bold'))
                self.list_of_entries.append(self.e)
                self.e.grid(row=i, column=j)
                self.e.insert(END, root.list_of_vivaldi_test_folder_names[i])
    # If the application is already destroyed skip
    def __del__(self):
        for elem in self.list_of_entries:
            try:
                elem.destroy()
            except:
                pass
        print("Table destroyed")

def main():
    # create the root window
    # root = tk.Tk()
    root = NewTk()
    root.title("Auto Execute and Generate tests - IHM")
    root.geometry("1100x700")
    root.event_running = False
    root.number_of_executed_tests_in_campaign = 0
    # Initializing Base tab and Exec tab
    tabControl = ttk.Notebook(root)
    root.base_tab = ttk.Frame(tabControl)
    root.exec_tab = ttk.Frame(tabControl)

    tabControl.add(root.base_tab, text = 'Base')
    tabControl.add(root.exec_tab, text = 'Exec')

    tabControl.pack(expand = 1, fill = "both")

    root.base_tab.vivaldi_campaign = get_vivaldi_campaign(sys.argv[1])
    root.base_tab.result_folder = get_result_folder(sys.argv[1])
    root.base_tab.test_folder = get_test_folder(sys.argv[1])
    # noinspection PyTypeChecker
    config_label_setup(root, root.base_tab.vivaldi_campaign)
    # noinspection PyTypeChecker
    script_label_setup(root, root.base_tab.result_folder)
    terminal_label_setup(root.base_tab)
    # Configure rows and columns
    configure_rows_columns(root.base_tab, 3, 1, 1)
    # Init TLOG size
    root.base_tab.grid_rowconfigure(index=2, weight=5)

    root.mainloop()


if __name__ == "__main__":
    main()
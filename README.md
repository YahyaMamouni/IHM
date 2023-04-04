
# Prerequisites

## Installation
Installation of `Squish`:

    Requires the following file: `squish-7.0.0-qt62x-linux64.run`
    - Double click on the installer and proceed to install Squish

Installation of `poetry`:

    - `pip install --user poetry`

Installation of our dependencies in the poetry virtualenv:

    At the root of the project (containing the `pyproject.toml` file)
    - `poetry install`

Installation of `pre-commit`:

    - `pip install pre-commit`
    - `pre-commit autoupdate`

Installation of `Pycharm`:

    Requires the following file: `pycharm-community-2022.1.1.tar.gz`
    - sudo tar xzf pycharm-community-2022.1.1.tar.gz -C /opt/


## Configuration

### Use poetry and get the location of Black & flake8
    In the project folder containing the `pyproject.toml` file
    - `poetry shell`
    - `which black`
    - `which flake8`

### Configuration Pycharm
    Create a desktop entry:
    - Launch Pycharm `sh /opt/pycharm-community-2022.1.1/bin/pycharm.sh`
    - From the Tools menu (bottom left), select `Create Desktop Entry...`

    Integration of `Black`
    - File -> Settings -> Tools -> External Tools
    - Click the + icon to add a new external tools:
        Name : Black
        Program : <the location in the poetry env>
    - Settings -> Keymap -> External Tools -> External Tools -> Black -> Add Keyboard Shortcut
    - Or run manually with Tools -> External Tools -> Black

    Integration of `flake8`
    - File -> Settings -> Tools -> External Tools
    - Click the + icon to add a new external tools:
        Name : flake8
        Program : <the location in the poetry env>
        Arguments: --config <projectPath>/.flake8
    - Settings -> Keymap -> External Tools -> External Tools -> Black -> Add Keyboard Shortcut
    - Or run manually with Tools -> External Tools -> flake8

### Configuration pre-commit
    At the root of the project (containing the .pre-commit-config.yaml file)
    `pre-commit install`

# Use of the interface : Auto Execute and Generate tests

## Launch the interface
    In order to launch the interface you can proceed in two ways:
    - Double click on the interface from the Desktop
    - Inside the project repository run `./ihm.sh`

## Configuration
    - The configuration in the interface is pre-filled from the conf file (ivvq/conf/conf)
    - Click on the "Open folder" button in order to change the Vivaldi campaign
    - Change the version under test, software environment and hardawre environment by modifying their entries

## Scripts
    The different scripts of automation are presented as buttons:
    - Click on "Generate BDD tests" to generate the BDD tests that are equivalent to the Vivaldi campaign chosen on the conf
    - Click on "Execute & Generate results" -> Select the tests you want to run -> Select the mode of execution (Normal or random). After this the tests will be executed on Squish and their results will be filled in the Vivaldi campaign
    - Click on "Compare tests" to compare Vivaldi tests with Squish tests
    - Click on "Show results" to open results folder

## Log box
    You can see the results of executions (Passed or failed) as well as the Vivaldi campaign chosen and the launched script.
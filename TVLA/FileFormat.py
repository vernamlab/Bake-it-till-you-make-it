from __future__ import annotations

import json
import os
import re
import shutil
from datetime import date

import numpy as np

# from Metrics import *

"""
File: FileFormat.py
Authors: Samuel Karkache (swkarkache@wpi.edu), Trey Marcantonio (tmmarcantonio@wpi.edu)
Date: 2024-28-02
Description: File Format API for side-channel analysis experiments.
"""


class FileParent:
    def __init__(self, name: str, path: str, existing: bool = False):
        """
        Initialize FileFormatParent class. Creates the basic file structure including JSON metadata holder. If the file
        already exists it simply returns a reference to that file. To create a file named "ExampleFile" in your downloads
        directory set the name parameter to `name="ExampleFile` and the path to `path="C:\\users\\username\\\desktop`. The
        path needs to be structured as shown with double backslashes.
        :param name: The name of the file parent directory
        :type name: str
        :param path: The path to the file parent.
        :type path: str
        :param existing: whether the file already exists
        :type existing: bool
        :returns: None
        """
        if not existing:
            self.name = name
            if path[-1:] == "\\":
                self.path = path + name
            else:
                self.path = path + "\\" + name
            self.experiments_path = f"{self.path}\\Experiments"

            dir_created = False

            while not dir_created:
                try:
                    os.mkdir(self.path)
                    os.mkdir(self.experiments_path)
                    dir_created = True
                except FileExistsError:
                    if bool(re.match(r'.*-\d$', self.name)):
                        ver_num = int(self.name[len(self.name) - 1]) + 1
                        new_name = self.name[:-1] + str(ver_num)
                        new_path = self.path[:-1] + str(ver_num)
                    else:
                        new_name = self.name + "-1"
                        new_path = self.path + "-1"
                    self.name = new_name
                    self.path = new_path
                    self.experiments_path = f"{self.path}\\Experiments"

            self.json_data = {
                "fileName": sanitize_input(name),
                "metadata": {"dateCreated": date.today().strftime('%Y-%m-%d')},
                "path": self.path,
                "experiments": []
            }

            with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.json_data, json_file, indent=4)

            self.experiments = {}
            self.metadata = self.json_data['metadata']

        else:
            self.name = name
            if path[-1:] == "\\":
                path = path + name
            else:
                path = path + "\\" + name
            with open(f"{path}\\metadataHolder.json", 'r') as json_file:
                self.json_data = json.load(json_file)
            path_from_json = self.json_data["path"]

            # check if file has been moved
            if path_from_json != path:
                self.path = path
                self.json_data["path"] = path
                self.update_json()
            else:
                self.path = path_from_json

            self.experiments_path = f"{self.path}\\Experiments"
            self.experiments = {}
            self.metadata = self.json_data["metadata"]

            for experiment in self.json_data["experiments"]:
                if os.path.exists(self.path + experiment["path"]):
                    self.add_experiment_internal(exp_name=experiment.get('name'), existing=True,
                                                 index=experiment.get('index'),
                                                 experiment=experiment)
                else:
                    for experiment_json in self.json_data["experiments"]:
                        if experiment_json["name"] == experiment["name"]:
                            self.json_data["experiments"].remove(experiment_json)

                    with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                        json.dump(self.json_data, json_file, indent=4)

    def update_json(self) -> None:
        with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
            json.dump(self.json_data, json_file, indent=4)

    def update_metadata(self, key: str, value: any) -> None:
        """
        Update file JSON metadata with key-value pair
        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON
        :type value: any
        :returns: None
        """
        key = sanitize_input(key)
        self.metadata[key] = value
        self.update_json()

    def read_metadata(self) -> dict:
        """
        Read JSON metadata from file
        :returns: The metadata dictionary for the FileParent object
        :rtype: dict
        """
        return self.metadata

    def add_experiment(self, name: str) -> 'Experiment':
        """
        Adds a new experiment to the FileParent object
        :param name: The desired name of the new experiment
        :type name: str
        :returns: The newly created Experiment object
        :rtype: Experiment
        """
        return self.add_experiment_internal(name, existing=False, index=0, experiment=None)

    def add_experiment_internal(self, exp_name: str, existing: bool = False, index: int = 0,
                                experiment: dict = None) -> 'Experiment':
        """
        Internal Function for adding experiments used when getting a reference to an existing file. Call add_experiment
        to add a new experiment instead of this.
        """
        if experiment is None:
            experiment = {}

        exp_name = sanitize_input(exp_name)
        exp_path = f'\\Experiments\\{exp_name}'

        if not existing:
            dir_created = False
            while not dir_created:
                try:
                    os.mkdir(self.path + exp_path)
                    os.mkdir(f"{self.path + exp_path}\\visualization")
                    dir_created = True
                except FileExistsError:
                    if bool(re.match(r'.*-\d$', exp_name)):
                        ver_num = int(exp_name[len(exp_name) - 1]) + 1
                        new_name = exp_name[:-1] + str(ver_num)
                        new_path = exp_path[:-1] + str(ver_num)
                    else:
                        new_name = exp_name + "-1"
                        new_path = exp_path + "-1"
                    exp_name = new_name
                    exp_path = new_path

            json_to_save = {
                "name": exp_name,
                "path": exp_path,
                "metadata": {},
                "datasets": [],
            }

            self.json_data["experiments"].append(json_to_save)
            idx = len(self.json_data["experiments"]) - 1
            self.json_data["experiments"][idx]["index"] = idx
            self.experiments[exp_name] = Experiment(exp_name, exp_path, self, existing=False, index=idx)
            self.update_json()

        else:
            self.experiments[exp_name] = (
                Experiment(exp_name, exp_path, self, existing=True, index=index, experiment=experiment))

        return self.experiments[exp_name]

    def get_experiment(self, experiment_name: str) -> 'Experiment':
        """
        Get an existing experiment from the FileParent.
        :param experiment_name: The name of the requested experiment
        :type experiment_name: str
        :returns: The requested experiment. None if it does not exist.
        :rtype: Experiment. None if not found.
        """
        experiment_name = sanitize_input(experiment_name)
        return self.experiments[experiment_name]

    def delete_file(self) -> None:
        """
        Deletes the entire file. Confirmation required.
        :returns: None
        """
        res = sanitize_input(
            input("You are about to delete file {}. Do you want to proceed? [Y/N]: ".format(self.name)))

        if res == "y" or res == "yes":
            print("Deleting file {}".format(self.name))
            shutil.rmtree(self.path)
        else:
            print("Deletion of file {} cancelled.".format(self.name))

    def delete_experiment(self, experiment_name: str) -> None:
        """
        Deletes an experiment and all of its datasets from a FileParent. Confirmation Required.
        :param experiment_name: The name of the experiment
        :type experiment_name: str
        :returns: None
        """
        experiment_name = sanitize_input(experiment_name)
        res = sanitize_input(input(
            "You are about to delete {} in file {}. Do you want to proceed? [Y/N]: ".format(experiment_name,
                                                                                            self.name)))

        if res == "y" or res == "yes":
            print("Deleting experiment {}".format(experiment_name))

            shutil.rmtree(self.path + self.experiments[experiment_name].path)
            self.experiments.pop(experiment_name)
            for experiment_json in self.json_data["experiments"]:
                if experiment_json["name"] == experiment_name:
                    self.json_data["experiments"].remove(experiment_json)

            with open(f"{self.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.json_data, json_file, indent=4)
        else:
            print("Deletion of experiment {} cancelled.".format(experiment_name))

    def query_experiments_with_metadata(self, key: str, value: any, regex: bool = False) -> list['Experiment']:
        """
        Query all experiments in the FileParent object based on exact metadata key-value pair or using regular expressions.
        :param key: The key to be queried
        :type key: str
        :param value: The value to be queried. Supply a regular expression if the `regex` parameter is set to true. Supplying
                        a value of "*" will return all experiments with the `key` specified in the key parameter.
        :type value: any
        :returns: A list of queried experiments
        :rtype: list['Experiment']
        """
        experiments = []

        for exp in self.experiments.values():
            try:
                res = exp.metadata[key]
                if not regex:
                    if value == res or value == "*":
                        experiments.append(exp)
                else:
                    if bool(re.match(value, res)):
                        experiments.append(exp)
            except KeyError:
                continue
        return experiments


class Experiment:
    def __init__(self, name: str, path: str, file_format_parent: FileParent, existing: bool = False, index: int = 0,
                 experiment: dict = None):
        """
        Creates an Experiment object. Do not call this constructor. Please use `FileParent.add_experiment()` to
        create a new Experiment object. DO NOT USE.
        """

        if experiment is None:
            experiment = {}

        name = sanitize_input(name)

        if not existing:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = {}
            self.fileFormatParent = file_format_parent
            self.experimentIndex = index

        else:
            self.name = name
            self.path = path
            self.dataset = {}
            self.metadata = experiment["metadata"]
            self.fileFormatParent = file_format_parent
            self.experimentIndex = index

            for dataset in experiment["datasets"]:
                if os.path.exists(self.fileFormatParent.path + self.path + dataset["path"]):
                    self.add_dataset_internal(dataset["name"], existing=True, dataset=dataset)
                else:
                    for experiment_json in self.fileFormatParent.json_data["experiments"]:
                        if experiment_json["name"] == self.name:

                            for _dataset in experiment_json["datasets"]:
                                if dataset["name"] == _dataset["name"]:
                                    try:
                                        experiment_json["datasets"].remove(dataset)
                                    except ValueError:
                                        continue

                    with open(f"{self.fileFormatParent.path}\\metadataHolder.json", 'w') as json_file:
                        json.dump(self.fileFormatParent.json_data, json_file, indent=4)

    def update_metadata(self, key: str, value: any) -> None:
        """
        Update the experiment metadata using a new key value pair.
        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON.
        :type value: any
        :returns: None
        """
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.json_data["experiments"][self.experimentIndex]["metadata"][key] = value
        self.fileFormatParent.update_json()

    def read_metadata(self) -> dict:
        """
        Reads experiment metadata
        :returns: The experiment's metadata dictionary
        :rtype: dict
        """
        return self.metadata

    def add_dataset(self, name: str, data_to_add: np.ndarray, datatype: any) -> 'Dataset':
        """
        Adds a new Dataset to a given Experiment
        :param name: The desired name of the new dataset
        :type name: str
        :param data_to_add: The NumPy array of data to be added to the new dataset
        :type data_to_add: np.ndarray
        :param datatype: The datatype of the dataset
        :type datatype: any
        :returns: The newly created Dataset object
        :rtype: Dataset
        """
        dataset = self.add_dataset_internal(name, existing=False, dataset=None)
        dataset.add_data(data_to_add, datatype)
        return dataset

    def add_dataset_internal(self, name: str, existing: bool = False, dataset: dict = None) -> 'Dataset':
        """
        Internal Function for adding experiments used when getting a reference to an existing file. Call add_experiment
        to add a new experiment instead of this.
        """

        if dataset is None:
            dataset = {}

        name = sanitize_input(name)

        while name in self.dataset:
            if bool(re.match(r'.*-\d$', name)):
                ver_num = int(name[len(name) - 1]) + 1
                name = name[:-1] + str(ver_num)
            else:
                name = name + "-1"

        path = f'\\{name}.npy'

        if not existing:
            dataToAdd = {
                "name": name,
                "path": path,
                "metadata": {}
            }

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"].append(dataToAdd)
            index = len(self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"]) - 1

            self.fileFormatParent.json_data["experiments"][self.experimentIndex]["datasets"][index]['index'] = index
            self.fileFormatParent.update_json()

            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, index, existing=False)

        if existing:
            self.dataset[name] = Dataset(name, path, self.fileFormatParent, self, dataset["index"], existing=True,
                                         dataset=dataset)

        return self.dataset[name]

    def get_dataset(self, dataset_name: str) -> 'Dataset':
        """
        Get a dataset from a given experiment.
        :param dataset_name: The name of the requested dataset
        :type dataset_name: str
        :returns: The requested dataset. None if it is not found.
        :rtype: Dataset. None if not found.
        """
        dataset_name = sanitize_input(dataset_name)
        return self.dataset[dataset_name]

    def delete_dataset(self, dataset_name: str) -> None:
        """
        Deletes a dataset and all its contents. Confirmation required.
        :param dataset_name: The name of the dataset to be deleted
        :type dataset_name: str
        :returns: None
        """
        dataset_name = sanitize_input(dataset_name)
        res = sanitize_input(input(
            "You are about to delete {} in experiment {}. Do you want to proceed? [Y/N]: ".format(dataset_name,
                                                                                                  self.name)))
        if res == "y" or res == "yes":
            print("Deleting dataset {}".format(dataset_name))
            os.remove(self.fileFormatParent.path + self.path + "\\" + dataset_name + ".npy")
            self.dataset.pop(dataset_name)

            for experiment_json in self.fileFormatParent.json_data["experiments"]:
                if experiment_json["name"] == self.name:
                    for dataset in experiment_json["datasets"]:
                        if dataset["name"] == dataset_name:
                            experiment_json["datasets"].remove(dataset)

            with open(f"{self.fileFormatParent.path}\\metadataHolder.json", 'w') as json_file:
                json.dump(self.fileFormatParent.json_data, json_file, indent=4)

        else:
            print("Deletion of experiment {} cancelled.".format(dataset_name))

    def query_datasets_with_metadata(self, key: str, value: any, regex: bool = False) -> list['Dataset']:
        """
        Query all datasets in the Experiment object based on exact metadata key-value pair or using regular expressions.
        :param key: The key to be queried
        :type key: str
        :param value: The value to be queried. Supply a regular expression if the `regex` parameter is set to true. Supplying
                        a value of "*" will return all experiments with the `key` specified in the key parameter.
        :type value: any
        :returns: A list of queried datasets
        :rtype: list['Dataset']
        """
        datasets = []
        for dset in self.dataset.values():
            try:
                res = dset.metadata[key]
                if not regex:
                    if res == value or value == "*":
                        datasets.append(dset)
                else:
                    if bool(re.match(value, res)):
                        datasets.append(dset)
            except KeyError:
                continue
        return datasets

    def get_visualization_path(self) -> str:
        """
        Get the path to the visualization directory for the Experiment object.
        :returns: The visualization path of the experiment
        :rtype: str
        """
        return self.fileFormatParent.path + self.path + "\\" + "visualization" + "\\"

    def calculate_snr(self, traces_dataset: str, intermediate_fcn: Callable, *args: any,  visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:
        """
        Integrated signal-to-noise ratio metric.
        :param traces_dataset: The name of the traces dataset
        :type traces_dataset: str
        :param intermediate_fcn: A callback function that determines how the intermediate values for SNR labels are calculated.
        :type intermediate_fcn: Callable
        :param *args: Additonal datasets needed for the parameters of the intermediate_fnc.
        :type *args: any
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The SNR metric result
        :rtype: np.ndarray
        """

        traces_dataset = sanitize_input(traces_dataset)
        args = tuple(self.dataset[sanitize_input(x)].read_all() for x in args)

        traces = self.dataset[traces_dataset].read_all()
        labels = organize_snr_label(traces, intermediate_fcn, *args)

        if save_graph:
            path_created = False
            image_name = "{}_snr".format(traces_dataset)
            path = self.get_visualization_path() + image_name

            while not path_created:
                if os.path.exists(self.get_visualization_path() + image_name + ".png"):
                    if bool(re.match(r'.*-\d$', image_name)):
                        ver_num = int(image_name[len(image_name) - 1]) + 1
                        image_name = image_name[:-1] + str(ver_num)
                    else:
                        image_name = image_name + "-1"
                else:
                    path = self.get_visualization_path() + image_name + ".png"
                    path_created = True
        else:
            path = None

        snr = signal_to_noise_ratio(labels, visualize=visualize, visualization_path=path)

        if save_data:
            self.add_dataset("{}_snr".format(traces_dataset), snr, "float32")

        return snr

    def calculate_t_test(self, fixed_dataset: str, random_dataset: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> (np.ndarray, np.ndarray):
        """
        Integrated t-test metric.
        :param fixed_dataset: The name of the dataset containing the fixed trace set
        :type fixed_dataset: str
        :param random_dataset: The name of the dataset containing the random trace set
        :type random_dataset: str
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The t-test metric result
        :rtype: np.ndarray
        """

        rand = self.dataset[sanitize_input(random_dataset)].read_all()
        fixed = self.dataset[sanitize_input(fixed_dataset)].read_all()

        if save_graph:
            path_created_t = False
            t_name = f"t_test_{random_dataset}_{fixed_dataset}"
            t_path = self.get_visualization_path() + t_name

            while not path_created_t:
                if os.path.exists(self.get_visualization_path() + t_name + ".png"):
                    if bool(re.match(r'.*-\d$', t_name)):
                        ver_num = int(t_name[len(t_name) - 1]) + 1
                        t_name = t_name[:-1] + str(ver_num)
                    else:
                        t_name = t_name + "-1"
                else:
                    t_path = self.get_visualization_path() + t_name + ".png"
                    path_created_t = True

            path_created_max = False
            t_max_name = f"t_max_{random_dataset}_{fixed_dataset}"
            t_max_path = self.get_visualization_path() + t_max_name

            while not path_created_max:
                if os.path.exists(self.get_visualization_path() + t_max_name + ".png"):
                    if bool(re.match(r'.*-\d$', t_max_name)):
                        ver_num = int(t_max_name[len(t_max_name) - 1]) + 1
                        t_max_name = t_max_name[:-1] + str(ver_num)
                    else:
                        t_max_name = t_max_name + "-1"
                else:
                    t_max_path = self.get_visualization_path() + t_max_name + ".png"
                    path_created_max = True
            path = (t_path, t_max_path)
        else:
            path = None

        t, t_max = t_test_tvla(fixed, rand, visualize=visualize, visualization_paths=path)

        if save_data:
            self.add_dataset(f"t_test_{random_dataset}_{fixed_dataset}", t, datatype="float32")
            self.add_dataset(f"t_max_{random_dataset}_{fixed_dataset}", t_max, datatype="float32")

        return t, t_max

    def calculate_correlation(self, predicted_dataset_name: str, observed_dataset_name: str, visualize: bool = False, save_data: bool = False, save_graph: bool = False) -> np.ndarray:
        """
        Integrated correlation metric.
        :param predicted_dataset_name: The name of the dataset containing the predicted leakage
        :type predicted_dataset_name: str
        :param observed_dataset_name: The name of the dataset containing the observed leakage
        :type observed_dataset_name: str
        :param visualize: Whether to visualize the result or not
        :type visualize: bool
        :param save_data: Whether to save the metric result as a new dataset or not
        :type save_data: bool
        :param save_graph: Whether to save the visualization to the experiments visualization folder or not
        :type save_graph: bool
        :returns: The correlation metric result
        :rtype: np.ndarray
        """

        predicted = self.get_dataset(predicted_dataset_name).read_all()
        observed = self.get_dataset(observed_dataset_name).read_all()

        if save_graph:
            path_created = False
            image_name = f"corr_{predicted_dataset_name}_{observed_dataset_name}"
            path = self.get_visualization_path() + image_name

            while not path_created:
                if os.path.exists(self.get_visualization_path() + image_name + ".png"):
                    if bool(re.match(r'.*-\d$', image_name)):
                        ver_num = int(image_name[len(image_name) - 1]) + 1
                        image_name = image_name[:-1] + str(ver_num)
                    else:
                        image_name = image_name + "-1"
                else:
                    path = self.get_visualization_path() + image_name + ".png"
                    path_created = True
        else:
            path = None

        corr = pearson_correlation(predicted, observed, visualize=visualize, visualization_path=path)

        if save_data:
            self.add_dataset(f"corr_{predicted_dataset_name}_{observed_dataset_name}", corr, datatype="float32")

        return corr


class Dataset:
    def __init__(self, name: str, path: str, file_format_parent: FileParent, experiment_parent: Experiment, index: int,
                 existing: bool = False, dataset: dict = None):
        """
        Creates a Dataset object. Do not call this constructor. Please use `Experiment.add_dataset()` to
        create a new Dataset object. DO NOT USE.
        """
        if dataset is None:
            dataset = {}

        name = sanitize_input(name)
        if not existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = \
                self.fileFormatParent.json_data["experiments"][self.experimentParent.experimentIndex]["datasets"][
                    self.index]["metadata"]
            self.update_metadata("date_created", date.today().strftime('%Y-%m-%d'))

        if existing:
            self.name = name
            self.path = path
            self.index = index
            self.fileFormatParent = file_format_parent
            self.experimentParent = experiment_parent
            self.metadata = dataset["metadata"]

    def read_data(self, start: int, end: int) -> np.ndarray:
        """
        Read data from the dataset a specific start and end index.
        :param start: the start index of the data
        :type start: int
        :param end: the end index of the data
        :type end: int
        :returns: An NumPy array containing the requested data over the specified interval
        :rtype: np.ndarray
        """
        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[start:end]

    def read_all(self) -> np.ndarray:
        """
        Read all data from the dataset
        :returns: All data contained in the dataset
        :rtype: np.ndarray
        """

        data = np.load(self.fileFormatParent.path + self.experimentParent.path + self.path)
        return data[:]

    def add_data(self, data_to_add: np.ndarray, datatype: any) -> None:
        """
        Add data to an existing dataset
        :param data_to_add: The data to be added to the dataset as a NumPy array
        :type data_to_add: np.ndarray
        :param datatype: The datatype of the data being added
        :type datatype: any
        :returns: None
        """
        data_to_add = np.array(data_to_add, dtype=datatype)
        np.save(self.fileFormatParent.path + self.experimentParent.path + self.path, data_to_add)

    def update_metadata(self, key: str, value: any) -> None:
        """
        Update the dataset metadata using a new key value pair.
        :param key: The key of the metadata
        :type key: str
        :param value: The value of the metadata. Can be any datatype supported by JSON.
        :type value: any
        :returns: None
        """
        key = sanitize_input(key)
        self.metadata[key] = value
        self.fileFormatParent.update_json()


def sanitize_input(input_string: str) -> str:
    if type(input_string) is not str:
        raise ValueError("The input to this function must be of type string")
    return input_string.lower()

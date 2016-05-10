#!/usr/local/bin/python3
# coding=utf8
import yaml
import jsonpickle
import click
import json

from util.utils import get_documents, read_templates
from feature_training.trainer import Trainer
from feature_training.feature_extractor import FeatureExtractor
from features import AbstractFeature

@click.group()
def cli():
    pass


@click.command()
@click.option('-d', '--directory', type=click.STRING)
@click.option('-y', '--yaml_path', type=click.STRING)
@click.option('-m', '--model_path', type=click.STRING)
def create_model(directory, yaml_path, model_path):
    documents = get_documents(directory)
    apply_features_to_documents(documents, yaml_path)
    trainer = Trainer()
    templates = read_templates(yaml_path)
    trainer.train_model(documents, templates, model_path)


@click.option('-y', '--yaml_path', type=click.STRING)
@click.option('-d', '--directory', type=click.STRING)
@click.option('-o', '--output', type=click.STRING)
def create_feature_snapshot(yaml_path, directory, output):
    documents = get_documents(directory)
    apply_features_to_documents(documents, yaml_path)
    dump_to_json(documents, output)


@cli.command()
@click.option('-y', '--yaml_path', type=click.STRING)
@click.option('-d', '--directory', type=click.STRING)
def test_print_first_word(yaml_path, directory):
    documents = get_documents(directory)
    apply_features_to_documents(documents, yaml_path)
    print(documents[0].sentences[0].words[0].applied_features)


def apply_features_to_documents(documents, yaml_path):
    run_config = _read_run_config(yaml_path)
    feature_extractor = FeatureExtractor()
    feature_extractor.apply_features(run_config, documents)


def get_precomputed_features(feature_path):
    with open(feature_path) as pre_computed:
        return json.load(pre_computed)


def dump_to_json(documents, file_path):
    frozen = jsonpickle.encode(documents)
    with open(file_path, 'w') as outfile:
        outfile.write(frozen)


def load_documents():
    with open('data.txt', 'r') as outfile:
        content = outfile.read()
        print(jsonpickle.decode(content))


def _read_run_config(yaml_path):
    run_config = yaml.load(yaml_path)
    with open(yaml_path, 'r') as stream:
        run_config = yaml.load(stream)
    return run_config


def get_default_templates():
    return {'shape': [-1, 0, 1], 'word': [-1, 0, 1]}


def _get_all_features(self):
    all_classes = {}
    for sub_class in AbstractFeature.__subclasses__():
        all_classes[sub_class.__name__] = sub_class
    return all_classes


def _initialize_features_from_yaml(self, feature_dict):
    """
    Takes the feature specification from yaml and builds features
    from that. Each feature needs a priority and a name. The name is
    matched against the class name of the feature.
    """
    all_features = self._get_all_features()
    features = []
    for feature_name, values in feature_dict.items():
            feature_class = all_features[feature_name]
            if 'initializationProperties' in values:
                properties = values['initializationProperties']
                feature = feature_class(**properties)
            else:
                feature = feature_class()
            priority = values['priority']
            features.append((priority, feature))
    return features

cli.add_command(create_model)
cli.add_command(create_feature_snapshot)

if __name__ == '__main__':
    cli()

#!/usr/local/bin/python3
# coding=utf8
import click
import jsonpickle
import yaml

from evaluation.evaluator import Evaluator
from feature_training.feature_extractor import FeatureExtractor
from util.utils import get_documents, read_templates


@click.group()
def cli():
    pass


@click.command()
@click.option('-d', '--directory', type=click.STRING)
@click.option('-y', '--yaml_path', type=click.STRING)
@click.option('-m', '--model_path', type=click.STRING)
@click.option('-l', '--log_path', type=click.STRING)
def evaluate_model(directory, yaml_path, model_path, log_path):
    documents = get_documents(directory)
    apply_features(yaml_path, documents)
    evaluator = Evaluator()
    templates = read_templates(yaml_path)
    evaluator.test_model(model_path, documents, templates, log_path)


def apply_features(yaml_path, documents):
    with open(yaml_path, 'r') as stream:
        run_config = yaml.load(stream)
    feature_extractor = FeatureExtractor()
    feature_extractor.apply_features(run_config,  documents)


@cli.command()
@click.option('-f', '--first_run', type=click.STRING)
@click.option('-s', '--second_run', type=click.STRING)
def compare_runs(first_run, second_run):
    evaluator = Evaluator()
    with open(first_run, 'r') as infile:
        read = infile.read()
        first_log = jsonpickle.decode(read)
    with open(second_run, 'r') as infile:
        read = infile.read()
        second_log = jsonpickle.decode(read)
    evaluator.compare_output_files(first_log, second_log)


@cli.command()
@click.option('-l', '--log_dir', type=click.STRING, help='path to log')
def display_run(log_dir):
    with open(log_dir, 'r') as infile:
        read = infile.read()
        log = jsonpickle.decode(read)
        evaluator = Evaluator()
        evaluator.display_run(log)


@cli.command()
@click.option('-d', '--directory', type=click.STRING)
@click.option('-y', '--yaml_path', type=click.STRING)
@click.option('-c', '--chunk_count', type=click.INT)
def perform_cross_validation(directory, yaml_path, chunk_count):
    documents = get_documents(directory)
    apply_features(yaml_path, documents)
    evaluator = Evaluator()
    templates = read_templates(yaml_path)
    evaluator.perform_cross_validation(chunk_count, documents, templates)

cli.add_command(perform_cross_validation)
cli.add_command(evaluate_model)
cli.add_command(compare_runs)
cli.add_command(display_run)

cli()

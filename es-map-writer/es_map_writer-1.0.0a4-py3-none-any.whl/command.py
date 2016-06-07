import click
import os
from .writer import Writer


@click.command()
@click.option('--database-url', default=None, help='Postgres URI.')
@click.option('--file-path', help='Output file destination folder.')
@click.option('--table-name', help='Postgres table the mapping is being written for.')
@click.option('--index-name', default=None,
              help='Elasticsearch index name. Will default to the table name if blank.')
@click.option('--document-type', help='Elasticsearch document type.')
def cli(database_url, file_path, table_name, index_name, document_type):
    if not database_url:
        raise click.BadParameter('The --database-url cannot be blank.')
    click.echo('Writing map.')
    w = Writer(database_url)
    w.write_mapping(table_name=table_name, document_type=document_type,
                    path=file_path, index_name=index_name)

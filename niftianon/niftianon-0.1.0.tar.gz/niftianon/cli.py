from __future__ import absolute_import
import click
import niftianon.anonymiser


@click.command()
@click.argument('identifiable_image', type=click.Path(exists=True))
@click.argument('anonymised_image', type=click.Path(exists=False))
def anonymise(identifiable_image, anonymised_image):
    """Anonymise IDENTIFIABLE_IMAGE and save the result to ANONYMISED_IMAGE

    IDENTIFIABLE_IMAGE must be the path to a NIFTI or NIFTI_GZ format image
    ANONYMISED_IMAGE must be a path that does not currently exist
    """

    niftianon.anonymiser.anonymise(identifiable_image, anonymised_image)

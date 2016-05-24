import logging
import csv
from parrot.utils import traceback_in_one_line, make_dirs
from parrot.exceptions import (
    CSVExporterItemExportException, ExporterInitFunctionCallException
)

from .base import Exporter


logger = logging.getLogger(__name__)


class CSVExporter(Exporter):
    EXTENSION = 'csv'

    @property
    def extension_with_dot(self):
        return (
            '.' + self.EXTENSION if not self.EXTENSION.startswith('.')
            else self.EXTENSION
        )

    def _fix_extension(self, filename):
        if not filename.endswith(self.extension_with_dot):
            filename += self.extension_with_dot
        return filename

    def __init__(
        self, output_fn, columns,
        init_export_func=None, item_export_func=None, *,
        silent=True, encoding='utf-8', fix_extension=True
    ):
        """
        :param columns: список столбцов (порядок важен)
        :param silent:
        :return:
        """
        super().__init__(init_export_func, item_export_func, silent=silent)
        if fix_extension:
            output_fn = self._fix_extension(output_fn)
        self.output_fn = output_fn
        self.columns = columns
        self.encoding = encoding
        self.fix_extension = fix_extension

    def __call__(self, items):
        total = scs = err = 0
        try:
            init = self._init_export()
        except Exception as exc:
            custom_exc = ExporterInitFunctionCallException(
                self._init_export, exc, traceback_in_one_line()
            )
            self._raise_if_not_silent(custom_exc, logger)
            logger.warning(custom_exc)
            init = None

        make_dirs(self.output_fn)
        with open(self.output_fn, 'wt', encoding=self.encoding) as csv_file:
            csv_writer = csv.DictWriter(
                csv_file, lineterminator='\n', fieldnames=self.columns
            )
            csv_writer.writeheader()

            for item in items:
                total += 1
                try:
                    item = self._item_export(item, init)
                    csv_writer.writerow(item)
                except Exception as exc:
                    err += 1
                    custom_exc = CSVExporterItemExportException(
                        item, self.output_fn, exc, traceback_in_one_line()
                    )
                    self._raise_if_not_silent(exc, logger)
                    logger.warning(custom_exc)
                else:
                    scs += 1

        return total, scs, err

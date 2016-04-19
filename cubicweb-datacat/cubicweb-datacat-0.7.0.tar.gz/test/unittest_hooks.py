"""cubicweb-datacat unit tests for hooks"""

from datetime import datetime

from pytz import utc

from cubicweb.devtools.testlib import CubicWebTC

from utils import create_file, produce_file


def mediatypes_scheme(cnx, *concepts):
    """Build a "dummy" media-types concept scheme to satisfy hooks on
    distribution/file media type conformance.
    """
    scheme = cnx.create_entity(
        'ConceptScheme',
        cwuri=u'http://www.iana.org/assignments/media-types/media-types.xml')
    for concept in concepts:
        scheme.add_concept(concept)
    return scheme


class DataProcessWorkflowHooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'Test dataset', description=u'A dataset',
                                   in_catalog=cat)
            di = cnx.create_entity('Distribution', of_dataset=ds,
                                   access_url=u'http://www.example.org')
            cnx.commit()
            self.dataset_eid = ds.eid
            self.distribution_eid = di.eid

    def _setup_and_start_dataprocess(self, cnx, process_etype, scriptcode):
        inputfile = create_file(cnx, 'data',
                                file_distribution=self.distribution_eid)
        script = cnx.create_entity('Script',
                                   name=u'%s script' % process_etype)
        create_file(cnx, scriptcode, reverse_implemented_by=script.eid)
        with cnx.security_enabled(write=False):
            process = cnx.create_entity(process_etype,
                                        process_script=script)
            cnx.commit()
        process.cw_clear_all_caches()
        iprocess = process.cw_adapt_to('IDataProcess')
        self.assertEqual(process.in_state[0].name,
                         iprocess.state_name('initialized'))
        process.cw_set(process_input_file=inputfile)
        cnx.commit()
        process.cw_clear_all_caches()
        return process

    def test_data_process_autostart(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=script)
            with cnx.security_enabled(write=False):
                process = cnx.create_entity('DataValidationProcess',
                                            process_script=script)
                cnx.commit()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_initialized')
            inputfile = create_file(cnx, 'data',
                                    file_distribution=self.distribution_eid)
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_error')

    def test_data_process(self):
        with self.admin_access.repo_cnx() as cnx:
            for ptype in ('transformation', 'validation'):
                etype = 'Data' + ptype.capitalize() + 'Process'
                process = self._setup_and_start_dataprocess(cnx, etype, 'pass')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_completed')
                process.cw_delete()
                cnx.commit()
                process = self._setup_and_start_dataprocess(cnx, etype, '1/0')
                self.assertEqual(process.in_state[0].name,
                                 'wfs_dataprocess_error')

    def test_data_process_output(self):
        with self.admin_access.repo_cnx() as cnx:
            self._setup_and_start_dataprocess(
                cnx, 'DataTransformationProcess',
                open(self.datapath('cat.py')).read())
            rset = cnx.execute(
                'Any X WHERE EXISTS(X produced_by S)')
            self.assertEqual(len(rset), 1)
            stdout = rset.get_entity(0, 0)
            self.assertEqual(stdout.read(), 'data\n')

    def test_data_validation_process_validated_by(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=script)
            with cnx.security_enabled(write=False):
                process = cnx.create_entity('DataValidationProcess',
                                            process_script=script)
                cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    file_distribution=self.distribution_eid)
            # Triggers "start" transition.
            process.cw_set(process_input_file=inputfile)
            cnx.commit()
            process.cw_clear_all_caches()
            self.assertEqual(process.in_state[0].name,
                             'wfs_dataprocess_completed')
            validated = cnx.find('File', validated_by=process).one()
            self.assertEqual(validated, inputfile)

    def test_data_process_dependency(self):
        """Check data processes dependency"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, 'pass', reverse_implemented_by=vscript)
            with cnx.security_enabled(write=False):
                vprocess = cnx.create_entity('DataValidationProcess',
                                             process_script=vscript)
                cnx.commit()
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx,
                        ('import sys;'
                         'sys.stdout.write(open(sys.argv[1]).read())'),
                        reverse_implemented_by=tscript)
            with cnx.security_enabled(write=False):
                tprocess = cnx.create_entity('DataTransformationProcess',
                                             process_depends_on=vprocess,
                                             process_script=tscript)
                cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    file_distribution=self.distribution_eid)
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_completed'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_completed')
            rset = cnx.find('File', produced_by=tprocess)
            self.assertEqual(len(rset), 1, rset)
            output = rset.one()
            self.assertEqual(output.read(), inputfile.read())

    def test_data_process_dependency_validation_error(self):
        """Check data processes dependency: validation process error"""
        with self.admin_access.repo_cnx() as cnx:
            vscript = cnx.create_entity('Script', name=u'v')
            create_file(cnx, '1/0', reverse_implemented_by=vscript)
            with cnx.security_enabled(write=False):
                vprocess = cnx.create_entity('DataValidationProcess',
                                             process_script=vscript)
                cnx.commit()
            tscript = cnx.create_entity('Script', name=u't')
            create_file(cnx, 'import sys; print open(sys.argv[1]).read()',
                        reverse_implemented_by=tscript)
            with cnx.security_enabled(write=False):
                tprocess = cnx.create_entity('DataTransformationProcess',
                                             process_depends_on=vprocess,
                                             process_script=tscript)
                cnx.commit()
            inputfile = create_file(cnx, 'data',
                                    file_distribution=self.distribution_eid)
            # Triggers "start" transition.
            vprocess.cw_set(process_input_file=inputfile)
            tprocess.cw_set(process_input_file=inputfile)
            cnx.commit()
            vprocess.cw_clear_all_caches()
            tprocess.cw_clear_all_caches()
            assert vprocess.in_state[0].name == 'wfs_dataprocess_error'
            self.assertEqual(tprocess.in_state[0].name,
                             'wfs_dataprocess_initialized')


class ResourceFeedHooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'Test dataset', description=u'A dataset',
                                   in_catalog=cat)
            cnx.commit()
            self.dataset_eid = ds.eid

    def test_distribution_created(self):
        with self.admin_access.repo_cnx() as cnx:
            mediatypes_scheme(cnx, u'text/plain')
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=u'a/b/c',
                data_format=u'text/plain',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            self.assertTrue(resourcefeed.resourcefeed_distribution)
            dist = resourcefeed.resourcefeed_distribution[0]
            self.assertEqual(dist.distribution_media_type[0].label(), u'text/plain')
            self.assertEqual([x.eid for x in dist.of_dataset],
                             [self.dataset_eid])

    def test_resourcefeed_cwsource(self):
        with self.admin_access.repo_cnx() as cnx:
            resourcefeed = cnx.create_entity(
                'ResourceFeed', url=u'a/b/c',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            source = resourcefeed.resource_feed_source[0]
            self.assertEqual(source.url, resourcefeed.url)
            resourcefeed.cw_set(url=u'c/b/a')
            cnx.commit()
            source.cw_clear_all_caches()
            self.assertEqual(source.url, u'c/b/a')
            resourcefeed1 = cnx.create_entity(
                'ResourceFeed', url=u'c/b/a',
                resource_feed_of=self.dataset_eid)
            cnx.commit()
            self.assertEqual(resourcefeed1.resource_feed_source[0].eid,
                             source.eid)

    def test_linkto_dataset(self):
        with self.admin_access.repo_cnx() as cnx:
            inputfile = create_file(cnx, 'data')
            script = cnx.create_entity('Script', name=u'script')
            create_file(cnx, 'pass', reverse_implemented_by=script.eid)
            resourcefeed = cnx.create_entity('ResourceFeed', url=u'a/b/c',
                                             resource_feed_of=self.dataset_eid,
                                             transformation_script=script)
            cnx.commit()
            produce_file(cnx, resourcefeed, inputfile)
            rset = cnx.execute('Any X WHERE X file_distribution D, D eid %s' %
                               resourcefeed.resourcefeed_distribution[0].eid)
            self.assertEqual(len(rset), 1, rset)
            outdata = rset.get_entity(0, 0).read()
            self.assertEqual(outdata, 'plop')

    def test_file_replaced(self):
        with self.admin_access.repo_cnx() as cnx:
            script = cnx.create_entity('Script', name=u'script')
            create_file(cnx, 'pass', reverse_implemented_by=script.eid)
            resourcefeed = cnx.create_entity('ResourceFeed', url=u'a/b/c',
                                             resource_feed_of=self.dataset_eid,
                                             transformation_script=script)
            cnx.commit()
            outfile1 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data'))
            outfile2 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data 2'))
            outfile3 = produce_file(cnx, resourcefeed,
                                    create_file(cnx, 'data 3'))
            rset = cnx.execute('Any F1,F2 WHERE F1 replaces F2')
            self.assertEqual(rset.rowcount, 2)
            self.assertIn([outfile2.eid, outfile1.eid], rset.rows)
            self.assertIn([outfile3.eid, outfile2.eid], rset.rows)
            rset = cnx.execute(
                'Any X WHERE X file_distribution D, D eid %(d)s',
                {'d': resourcefeed.resourcefeed_distribution[0].eid})
            self.assertEqual(rset.rowcount, 1)
            self.assertEqual(rset[0][0], outfile3.eid)


class DatesHooksTC(CubicWebTC):

    def test_issued_modified(self):
        past = datetime(2008, 1, 4, 3, 4, 5, tzinfo=utc)
        future = datetime(3000, 1, 4, 3, 4, 5, tzinfo=utc)
        with self.admin_access.cnx() as cnx:
            catalog = cnx.create_entity(
                'DataCatalog', title=u'c', description=u'd', issued=past,
                catalog_publisher=cnx.create_entity('Agent', name=u'publisher'))
            dataset = cnx.create_entity(
                'Dataset', title=u'ds', description=u'A dataset',
                in_catalog=catalog)
            dist = cnx.create_entity(
                'Distribution', title=u'di', of_dataset=dataset,
                issued=future, modified=past)
            cnx.commit()
            self.assertEqual(catalog.issued, past)
            self.assertEqual(catalog.modified, past)
            self.assertGreater(dataset.issued, past)
            self.assertEqual(dataset.modified, dataset.issued)
            self.assertGreater(dataset.issued, past)
            self.assertEqual(dist.modified, past)
            self.assertEqual(dist.issued, future)
            dist.cw_set(access_url=u'http://example.org')
            cnx.commit()
            self.assertGreater(dist.modified, past)
            self.assertEqual(dist.issued, future)


class DistributionHooksTC(CubicWebTC):

    def test_accessurl(self):
        with self.admin_access.cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', identifier=u'ds', title=u'ds',
                                   description=u'A dataset', in_catalog=cat)
            dist_with_url = cnx.create_entity(
                'Distribution', of_dataset=ds, title=u'with',
                access_url=u'http://example.org')
            dist_without_url = cnx.create_entity(
                'Distribution', of_dataset=ds, title=u'without')
            cnx.commit()
            self.assertEqual(dist_with_url.access_url, u'http://example.org')
            self.assertEqual(dist_without_url.access_url,
                             dist_without_url.absolute_url())


class FileDistributionRelationHooksTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', identifier=u'ds', title=u'ds',
                                   description=u'A dataset', in_catalog=cat)
            self.distribution_eid = cnx.create_entity(
                'Distribution', of_dataset=ds, title=u'THE distr',
                description=u'one and only', access_url=u'http://example.org').eid
            cnx.commit()

    @staticmethod
    def create_file(cnx, **kwargs):
        """Simplified version of utils.create_file"""
        return create_file(cnx, data_name=u"foo.txt", data="xxx", **kwargs)

    def create_distribution_file(self, cnx, **kwargs):
        """Create a file link to self.distribution_eid"""
        return self.create_file(cnx, file_distribution=self.distribution_eid,
                                **kwargs)

    def test_update_file_of_distribution(self):
        with self.admin_access.repo_cnx() as cnx:
            file_v1 = self.create_distribution_file(cnx)
            cnx.commit()
            distr = cnx.find('Distribution', eid=self.distribution_eid).one()
            self.assertEqual(distr.reverse_file_distribution[0], file_v1)
            file_v2 = self.create_file(cnx, replaces=file_v1)
            cnx.commit()
            distr = cnx.find('Distribution', eid=self.distribution_eid).one()
            self.assertEqual(distr.reverse_file_distribution[0], file_v2)
            self.assertEqual(file_v2.replaces[0], file_v1)

    def test_update_distribution_on_create_filedistribution(self):
        with self.admin_access.repo_cnx() as cnx:
            mediatypes_scheme(cnx, u'text/csv')
            cnx.commit()
            distr = cnx.entity_from_eid(self.distribution_eid)
            self.assertIsNone(distr.byte_size)
            self.assertFalse(distr.distribution_format)
            self.assertFalse(distr.distribution_media_type)
            self.assertIsNone(distr.download_url)
            distr_file = self.create_distribution_file(cnx, data_format=u'text/csv')
            cnx.commit()
            self.assertEqual(distr.byte_size, distr_file.size())
            self.assertEqual(distr.distribution_media_type[0].label(), distr_file.data_format)
            self.assertEqual(distr.access_url,
                             distr_file.cw_adapt_to("IDownloadable").download_url())
            self.assertIsNone(distr.download_url)

    def test_update_distribution_on_create_and_on_update(self):
        """Test the value of issued and modified
            - when a file is added : issued ~= modified = time when the file is added
            - when a new file is added : issued ~= modified = time when the new file is added
            - when the last file is updated : issued = time when the file was added,
                                              modified = time when the file was updated
            - when an older file is updated : nothing change
        """
        with self.admin_access.repo_cnx() as cnx:
            distr = cnx.entity_from_eid(self.distribution_eid)
            file_v1 = self.create_distributionfile_and_check_date(cnx, distr)
            file_v2 = self.create_distributionfile_and_check_date(cnx, distr)
            self.update_file_and_check_date(cnx, distr, file_v2, current_file=True)
            self.update_file_and_check_date(cnx, distr, file_v1, current_file=False)

    def create_distributionfile_and_check_date(self, cnx, distr):
        before = distr.creation_date
        distr_file = self.create_distribution_file(cnx)
        cnx.commit()
        after = datetime.now(utc)
        distr.cw_clear_all_caches()
        for date in [distr.issued, distr.modified]:
            self.assertGreater(date, before)
            self.assertLess(date, after)
        return distr_file

    def update_file_and_check_date(self, cnx, distr, distr_file, current_file):
        issued_before, modified_before = distr.issued, distr.modified
        distr_file.cw_set(data_name=u'bar.txt')
        cnx.commit()
        distr.cw_clear_all_caches()
        self.assertEqual(distr.issued, issued_before)
        if current_file:
            self.assertGreater(distr.modified, modified_before)
        else:
            self.assertEqual(distr.modified, modified_before)

    def test_set_title_description(self):
        with self.admin_access.repo_cnx() as cnx:
            distr_file = self.create_distribution_file(cnx)
            self.assertEqual(distr_file.title, 'THE distr')
            self.assertEqual(distr_file.description, 'one and only')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

import unittest
from abc import abstractmethod
from copy import deepcopy

from baton._baton.baton_metadata_mappers import BatonDataObjectIrodsMetadataMapper, BatonCollectionIrodsMetadataMapper, \
    _BatonIrodsMetadataMapper
from baton.collections import IrodsMetadata
from baton.models import Collection, IrodsEntity
from baton.models import DataObject
from baton.tests._baton._helpers import NAMES, create_collection, create_data_object
from baton.tests._baton._settings import BATON_SETUP
from testwithbaton.api import TestWithBaton
from testwithbaton.helpers import SetupHelper


class _TestBatonIrodsEntityMetadataMapper(unittest.TestCase):
    """
    Tests for `_BatonIrodsMetadataMapper`.
    """
    def setUp(self):
        self.test_with_baton = TestWithBaton(baton_setup=BATON_SETUP)
        self.test_with_baton.setup()
        self.setup_helper = SetupHelper(self.test_with_baton.icommands_location)
        self.mapper = self.create_mapper()
        self.metadata = IrodsMetadata({"key_1": {"value_1", "value_2"}, "key_2": {"value_3"}})

    def tearDown(self):
        self.test_with_baton.tear_down()

    @abstractmethod
    def create_mapper(self) -> _BatonIrodsMetadataMapper:
        """
        Creates a mapper to test with.
        :return: the created mapper
        """

    @abstractmethod
    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> IrodsEntity:
        """
        Creates an iRODS entity to test with
        :param name: the name of the entity to create
        :param metadata: the metadata to give to the entity
        :return: the created entity
        """

    def test_get_all_with_no_paths(self):
        self.assertEqual(self.mapper.get_all([]), [])

    def test_get_all_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.get_all, "/invalid")

    def test_get_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_get_all_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertRaises(FileNotFoundError, self.mapper.get_all, [entity.path, "/invalid"])

    def test_get_all_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.assertEqual(self.mapper.get_all(paths), [entity.metadata for entity in entities])

    def test_add_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.add, "/invalid", self.metadata)

    def test_add_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.mapper.add(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_add_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.assertRaises(FileNotFoundError, self.mapper.add, [entity.path, "/invalid"], self.metadata)

    def test_add_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, IrodsMetadata()) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.add(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [self.metadata for entity in entities])

    def test_add_no_metadata(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.mapper.add(entity.path, IrodsMetadata())
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())

    def test_add_metadata_with_same_key(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        del self.metadata["key_1"]
        self.assertRaises(KeyError, self.mapper.add, entity.path, self.metadata)

    def test_set_with_no_paths(self):
        self.mapper.set([], self.metadata)

    def test_set_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.set, "/invalid", self.metadata)

    def test_set_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_set_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.assertRaises(FileNotFoundError, self.mapper.set, [entity.path, "/invalid"], self.metadata)

    def test_set_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, IrodsMetadata()) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.set(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [self.metadata for _ in entities])

    def test_set_with_existing_non_duplicate_metadata(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata({"another": {"value"}}))
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_set_with_and_when_existing_duplicate_metadata(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.set(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), self.metadata)

    def test_remove_with_no_paths(self):
        self.mapper.remove([], self.metadata)

    def test_remove_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.remove, "/invalid", self.metadata)

    def test_remove_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.remove(entity.path, self.metadata)
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())

    def test_remove_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertRaises(FileNotFoundError, self.mapper.remove, [entity.path, "/invalid"], self.metadata)

    def test_remove_entire_metadata_with_multiple_paths(self):
        entities = [self.create_irods_entity(name, self.metadata) for name in NAMES]
        paths = [entity.path for entity in entities]
        self.mapper.remove(paths, self.metadata)
        self.assertEqual(self.mapper.get_all(paths), [IrodsMetadata() for _ in paths])

    def test_remove__unset_metadata(self):
        entity = self.create_irods_entity(NAMES[0], IrodsMetadata())
        self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)

    def test_remove_partially_unset_metadata(self):
        partial_metadata = deepcopy(self.metadata)
        del partial_metadata["key_1"]
        entity = self.create_irods_entity(NAMES[0], partial_metadata)
        self.assertRaises(KeyError, self.mapper.remove, entity.path, self.metadata)

    def test_remove_subset_of_metadata(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        assert len(self.metadata) == 2
        partial_metadata_1 = deepcopy(self.metadata)
        del partial_metadata_1["key_1"]
        partial_metadata_2 = deepcopy(self.metadata)
        del partial_metadata_2["key_2"]
        self.mapper.remove(entity.path, partial_metadata_1)
        self.assertEqual(self.mapper.get_all(entity.path), partial_metadata_2)

    def test_remove_all_with_no_paths(self):
        self.mapper.remove_all([])

    def test_remove_all_with_single_path_that_is_invalid(self):
        self.assertRaises(FileNotFoundError, self.mapper.remove_all, "/invalid")

    def test_remove_all_with_single_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.remove_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())

    def test_remove_all_with_multiple_paths_including_an_invalid_path(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.assertRaises(FileNotFoundError, self.mapper.remove_all, [entity.path, "/invalid"])

    def test_remove_all_with_multiple_paths(self):
        entity = self.create_irods_entity(NAMES[0], self.metadata)
        self.mapper.remove_all(entity.path)
        self.assertEqual(self.mapper.get_all(entity.path), IrodsMetadata())


class TestBatonDataObjectMapper(_TestBatonIrodsEntityMetadataMapper):
    """
    Tests for `BatonDataObjectIrodsMetadataMapper`.
    """
    def create_mapper(self) -> BatonDataObjectIrodsMetadataMapper:
        return BatonDataObjectIrodsMetadataMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> DataObject:
        return create_data_object(self.test_with_baton, name, metadata)


class TestBatonCollectionMapper(_TestBatonIrodsEntityMetadataMapper):
    """
    Tests for `BatonCollectionIrodsMetadataMapper`.
    """
    def create_mapper(self) -> BatonCollectionIrodsMetadataMapper:
        return BatonCollectionIrodsMetadataMapper(self.test_with_baton.baton_location)

    def create_irods_entity(self, name: str, metadata: IrodsMetadata=IrodsMetadata()) -> Collection:
        return create_collection(self.test_with_baton, name, metadata)


# Trick required to stop Python's unittest from running the abstract base classes as tests
del _TestBatonIrodsEntityMetadataMapper


if __name__ == "__main__":
    unittest.main()

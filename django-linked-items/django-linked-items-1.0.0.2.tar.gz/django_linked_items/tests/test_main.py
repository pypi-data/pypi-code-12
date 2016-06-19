"main testing module"
from django.test import TestCase

def data():
    "Add data to the system to test against."
    # pylint: disable=no-member
    # Add the following items:
    from ..tools import models
    entries = ['Alpha', 'Bravo', 'Charlie', 'Delta',
               'A1', 'C1', 'D1', 'D2',
               'C1-A', 'D2-1', 'D2-2']

    tmp = dict()
    for index, entry in enumerate(entries):
        index += 1
        tmp[entry] = models.Item.objects.create(id=index, name=entry)

    # Now create relationships, A1 is under Alpha, C1 under Charlie and D1 & D2
    # under Delta, C1-A under C1, etc.
    pairs = [[tmp['Alpha'], tmp['A1']],
             [tmp['Charlie'], tmp['C1']],
             [tmp['Delta'], tmp['D1']],
             [tmp['Delta'], tmp['D2']],
             [tmp['C1'], tmp['C1-A']],
             [tmp['D2'], tmp['D2-1']],
             [tmp['D2'], tmp['D2-2']]]

    for one, two in pairs:
        models.Link.objects.create(item_one=one, item_two=two)



# Create your tests here.
class MainTestCase(TestCase):
    "main test case"
    # pylint: disable=missing-docstring, no-member, invalid-name
    @classmethod
    def setUpClass(cls):
        returns = super(MainTestCase, cls).setUpClass()
        data()
        return returns

    def setUp(self):
        self.expected_4 = {4:{7:'$',
                              8:{10:'$',
                                 11:'$'}},}
        TestCase.setUp(self)

    def test_010_delta_id(self):
        from .. import models
        expected = 4
        actually = models.Item.objects.get(name='Delta').id
        self.assertEqual(expected, actually)

    def test_020_get_linked_ids(self):
        from ..tools import relations
        expected = [7, 8]
        actually = list(relations.get_linked_ids(4))
        self.assertEqual(expected, actually)

    def test_021_get_linked_ids_upwards(self):
        from ..tools import relations
        expected = [1]
        actually = list(relations.get_linked_ids(5, upwards=True))
        self.assertEqual(expected, actually)

    def test_030_get_work(self):
        from ..tools import relations
        temp = {'Alpha':{'A1':None},
                'Bravo':None,
                'Charlie':{'C1':{'C1-A':None},},
                'Delta':{'D1':None,
                         'D2':{'D2-1':None,
                               'D2-2':'XYZ'}}}
        expected = 'XYZ'
        provided = ['Delta', 'D2', 'D2-2']
        actually = relations.get_work(temp, provided)
        self.assertEqual(expected, actually)

    def test_040_get_all_leaves(self):
        "Test if it gets all leaves"
        from ..tools import relations
        provided = 4
        expected = self.expected_4
        actually = relations.get_nodes_recursive_from(provided)
        self.assertEqual(expected, actually)

    def test_050_get_all_leaves_with_infinity(self):
        "Test if it gets all leaves"
        # As we are adding a link, this test will also fail if the lru_cache
        # is not cleared (since we already queries with the same parameters).
        from ..tools import relations, models
        item_one = models.Item.objects.get(name='D2-2')
        item_two = models.Item.objects.get(name='Delta')
        link = models.Link.objects.create(item_one=item_one,
                                          item_two=item_two)
        self.expected_4[4][8][11] = {4:'∞'}

        provided = 4
        expected = self.expected_4
        actually = relations.get_nodes_recursive_from(provided)
        self.assertEqual(expected, actually)
        link.delete()

    def test_060_get_leaves_at_end(self):
        "Test if it gets all leaves"
        from ..tools import relations
        provided = 10
        expected = {10:'$'}
        actually = relations.get_nodes_recursive_from(provided)
        self.assertEqual(expected, actually)

    def test_070_relations_exception(self):
        "Test if throws an exception if the item id does not exist."
        from ..tools import relations
        provided = 20
        self.assertRaises(relations.RelationsError,
                          relations.get_nodes_recursive_from, provided)

    def test_080_get_leaves_by_item(self):
        "Test if the model integations work"
        from ..tools import models
        provided = models.Item.objects.get(id=4)
        expected = self.expected_4
        actually = provided.get_linked()
        self.assertEqual(expected, actually)


    def test_085_add_link_via_item(self):
        "Test if it gets all leaves"
        from ..tools import relations, models
        item = models.Item.objects.get(name='D2-2')
        to_link = models.Item.objects.get(name='Delta')
        link = item.add_link(to_link)

        self.expected_4[4][8][11] = {4:'∞'}

        provided = 4
        expected = self.expected_4
        actually = relations.get_nodes_recursive_from(provided)
        self.assertEqual(expected, actually)
        link.delete()

    def test_090_get_leaves_by_item_upwards(self):
        "Test if the model integations work"
        from ..tools import models
        provided = models.Item.objects.get(id=5)
        expected = {5: {1: '^'}}
        actually = provided.get_linked(upwards=True)
        self.assertEqual(expected, actually)

    def test_100_print_name(self):
        "Test if the models string are as expected"
        from ..tools import models
        item = models.Item.objects.get(id=5)
        self.assertEqual('A1', str(item))

        link = item.linked_as_two.all()[0]

        self.assertEqual('Alpha | A1', str(link))
        relation_name = 'Relation Name'

        relation = models.Relation.objects.create(name=relation_name)
        self.assertEqual(relation_name, str(relation))

        link.relation = relation
        link.save()

        self.assertEqual('Alpha | A1' + ' # ' + relation_name, str(link))

    def test_110_view(self):
        "Test if the view returns something sensible."
        # The view is not expected to be used in anything resembling production
        response = self.client.get('/')
        expected = [[1, 5, None], [3, 6, None], [4, 7, None], [4, 8, None],
                    [6, 9, None], [8, 10, None], [8, 11, None]]
        self.assertEqual(expected, response.json()['response'])


if __name__ == '__main__': # pragma: no cover
    # pylint: disable=wrong-import-position
    import django
    django.setup()
    django.core.management.call_command('test')

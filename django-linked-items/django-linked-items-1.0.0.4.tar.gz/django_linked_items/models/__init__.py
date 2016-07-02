"""
Django Linked Items Models
"""
from django.db import models
from ..tools import relations

#pylint: disable=no-member
class Item(models.Model):
    "The base item to be linked."
    name = models.CharField(max_length=128)

    def get_linked(self, upwards=False):
        "Return relations."
        # The return compound dictionary has keys that are the item id's.
        return relations.get_nodes_recursive_from(self.id, upwards)

    def add_link(self, item, relation=None):
        "Add a link"
        return Link.objects.create(item_one=self, item_two=item,
                                   relation=relation)

    def __str__(self):
        return self.name


class Relation(models.Model):
    "The relationship between the item."
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Link(models.Model):
    "Link two items together"
    class Meta: # pylint: disable=missing-docstring, too-few-public-methods
        unique_together = ('item_one', 'item_two', 'relation')

    item_one = models.ForeignKey(Item, related_name='linked_as_one')
    item_two = models.ForeignKey(Item, related_name='linked_as_two')
    relation = models.ForeignKey(Relation, related_name='link',
                                 null=True, blank=True)

    def __str__(self):
        tmp = [str(self.item_one), ' | ', str(self.item_two)]
        if not self.relation is None:
            tmp.append(' # ' + str(self.relation))
        return ''.join(tmp)

    def save(self, *args, **kwargs):
        return models.Model.save(self, *args, **kwargs)


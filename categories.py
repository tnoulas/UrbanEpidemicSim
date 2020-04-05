'''
Created on 22 Jul 2013

@author: petko
'''
import json
from pydoc import deque


class _Node(object):

    def __init__(self, parent, data):
        self.parent = parent
        self.data = data
        self.children = []


class Categories(object):

    def __init__(self):
        self._categories = None
        # self._resources = Resources()

        self._root = None
        self._name_category_map = {}
        self._short_name_category_map = {}

        self._load()
        self._load_colors()

    def _load(self):

        json_data = open('categories.json')
        data = json.load(json_data)
        json_data.close()
        self._categories = data

        self._root = _Node(None, None)
        nodeQueue = deque([])
        nodeQueue.append(self._root)

        objectQueue = deque([])
        objectQueue.append(self._categories)

        while len(nodeQueue) > 0:
            node = nodeQueue.pop()
            category = objectQueue.pop()
            if not (node.data is None):
                self._name_category_map[node.data['name']] = node
                self._short_name_category_map[node.data['shortName']] = node

            categories = category.get('categories')
            if not (categories is None):
                for child in categories:
                    childNode = _Node(node, {'name': child['pluralName'],  ### change this to name if it is not plural
                                             'shortName': child['shortName']})
                    node.children.append(childNode)

                    nodeQueue.append(childNode)
                    objectQueue.append(child)

    def get_parent(self, category):
        node = self._name_category_map.get(category)
        if node is None:
            node = self._short_name_category_map.get(category)
            if node is None:
                return None

        while node.parent is not None and node.parent.data is not None:
            node = node.parent
            break

        return node.data['name']

    def get_top_parent(self, category):
        node = self._name_category_map.get(category)
        if node is None:
            node = self._short_name_category_map.get(category)
            if node is None:
                return None

        while node.parent is not None and node.parent.data is not None:
            node = node.parent

        return node.data['name']

    def get_top_level_categories(self):
        return [child.data['name'] for child in self._root.children]

    def _load_colors(self):
        self._colors = {'Arts & Entertainment': 'r', 'College & University': '#44FF00',
                        'Food': 'b', 'Nightlife Spot': '#DDFF00', 'Outdoors & Recreation': 'm',
                        'Professional & Other Places': 'c', 'Residence': 'k',
                        'Shop & Service': '#800000', 'Travel & Transport': '#008000'}

    def get_category_color_code(self, category):
        """
        """
        if category in self._colors:
            return self._colors[category]

        return 'k'


cats = Categories()
# print cats.get_top_level_categories()
# print cats.get_top_parent('Automotive Shop')

import binascii
import random
import urllib.request

from enum import Enum

class ClassName(Enum):
    Scion = 0
    Marauder = 1
    Ranger = 2
    Witch = 3
    Duelist = 4
    Templar = 5
    Shadow = 6

class Build:
    def __init__(self, class_name):
        self.class_name = class_name
        self.nodes = []
        self.choices = []

    def add_node(self, node, alternates=None):
        self.nodes.append(node)
        if alternates:
            self.choices.append(alternates)

    def url(self, base='https://www.pathofexile.com/passive-skill-tree/'):
        array = bytearray()
        version_info = [0,0,0,4]
        array.extend(version_info)
        array.append(self.class_name.value)
        array.append(0)
        array.append(0) # this is the "ascendancy class" -- we don't support it dawg
        for node in self.nodes:
            array.append(int(node / 256))
            array.append(node % 256)
        array.extend([0] * (2 * len(self.nodes) + 4 - len(array)))

        url = base + binascii.b2a_base64(array).decode('utf-8').replace('+', '-').replace('/', '_')
        shortened = urllib.request.urlopen("http://poeurl.com/shrink.php?url=" + url).read()
        return "http://poeurl.com/" + shortened.decode('utf-8').strip()


class BuildMaker:
    def __init__(self, skill_tree):
        self.skills = skill_tree

    def new(self):
        character_classes = self.skills['root']['out']
        class_id = random.choice(character_classes)
        class_info = next(filter(
            lambda i: i['id'] == class_id,
            self.skills['nodes']
        ))
        return Build(ClassName(class_info['spc'][0]))

    def choose_next_node(self, build):
        if not build.nodes:
            class_info = next(filter(
                lambda i: i['spc'] == [build.class_name.value],
                self.skills['nodes']
            ))
            group_id = class_info['g']
            starting_nodes = list(filter(
                    lambda i: i != class_info['id'],
                    self.skills['groups'][str(group_id)]['n']
            ))
            node_id = random.choice(starting_nodes)
            alternate_ids = list(filter(
                lambda i: i != node_id,
                starting_nodes
            ))

            build.add_node(node_id, alternate_ids)
        else:
            last_node_id = build.nodes[-1]
            last_node = next(filter(
                lambda i: i['id'] == last_node_id,
                self.skills['nodes']
            ))
            last_node_outs = list(i for i in filter(
                lambda i: i not in build.nodes,
                last_node['out']
            ) if not next(filter(lambda j: j['id'] == i, self.skills['nodes']))['spc'])
            other_node_ins = list(x['id'] for x in filter(
                lambda i: last_node_id in i['out'] and i['id'] not in build.nodes,
                self.skills['nodes']
            ) if not x['spc'] and not 'isAscendancyStart' in x)
            possibilities = list(set(last_node_outs + other_node_ins))
            if possibilities:
                choice = random.choice(possibilities)
                alternates = list(filter(
                    lambda i: i != choice,
                    possibilities
                ))
                build.add_node(choice, alternates)
            else:
                possibilities = build.choices.pop()
                choice = possibilities.pop(random.randrange(len(possibilities)))
                build.add_node(choice, possibilities)
        return build



if __name__ == '__main__':
    import json, pprint
    s = json.load(open('skill-tree.json.txt'))
    bm = BuildMaker(s)
    b = bm.new()
    for i in range(109):
        bm.choose_next_node(b)

    print(b.class_name.name)
    # for node in b.nodes:
    #     n = next(filter(
    #         lambda i: i['id'] == node,
    #         s['nodes']
    #     ))
    #     pprint.pprint([n['id'], n['dn']])

    print(b.url())#base="https://poebuilder.com/character/"))

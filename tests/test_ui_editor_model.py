from __future__ import annotations

import copy


def find_by_id(target: str, data: dict):
    if data.get('id') == target:
        return data
    for child in data.get('children', []):
        found = find_by_id(target, child)
        if found:
            return found
    return None


def test_ui_tree_lookup_and_duplicate_model():
    data = {'type': 'panel', 'id': 'root', 'children': [
        {'type': 'button', 'id': 'start', 'x': 10, 'y': 20, 'width': 100, 'height': 40}
    ]}
    current = find_by_id('start', data)
    assert current is not None
    clone = copy.deepcopy(current)
    clone['id'] = 'start_copy'
    data['children'].append(clone)
    assert find_by_id('start_copy', data)['x'] == 10
    assert len(data['children']) == 2

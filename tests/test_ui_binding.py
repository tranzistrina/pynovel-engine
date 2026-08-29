from vnengine.ui.binding import Binding, BindingRegistry, get_path


class Doc:
    def __init__(self):
        self.widgets = {'label': type('W', (), {'text': ''})(), 'bar': type('W', (), {'visible': False})()}
    def find(self, widget_id):
        return self.widgets.get(widget_id)


def test_get_path_and_binding_apply():
    state = {'strategy': {'supplies': 0.25, 'name': 'Crusade'}}
    assert get_path(state, 'strategy.supplies') == 0.25
    doc = Doc()
    registry = BindingRegistry([
        Binding('label', 'text', 'strategy.name'),
        Binding('bar', 'visible', 'strategy.supplies'),
    ])
    changed = registry.apply(doc, state)
    assert changed == ['label.text', 'bar.visible']
    assert doc.widgets['label'].text == 'Crusade'
    assert doc.widgets['bar'].visible == 0.25


def test_binding_transforms_are_explicit():
    doc = Doc(); state = {'value': 0.42}
    registry = BindingRegistry([Binding('label', 'text', 'value', transform='percent')])
    registry.apply(doc, state)
    assert doc.widgets['label'].text == '42%'

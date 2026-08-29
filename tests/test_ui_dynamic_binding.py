from vnengine.ui.binding import Binding, BindingRegistry


class Widget:
    def __init__(self):
        self.text = ""
        self.visible = True
        self.enabled = True


class Document:
    def __init__(self):
        self.widget = Widget()

    def find(self, widget_id):
        return self.widget if widget_id == "status" else None


def test_binding_updates_text_visibility_and_enabled_properties():
    registry = BindingRegistry([
        Binding("status", "text", "strategy.supplies", default=0, transform="str"),
        Binding("status", "visible", "strategy.show_status", default=False),
        Binding("status", "enabled", "strategy.can_act", default=False),
    ])
    document = Document()
    changed = registry.apply(document, {"strategy": {"supplies": 42, "show_status": True, "can_act": False}})
    assert document.widget.text == "42"
    assert document.widget.visible is True
    assert document.widget.enabled is False
    assert changed == ["status.text", "status.visible", "status.enabled"]

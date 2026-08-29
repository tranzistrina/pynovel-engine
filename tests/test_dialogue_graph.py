from vnengine.script.dialogue_graph import DialogueGraph, DialogueNode


def test_compile_graph():
    graph = DialogueGraph(nodes=[
        DialogueNode(id='start', kind='say', speaker='Alice', text='Hello', target='choice'),
        DialogueNode(id='choice', kind='choice', options=[{'text':'Go', 'target':'end'}]),
        DialogueNode(id='end', kind='end'),
    ])
    text = graph.compile()
    assert 'label start' in text
    assert 'say Alice' in text
    assert '"Go": end' in text


def test_compile_rejects_missing_target():
    graph = DialogueGraph(nodes=[DialogueNode(id='start', kind='jump', target='missing')])
    try:
        graph.compile()
    except ValueError as exc:
        assert 'Missing node target' in str(exc)
    else:
        raise AssertionError('Missing target should fail compilation')

from vnengine.script.parser import VNParser

def test_parse():
    story = VNParser().parse('''label start\nsay Alice "Hello world"\nset affection = 5\nchoice\n  "Stay": start\n''')
    assert story.labels['start'] == 0
    assert [a.kind for a in story.actions] == ['say','set','choice']
    assert story.actions[-1].data['options'][0].target == 'start'

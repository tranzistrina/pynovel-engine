from vnengine.script.parser import VNParser

def test_parser_choices_conditions():
    story=VNParser().parse('''label start\nset affection = 2\nif affection >= 2\nsay Alice "Hello"\nelse\nsay Alice "Bye"\nendif\nchoice\n"Continue": start\n"End": ending\nlabel ending\nend\n''')
    assert story.labels['start']==0
    assert story.labels['ending']>0
    assert [a.kind for a in story.actions]==['set','if','say','else','say','endif','choice','end']

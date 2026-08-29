from vnengine.script.parser import VNParser
from vnengine.core.expressions import evaluate

def test_parser_choices_conditions():
    story=VNParser().parse('''title "Demo"\nlabel start\nset affection = 2\nset affection += 3\nif affection >= 5\nsay Alice "Hello"\nelse\nsay Alice "Bye"\nendif\nchoice\n"Continue": start\n"End": ending\nlabel ending\nend\n''')
    assert story.title=='Demo'
    assert story.labels['start']==0
    assert story.labels['ending']>0
    assert [a.kind for a in story.actions]==['set','set','if','say','else','say','endif','choice','end']
    assert story.actions[1].data['operator']=='+='
    assert story.actions[-2].data['options'][0].target=='start'

def test_safe_expression():
    env={'affection':7,'name':'Alice','flag':True}
    assert evaluate('affection >= 5 and flag',env) is True
    assert evaluate('name in ["Alice", "Bob"]',env) is True

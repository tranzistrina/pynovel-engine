from __future__ import annotations
from pathlib import Path
from typing import Callable
import operator,json,pygame
from vnengine.core.expressions import evaluate
from vnengine.core.model import Action,SaveState,Story,Character
from vnengine.core.save import read_save,write_save
from vnengine.animation.tween import Tween
from vnengine.animation.timeline_runtime import TimelinePlayer
POSITIONS={"left":23.0,"center":50.0,"right":77.0}
class GameState:
    def __init__(self,story:Story):
        self.story=story;self.index=0;self.variables=dict(story.variables);self.history=[];self.background_path=None;self.background=None;self.characters={};self.character_surfaces={};self.dialogue=None;self.choice_options=[];self.running=True;self.paused_for_input=False;self.text_progress=0.0;self.auto_mode=False;self.skip_mode=False;self.wait_until=0.0;self.transition_until=0.0;self.transition_name="none";self.conditional_stack=[];self.settings={"text_speed":42.0,"volume":0.8,"fullscreen":False};self.animations={};self.timeline_player=None
class Runtime:
    def __init__(self,story:Story,asset_root:str|Path):
        self.state=GameState(story);self.asset_root=Path(asset_root);self._image_cache={};self._sound_cache={};self.state.timeline_player=TimelinePlayer(self.asset_root);self._handlers={"background":self._background,"character":self._character,"expression":self._expression,"move":self._move,"scale":self._scale,"rotate":self._rotate,"play_animation":self._play_animation,"stop_animation":self._stop_animation,"music":self._music,"music_stop":self._music_stop,"sound":self._sound,"say":self._say,"set":self._set,"jump":self._jump,"if":self._if,"else":self._else,"endif":self._endif,"choice":self._choice,"wait":self._wait,"transition":self._transition,"end":self._end,"scene":lambda a:None}
    def asset(self,rel):p=Path(rel);return p if p.is_absolute() else self.asset_root/p
    def load_image(self,rel):
        if rel not in self._image_cache:
            path=self.asset(rel)
            if path.suffix.lower()==".svg":
                try:
                    import cairosvg,io
                    png=cairosvg.svg2png(url=str(path),output_width=1200,output_height=900)
                    self._image_cache[rel]=pygame.image.load(io.BytesIO(png)).convert_alpha()
                except ImportError as exc:raise pygame.error("SVG asset requires cairosvg") from exc
            else:self._image_cache[rel]=pygame.image.load(path).convert_alpha()
        return self._image_cache[rel]
    def _background(self,a):
        self.state.background_path=a.data["path"]
        try:self.state.background=self.load_image(a.data["path"])
        except (FileNotFoundError,pygame.error):self.state.background=None
    def _character(self,a):
        name=a.data["name"]
        if a.data.get("action")=="hide":self.state.characters.pop(name,None);self.state.character_surfaces.pop(name,None);self.state.animations.pop(name,None);return
        position=a.data.get("position","center");x=a.data.get("x");x=POSITIONS.get(position,50.0) if x is None else x
        char=Character(name,a.data["image"],position,True,float(x),float(a.data.get("y",100.0)),float(a.data.get("scale",1.0)),1.0,a.data.get("expression","neutral"),float(a.data.get("rotation",0.0)));self.state.characters[name]=char
        try:self.state.character_surfaces[name]=self.load_image(char.image)
        except (FileNotFoundError,pygame.error):self.state.character_surfaces.pop(name,None)
    def _expression(self,a):
        char=self.state.characters.get(a.data["name"])
        if char:char.expression=a.data["expression"]
    def _move(self,a):
        char=self.state.characters.get(a.data["name"])
        if not char:return
        self.state.animations.setdefault(char.name,{})["x"]=Tween(char.x,POSITIONS.get(a.data["position"],char.x),float(a.data.get("duration",.35)));char.position=a.data["position"]
    def _scale(self,a):
        char=self.state.characters.get(a.data["name"])
        if char:self.state.animations.setdefault(char.name,{})["scale"]=Tween(char.scale,float(a.data["scale"]),float(a.data.get("duration",.35)))
    def _rotate(self,a):
        char=self.state.characters.get(a.data["name"])
        if char:self.state.animations.setdefault(char.name,{})["rotation"]=Tween(char.rotation,float(a.data["rotation"]),float(a.data.get("duration",.35)))
    def _play_animation(self,a):
        if self.state.timeline_player:self.state.timeline_player.play(a.data["name"])
    def _stop_animation(self,a):
        if self.state.timeline_player:self.state.timeline_player.stop(a.data["name"])
    def _apply_timeline_updates(self,updates):
        for _name,values in updates.items():
            for (target,prop),value in values.items():
                char=self.state.characters.get(target)
                if char and prop in {"x","y","scale","opacity","rotation"}:setattr(char,prop,float(value))
    def update(self,dt):
        finished=[]
        for name,props in list(self.state.animations.items()):
            char=self.state.characters.get(name)
            if not char:finished.append(name);continue
            for prop,tween in props.items():setattr(char,prop,tween.step(dt))
            if all(t.done for t in props.values()):finished.append(name)
        for name in finished:self.state.animations.pop(name,None)
        if self.state.timeline_player:self._apply_timeline_updates(self.state.timeline_player.update(dt))
    def _music(self,a):
        try:pygame.mixer.music.load(self.asset(a.data["path"]));pygame.mixer.music.set_volume(float(self.state.settings["volume"]));pygame.mixer.music.play(-1)
        except pygame.error:pass
    def _music_stop(self,a):
        try:pygame.mixer.music.fadeout(300)
        except pygame.error:pass
    def _sound(self,a):
        try:
            key=a.data["path"];snd=self._sound_cache.get(key) or pygame.mixer.Sound(self.asset(key));self._sound_cache[key]=snd;snd.set_volume(float(self.state.settings["volume"]));snd.play()
        except (pygame.error,FileNotFoundError):pass
    def _say(self,a):self.state.dialogue=(a.data["speaker"],a.data["text"]);self.state.history.append(self.state.dialogue);self.state.history=self.state.history[-200:];self.state.paused_for_input=True;self.state.text_progress=0.0
    def _set(self,a):
        name=a.data["name"];value=evaluate(a.data["expression"],self.state.variables);opn=a.data.get("operator","=")
        if opn=="=":self.state.variables[name]=value;return
        cur=self.state.variables.get(name,0);funcs={"+=":operator.add,"-=":operator.sub,"*=":operator.mul,"/=":operator.truediv};self.state.variables[name]=funcs[opn](cur,value)
    def _jump(self,a):self.state.index=self.state.story.labels.get(a.data["target"],len(self.state.story.actions));self.state.paused_for_input=False;self.state.dialogue=None;self.state.conditional_stack.clear()
    def _if(self,a):self.state.conditional_stack.append(bool(evaluate(a.data["expression"],self.state.variables)))
    def _else(self,a):
        if self.state.conditional_stack:self.state.conditional_stack[-1]=not self.state.conditional_stack[-1]
    def _endif(self,a):
        if self.state.conditional_stack:self.state.conditional_stack.pop()
    def _choice(self,a):self.state.choice_options=a.data["options"];self.state.paused_for_input=True
    def _wait(self,a):self.state.wait_until=pygame.time.get_ticks()/1000.0+float(a.data["seconds"])
    def _transition(self,a):self.state.transition_name=a.data["name"];self.state.transition_until=pygame.time.get_ticks()/1000.0+float(a.data.get("duration",.35))
    def _end(self,a):self.state.running=False
    def choose(self,number):
        if not 0<=number<len(self.state.choice_options):return
        target=self.state.choice_options[number].target;self.state.choice_options=[];self._jump(Action("jump",{"target":target}));self.advance()
    def advance(self):
        if not self.state.running:return
        now=pygame.time.get_ticks()/1000.0
        if self.state.wait_until and now<self.state.wait_until:return
        self.state.wait_until=0
        if self.state.paused_for_input:
            if self.state.dialogue:self.state.dialogue=None;self.state.paused_for_input=False
            else:return
        while self.state.index<len(self.state.story.actions) and self.state.running and not self.state.paused_for_input:
            action=self.state.story.actions[self.state.index];self.state.index+=1
            if self.state.conditional_stack and not all(self.state.conditional_stack) and action.kind not in ("if","else","endif"):continue
            self._handlers[action.kind](action)
            if action.kind in ("say","choice","end"):break
    def new_game(self):
        story=self.state.story;self.state=GameState(story);self.state.timeline_player=TimelinePlayer(self.asset_root);self._image_cache.clear();self._sound_cache.clear();self.advance()
    def save(self,path):write_save(path,SaveState(self.state.index,self.state.variables,self.state.history,self.state.background_path,{k:{"image":v.image,"position":v.position,"visible":v.visible,"x":v.x,"y":v.y,"scale":v.scale,"opacity":v.opacity,"expression":v.expression,"rotation":v.rotation} for k,v in self.state.characters.items()}))
    def load(self,path):
        data=read_save(path);s=self.state;s.index=data.action_index;s.variables=data.variables;s.history=data.history;s.background_path=data.background;s.dialogue=None;s.choice_options=[];s.paused_for_input=False;s.conditional_stack.clear();s.animations.clear()
        if data.background:
            try:s.background=self.load_image(data.background)
            except (FileNotFoundError,pygame.error):s.background=None
        s.characters={k:Character(k,v["image"],v.get("position","center"),v.get("visible",True),v.get("x",POSITIONS.get(v.get("position","center"),50.0)),v.get("y",100.0),v.get("scale",1.0),v.get("opacity",1.0),v.get("expression","neutral"),v.get("rotation",0.0)) for k,v in data.characters.items()};s.character_surfaces={}
        for k,c in s.characters.items():
            try:s.character_surfaces[k]=self.load_image(c.image)
            except (FileNotFoundError,pygame.error):pass

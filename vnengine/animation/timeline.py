from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


EASINGS = {"linear", "smooth", "ease_in", "ease_out", "ease_in_out"}


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def ease(value: float, name: str = "linear") -> float:
    t = clamp01(value)
    if name == "linear": return t
    if name == "ease_in": return t * t
    if name == "ease_out": return 1.0 - (1.0 - t) ** 2
    if name in {"smooth", "ease_in_out"}: return t * t * (3.0 - 2.0 * t)
    raise ValueError(f"Unknown easing: {name}")


@dataclass(frozen=True, slots=True)
class Keyframe:
    time: float
    value: float
    easing: str = "linear"
    def __post_init__(self) -> None:
        if self.time < 0: raise ValueError("Keyframe time must be >= 0")
        if self.easing not in EASINGS: raise ValueError(f"Unknown easing: {self.easing}")


@dataclass(slots=True)
class Track:
    target: str
    property: str
    keys: list[Keyframe] = field(default_factory=list)
    def add(self, key: Keyframe) -> None: self.keys.append(key); self.keys.sort(key=lambda item: item.time)
    @property
    def duration(self) -> float: return self.keys[-1].time if self.keys else 0.0
    def sample(self, time: float) -> float | None:
        if not self.keys: return None
        if time <= self.keys[0].time: return self.keys[0].value
        if time >= self.keys[-1].time: return self.keys[-1].value
        for left, right in zip(self.keys, self.keys[1:]):
            if left.time <= time <= right.time:
                span = right.time-left.time
                progress = 1.0 if span <= 0 else (time-left.time)/span
                return left.value + (right.value-left.value)*ease(progress,left.easing)
        return self.keys[-1].value


@dataclass(slots=True)
class Timeline:
    name: str
    tracks: list[Track] = field(default_factory=list)
    loop: bool = False
    duration: float = 0.0
    time: float = 0.0
    playing: bool = False
    def add_track(self, track: Track) -> Track: self.tracks.append(track); self.duration=max(self.duration,track.duration); return track
    def add_keyframe(self,target: str,property: str,time: float,value: float,easing: str="linear") -> None:
        track=next((item for item in self.tracks if item.target==target and item.property==property),None)
        if track is None: track=self.add_track(Track(target,property))
        track.add(Keyframe(time,value,easing)); self.duration=max(self.duration,time)
    def sample(self,time: float|None=None)->dict[tuple[str,str],float]:
        current=self.time if time is None else float(time)
        return {(track.target,track.property):value for track in self.tracks if (value:=track.sample(current)) is not None}
    def seek(self,time: float)->None:
        value=max(0.0,float(time))
        if self.duration<=0:
            self.time=0.0; self.playing=False if value>0 else self.playing; return
        if self.loop:
            self.time=value%self.duration
            if value>0 and self.time==0: self.time=0.0
        else:
            self.time=min(self.duration,value)
            if self.time>=self.duration: self.playing=False
    def play(self)->None:self.playing=True
    def pause(self)->None:self.playing=False
    def stop(self)->None:self.playing=False;self.time=0.0
    def update(self,dt: float)->dict[tuple[str,str],float]:
        if self.playing:self.seek(self.time+max(0.0,float(dt)))
        return self.sample()
    def to_dict(self)->dict[str,Any]:
        return {"name":self.name,"loop":self.loop,"duration":self.duration,"tracks":[{"target":t.target,"property":t.property,"keys":[{"time":k.time,"value":k.value,"easing":k.easing} for k in t.keys]} for t in self.tracks]}
    @classmethod
    def from_dict(cls,payload:dict[str,Any])->"Timeline":
        timeline=cls(str(payload.get("name","Timeline")),loop=bool(payload.get("loop",False)))
        for raw_track in payload.get("tracks",[]):
            track=Track(str(raw_track.get("target","")),str(raw_track.get("property","")))
            for raw_key in raw_track.get("keys",[]):track.add(Keyframe(float(raw_key.get("time",0)),float(raw_key.get("value",0)),str(raw_key.get("easing","linear"))))
            timeline.add_track(track)
        timeline.duration=max(timeline.duration,float(payload.get("duration",timeline.duration)));return timeline

from __future__ import annotations
from typing import Generic, TypeVar, Optional, Protocol

TPercept = TypeVar("TPercept")
TAction = TypeVar("TAction")
TResult = TypeVar("TResult")
TExperience = TypeVar("TExperience")

class IPerceptionSource(Protocol[TPercept]):
    def sense(self) -> Optional[TPercept]: ...

class IPolicy(Protocol[TPercept, TAction]):
    def decide(self, percept: TPercept) -> TAction: ...

class IActuator(Protocol[TAction, TResult]):
    def act(self, action: TAction) -> TResult: ...

class ILearningComponent(Protocol[TExperience]):
    def learn(self, exp: TExperience) -> None: ...

class SoftwareAgent(Generic[TPercept, TAction, TResult, TExperience]):
    def step(self) -> Optional[TResult]:
        raise NotImplementedError

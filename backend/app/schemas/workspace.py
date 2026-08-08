from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkspacePosition(BaseModel):
    x: float
    y: float


class WorkspaceNode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1)
    data: dict[str, Any] = Field(default_factory=dict)
    position: WorkspacePosition | None = None
    type: str | None = None


class WorkspaceEdge(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    data: dict[str, Any] | None = None
    type: str | None = None


class WorkspaceSubmission(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId", min_length=1)
    timestamp: str = Field(min_length=1)
    payload: dict[str, Any] = Field(default_factory=dict)


class AddPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    node_id: str = Field(alias="nodeId", min_length=1)
    node_data: dict[str, Any] = Field(alias="nodeData", default_factory=dict)


class RemovePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    node_id: str = Field(alias="nodeId", min_length=1)


class ConnectPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    edge_id: str = Field(alias="edgeId", min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)


class DisconnectPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    edge_id: str = Field(alias="edgeId", min_length=1)
    source: str | None = None
    target: str | None = None


class ConfigurePayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_key: str = Field(alias="configKey", min_length=1)
    value: Any


class EditPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    editor_id: str = Field(alias="editorId", min_length=1)
    content: str


class RunPayload(BaseModel):
    target: str = Field(min_length=1)


class SubmitPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(alias="taskId", min_length=1)
    data: dict[str, Any] = Field(default_factory=dict)


class UndoPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    restored_to_index: int | None = Field(default=None, alias="restoredToIndex", ge=0)


class ResetPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: str | None = None
    initial_snapshot_present: bool = Field(alias="initialSnapshotPresent")


class WorkspaceEventBase(BaseModel):
    id: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)


class WorkspaceEventAdd(WorkspaceEventBase):
    type: Literal["add"]
    payload: AddPayload


class WorkspaceEventRemove(WorkspaceEventBase):
    type: Literal["remove"]
    payload: RemovePayload


class WorkspaceEventConnect(WorkspaceEventBase):
    type: Literal["connect"]
    payload: ConnectPayload


class WorkspaceEventDisconnect(WorkspaceEventBase):
    type: Literal["disconnect"]
    payload: DisconnectPayload


class WorkspaceEventConfigure(WorkspaceEventBase):
    type: Literal["configure"]
    payload: ConfigurePayload


class WorkspaceEventEdit(WorkspaceEventBase):
    type: Literal["edit"]
    payload: EditPayload


class WorkspaceEventRun(WorkspaceEventBase):
    type: Literal["run"]
    payload: RunPayload


class WorkspaceEventSubmit(WorkspaceEventBase):
    type: Literal["submit"]
    payload: SubmitPayload


class WorkspaceEventUndo(WorkspaceEventBase):
    type: Literal["undo"]
    payload: UndoPayload


class WorkspaceEventReset(WorkspaceEventBase):
    type: Literal["reset"]
    payload: ResetPayload


WorkspaceEvent = Annotated[
    WorkspaceEventAdd
    | WorkspaceEventRemove
    | WorkspaceEventConnect
    | WorkspaceEventDisconnect
    | WorkspaceEventConfigure
    | WorkspaceEventEdit
    | WorkspaceEventRun
    | WorkspaceEventSubmit
    | WorkspaceEventUndo
    | WorkspaceEventReset,
    Field(discriminator="type"),
]


class WorkspaceResetBaseline(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    nodes: list[WorkspaceNode]
    edges: list[WorkspaceEdge]
    config: dict[str, Any]
    editors: dict[str, str]
    submissions: list[WorkspaceSubmission]
    challenge_id: str | None = Field(default=None, alias="challengeId")


class SerializedWorkspace(BaseModel):
    """Validated semantic subset emitted by Issue #4 workspace serialization.

    Extra UI-only fields such as selection are ignored rather than becoming interview evidence.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    nodes: list[WorkspaceNode]
    edges: list[WorkspaceEdge]
    config: dict[str, Any]
    editors: dict[str, str]
    submissions: list[WorkspaceSubmission]
    events: list[WorkspaceEvent]
    workspace_active: bool = Field(alias="workspaceActive")
    challenge_id: str | None = Field(default=None, alias="challengeId")
    initial_snapshot: WorkspaceResetBaseline | None = Field(default=None, alias="initialSnapshot")

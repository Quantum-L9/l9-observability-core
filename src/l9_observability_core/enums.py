"""Bounded canonical vocabulary."""

from enum import StrEnum


class EventStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class SpanKind(StrEnum):
    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"
    AGENT = "agent"
    VALIDATION = "validation"
    DEPLOYMENT = "deployment"


class ToolOutcome(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class ValidationOutcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"
    NOT_RUN = "not_run"


class FailureClass(StrEnum):
    VALIDATION = "validation"
    TIMEOUT = "timeout"
    DEPENDENCY = "dependency"
    AUTHORIZATION = "authorization"
    POLICY = "policy"
    TOOL = "tool"
    NETWORK = "network"
    RESOURCE = "resource"
    DATA = "data"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class OutcomeKind(StrEnum):
    COMPLETED = "completed"
    ARTIFACT_PRODUCED = "artifact_produced"
    STATE_CHANGED = "state_changed"
    EFFECT_OBSERVED = "effect_observed"
    NO_EFFECT = "no_effect"
    ROLLED_BACK = "rolled_back"
    UNKNOWN = "unknown"


class EffectivenessSignal(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"


class EvidenceKind(StrEnum):
    ARTIFACT = "artifact"
    RECEIPT = "receipt"
    LOG = "log"
    TRACE = "trace"
    SCHEMA = "schema"
    COMMIT = "commit"
    URL = "url"
    OTHER = "other"

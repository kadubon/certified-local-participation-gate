from clpg import TaskSnapshot, canonical_json, sha256_digest


def test_canonical_json_sorts_keys() -> None:
    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_digest_stable_for_equivalent_models() -> None:
    assert sha256_digest(TaskSnapshot(task_id="x")) == sha256_digest(TaskSnapshot(task_id="x"))


def test_digest_changes_when_model_changes() -> None:
    assert sha256_digest(TaskSnapshot(task_id="x")) != sha256_digest(TaskSnapshot(task_id="y"))

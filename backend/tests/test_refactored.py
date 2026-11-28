"""Guard the extraction and the three independent policy runs."""

from copy import deepcopy

import pytest

from lab import refactored, simulation


@pytest.mark.parametrize("policy, runner, order", [
    ("fixed", refactored.simulate_fixed, [1, 2, 3, 4]),
    ("longest", refactored.simulate_longest, [2, 1, 3, 4]),
    ("critical", refactored.simulate_critical, [1, 3, 2, 4]),
])
def test_separate_policy_runs_preserve_priorities_and_inputs(policy, runner, order):
    tasks = [
        refactored.Task(1, "split", 1),
        refactored.Task(2, "split", 3),
        refactored.Task(3, "base", 10, (1,)),
        refactored.Task(4, "base", 1, (2,)),
    ]
    original = deepcopy(tasks)
    result = runner(tasks, 1)
    assert result["policy"] == policy
    assert [entry["task_id"] for entry in result["timeline"]] == order
    assert tasks == original


@pytest.mark.parametrize("policy", refactored.POLICIES)
def test_comparisons_keep_three_independent_results(policy):
    config = {"form": "map", "parameters": {"durations": [1, 5, 2]},
              "processors": 2, "policy": policy}
    original = deepcopy(config)
    experiment = refactored.run_experiment(config)
    comparisons = experiment["comparisons"]
    assert list(comparisons) == ["fixed", "longest", "critical"]
    assert experiment["results"] is comparisons[policy]
    assert [result["policy"] for result in comparisons.values()] == list(refactored.POLICIES)
    assert comparisons["longest"]["timeline"] == comparisons["critical"]["timeline"]
    comparisons["longest"]["timeline"][0]["end"] = -1
    assert comparisons["critical"]["timeline"][0]["end"] > 0
    assert config == original


def test_original_imports_use_the_extracted_implementation():
    assert simulation.Task is refactored.Task
    assert simulation.ValidationError is refactored.ValidationError
    assert simulation.run_experiment is refactored.run_experiment


@pytest.mark.parametrize("version", refactored.SUPPORTED_SIMULATOR_VERSIONS)
@pytest.mark.parametrize("form, parameters", [
    ("map", {"durations": [1, 5, 2, 8, 3]}),
    ("dc", {"n": 5, "k": 3, "b": 1, "split_duration": 2,
            "base_duration": 5, "combine_duration": 3}),
])
@pytest.mark.parametrize("policy", refactored.POLICIES)
def test_experiment_analyzes_once_and_matches_standalone_runs(
        monkeypatch, version, form, parameters, policy):
    config = {"form": form, "parameters": parameters,
              "processors": 2, "policy": policy}
    _, tasks = refactored.parse_configuration(config, simulator_version=version)
    expected = {choice: refactored.simulate(tasks, 2, choice)
                for choice in refactored.POLICIES}
    analyze = refactored.analyze_graph
    calls = []

    def counted_analyze(tasks):
        ranks = analyze(tasks)
        calls.append((tasks, ranks.copy(), ranks))
        return ranks

    monkeypatch.setattr(refactored, "analyze_graph", counted_analyze)
    experiment = refactored.run_experiment(config, simulator_version=version)

    assert len(calls) == 1
    analyzed_tasks, original_ranks, shared_ranks = calls[0]
    assert analyzed_tasks == tasks
    assert shared_ranks == original_ranks
    assert experiment["comparisons"] == expected
    assert experiment["results"] is experiment["comparisons"][policy]
    assert experiment["dag"] == [
        {**task.to_dict(), "rank": original_ranks[task.id]} for task in tasks
    ]


@pytest.mark.parametrize("processors, policy, error, message", [
    (0, "unknown", refactored.ValidationError,
     "Processor count P must be an integer from 1 to 1."),
    (1, "unknown", refactored.ValidationError, "Unknown policy."),
    (1, "fixed", refactored.StructuralError,
     "Unfinished tasks have no running or ready tasks: dependency cycle."),
])
def test_standalone_simulate_preserves_validation_order(processors, policy, error, message):
    tasks = [refactored.Task(1, "base", 1, (2,)),
             refactored.Task(2, "base", 1, (1,))]
    with pytest.raises(error) as caught:
        refactored.simulate(tasks, processors, policy)
    assert str(caught.value) == message

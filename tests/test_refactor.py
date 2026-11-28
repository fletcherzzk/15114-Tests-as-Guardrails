"""Hand-calculated scheduling examples; uses unittest only.

From the repository root, run:
    .venv/Scripts/python.exe -m unittest discover -s tests -p test_refactor.py -v

The scheduling module is named refactored.py, not refactor.py, in this repo.
"""

import unittest

from tests_as_Guardrails.refactored import StructuralError, Task, simulate


class SchedulingTests(unittest.TestCase):
    def test_simultaneous_completions_unlock_join_immediately(self):
        tasks = [
            Task(1, "base", 3),
            Task(2, "base", 3),
            Task(3, "combine", 2, (1, 2)),
            Task(4, "base", 5, (1,)),
        ]

        result = simulate(tasks, 2, "fixed")

        # T1 and T2 finish at 3. Both successors are ready then, so T3
        # gets processor 1 and T4 gets processor 2, with no extra delay.
        self.assertEqual(result["timeline"], [
            {"task_id": 1, "processor_id": 1, "start": 0, "end": 3},
            {"task_id": 2, "processor_id": 2, "start": 0, "end": 3},
            {"task_id": 3, "processor_id": 1, "start": 3, "end": 5},
            {"task_id": 4, "processor_id": 2, "start": 3, "end": 8},
        ])
        self.assertEqual(result["metrics"]["makespan"], 8)
        self.assertEqual(result["idle_intervals"], [
            {"processor_id": 1, "start": 5, "end": 8},
        ])

    def test_fixed_and_longest_choose_different_ready_tasks(self):
        tasks = [Task(1, "map", 2), Task(2, "map", 5)]

        fixed = simulate(tasks, 1, "fixed")
        longest = simulate(tasks, 1, "longest")

        # Both tasks are ready at 0. Fixed chooses ID 1; longest chooses
        # the five-unit task. On one processor both runs finish at 7.
        self.assertEqual(fixed["timeline"], [
            {"task_id": 1, "processor_id": 1, "start": 0, "end": 2},
            {"task_id": 2, "processor_id": 1, "start": 2, "end": 7},
        ])
        self.assertEqual(longest["timeline"], [
            {"task_id": 2, "processor_id": 1, "start": 0, "end": 5},
            {"task_id": 1, "processor_id": 1, "start": 5, "end": 7},
        ])

    def test_critical_and_longest_choose_different_ready_tasks(self):
        tasks = [
            Task(1, "split", 2),
            Task(2, "base", 4),
            Task(3, "base", 7, (1,)),
        ]

        critical = simulate(tasks, 1, "critical")
        longest = simulate(tasks, 1, "longest")

        # Initially only T1 and T2 are ready. T1's remaining path is
        # 2 + 7 = 9, versus T2's 4; longest instead chooses T2's duration.
        # After T1, critical chooses T3 (7) before the still-ready T2 (4).
        self.assertEqual(critical["timeline"], [
            {"task_id": 1, "processor_id": 1, "start": 0, "end": 2},
            {"task_id": 3, "processor_id": 1, "start": 2, "end": 9},
            {"task_id": 2, "processor_id": 1, "start": 9, "end": 13},
        ])
        self.assertEqual(longest["timeline"], [
            {"task_id": 2, "processor_id": 1, "start": 0, "end": 5},
            {"task_id": 1, "processor_id": 1, "start": 4, "end": 6},
            {"task_id": 3, "processor_id": 1, "start": 6, "end": 13},
        ])

    def test_cycle_is_rejected(self):
        # Neither task can start: each requires the other to finish first.
        tasks = [Task(1, "base", 1, (2,)), Task(2, "base", 1, (1,))]

        with self.assertRaises(StructuralError) as caught:
            simulate(tasks, 1, "fixed")

        self.assertEqual(
            str(caught.exception),
            "Unfinished tasks have no running or ready tasks: dependency cycle.",
        )


if __name__ == "__main__":
    unittest.main()

"""Compatibility imports for callers of the original simulation module.

Scheduling logic lives in :mod:`lab.refactored`.
"""

from .refactored import (
    POLICIES,
    SIMULATOR_VERSION,
    SUPPORTED_SIMULATOR_VERSIONS,
    StructuralError,
    Task,
    ValidationError,
    _generate_dc_preorder,
    analyze_graph,
    generate_dc,
    generate_map,
    integer,
    parse_configuration,
    run_experiment,
    simulate,
    simulate_critical,
    simulate_fixed,
    simulate_longest,
)

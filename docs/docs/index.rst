.. LGM-35A Sentinel AaC Framework documentation master file.

Welcome to the Sentinel AaC Framework Specification
===================================================

.. toctree::
   :maxdepth: 2
   :caption: Architectural Contents:

Core Simulation Engine API
--------------------------
.. automodule:: engine
   :members:
   :undoc-members:
   :show-inheritance:

Automated QA Verification Matrix
--------------------------------
.. automodule:: test_engine
   :members:
   :undoc-members:
   :show-inheritance:

Mathematical Physical Boundaries
--------------------------------
The state engine evaluates active telemetry steps against deterministic boundary thresholds using the following multi-physics relationship:

.. math::

   \text{aerodynamicDrag} > 50,000 \text{ N} \quad \wedge \quad \text{dissociationRate} > 0.05 \text{ mol}/(\text{m}^3 \cdot \text{s})

# Design Notes - Sistema Guardião Core Logic

This document outlines design considerations and conceptual details for the core logic components of the Sistema Guardião, focusing on the GuardianCentralOrchestrator and its interactions.

## 1. `ThreatEvent` Dataclass Enhancements

The `ThreatEvent` dataclass (defined in `src/core_logic/guardian_orchestrator.py`) serves as a crucial data structure for representing threats across the system. The following are considerations for its refinement:

### 1.1. `origin_sensor_id`

*   **Consideration:** While `subsystem_source` identifies the subsystem (e.g., "SACI", "CURUPIRA"), it might be beneficial to include an optional `origin_sensor_id` field.
*   **Rationale:** This would allow for more granular tracing of data back to the specific sensor or data collection point within a subsystem, which could be valuable for debugging, detailed analysis, and understanding sensor reliability or specific characteristics.
*   **Decision:** An optional `origin_sensor_id: Optional[str] = None` will be added to the `ThreatEvent` dataclass.

### 1.2. `metadata` Field Structure

*   **Consideration:** The `metadata: Dict[str, Any]` field is currently flexible but could lead to inconsistencies if not managed.
*   **Rationale:** Establishing a convention or a set of common keys for `metadata` could improve interoperability and data processing across subsystems and for the orchestrator. For example, subsystems could be encouraged to use keys like `sensor_type`, `raw_reading`, `device_status`, `ip_address`, `user_agent`, etc., where applicable.
*   **Decision:** While a strict schema for `metadata` might be too restrictive initially, documentation and comments in the code will suggest a convention for common keys. Subsystems should aim to provide contextually relevant and, where possible, standardized metadata. For instance:
    *   SACI (fire): `{'wind_speed': 15, 'humidity': 30, 'temperature': 35, 'vegetation_type': 'dry_grass'}`
    *   CURUPIRA (cyber): `{'source_ip': '192.168.1.100', 'target_port': 80, 'attack_signature': 'SQL_INJECTION_ATTEMPT'}`
    *   IARA (epidemic): `{'symptom_cluster': ['fever', 'cough'], 'case_count': 5, 'proximity_alerts': 12}`

Further details on the `ThreatEvent` structure will be reflected directly in the Python dataclass definition.
## 2. `GuardianCentralOrchestrator` Conceptual Logic

The `GuardianCentralOrchestrator` is responsible for coordinating responses to threats. Its `coordinate_multi_threat_response` method embodies the core intelligence.

### 2.1. Conceptual Flow of `coordinate_multi_threat_response`

The method follows a conceptual multi-stage process:

1.  **Threat Correlation (using `MultiThreatCorrelator`):**
    *   **Input:** A list of `ThreatEvent` objects.
    *   **Process:** The `MultiThreatCorrelator` (e.g., via its `analyze_correlations` method) examines the incoming events for potential relationships. This could involve analyzing:
        *   **Spatial proximity:** Events occurring close to each other.
        *   **Temporal proximity:** Events occurring around the same time.
        *   **Causal links:** One event potentially triggering or influencing another (e.g., a power outage reported by BOITATÁ followed by communication disruptions reported by ANHANGÁ).
        *   **Pattern matching:** Known attack patterns or common co-occurrences.
    *   **Output (Example):** A data structure that groups or links correlated events. This could be a dictionary where keys are group identifiers and values are lists of `ThreatEvent` objects belonging to that group (e.g., `{'correlation_group_1': [event_X, event_Y]}`), or a list of `CorrelationReport` objects detailing the nature and strength of identified links.

2.  **Response Strategy Generation (using `MetaLearningEngine`):**
    *   **Input:** The output from the `MultiThreatCorrelator` (correlated event groups/reports) and historical data on previous responses and their effectiveness (e.g., from `self.response_history`).
    *   **Process:** The `MetaLearningEngine` (e.g., via its `suggest_response_strategies` method) uses this information to:
        *   Identify optimal response strategies for the current situation.
        *   Predict the potential effectiveness of different actions.
        *   Prioritize responses if multiple correlated threats require attention.
        *   Adapt strategies based on learned patterns from past incidents.
    *   **Output (Example):** A set of strategic recommendations, which might include suggested actions, priorities for different threat groups, or modifications to standard response protocols.

3.  **Response Plan Formulation:**
    *   **Process:** Based on the raw threat events, the insights from the correlator, and the strategies from the meta-learning engine, the orchestrator constructs a `response_plan`. This plan is a structured dictionary detailing the actions to be taken by each subsystem.
    *   **Structure (Conceptual Example):**
        ```python
        response_plan = {
            'plan_id': 'unique_identifier_string', # e.g., generated with timestamp
            'target_event_ids': ['event_id_1', 'event_id_2', ...], # List of event_ids this plan addresses
            'subsystem_actions': {
                'saci': [
                    {'action_type': 'deploy_drones', 'target_area': (lat, lon), 'parameters': {'num_drones': 5, 'flight_pattern': 'grid'}},
                    {'action_type': 'activate_irrigation_system', 'zone': 'sector_alpha'}
                ],
                'curupira': [
                    {'action_type': 'isolate_network_segment', 'target_segment': 'iot_network_A', 'priority': 1},
                    {'action_type': 'block_ip_address', 'ip_address': 'x.x.x.x'}
                ],
                'iara': [
                    {'action_type': 'issue_health_advisory', 'region': 'city_sector_B', 'message_template': 'template_flu_A'}
                ],
                # ... other subsystems as needed (boitata, anhanga)
            },
            'coordination_strategy': 'simultaneous_execution', # Other options: 'sequential_by_priority', 'custom_sequence'
            'overall_priority': 'high', # e.g., 'critical', 'high', 'medium', 'low'
            'estimated_impact_reduction': 0.75, # A score or metric from MetaLearningEngine
            'confidence_in_plan': 0.90 # Confidence in the plan's success
        }
        ```
    *   Each 'action' within `subsystem_actions` is a dictionary specifying `action_type` (a predefined string for what the subsystem should do), `target` (what the action applies to), and `parameters` (any specific values needed for the action). It can also include `priority` if actions within a subsystem need ordering.

4.  **Asynchronous Subsystem Action Execution:**
    *   **Process:** The orchestrator dispatches the relevant parts of the `response_plan` to each concerned subsystem.
    *   Calls to subsystem methods like `subsystem_instance.execute_response_plan(actions_for_subsystem)` are made.
    *   To ensure efficiency and non-blocking operation, these calls are executed concurrently using `asyncio.gather`. This allows the orchestrator to manage multiple subsystem responses simultaneously.
    *   **Return from Subsystems:** Each subsystem's `execute_response_plan` method (which must be an `async` method) is expected to return a status or result for the actions it was tasked with. This could be a list of dictionaries, where each dictionary reports the outcome of an individual action:
        `[{'action_id': 'action_XYZ', 'status': 'success'/'failure'/'in_progress', 'details': '...', 'timestamp': '...'}]`

5.  **Monitoring, Logging, and Learning:**
    *   The results from the subsystem actions are collected and logged.
    *   This outcome data, along with the original `response_plan`, is then fed back into the `MetaLearningEngine` (e.g., via `learn_from_response`) to update its knowledge base and improve future response strategy suggestions.
    *   The `response_history` is updated with the plan, actions taken, and their outcomes.

This conceptual flow aims to create an adaptive and intelligent coordination mechanism.

from fastapi import FastAPI, WebSocket, Query, Body, status, HTTPException, WebSocketDisconnect
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid # For generating event IDs
import asyncio # For WebSocket example

# Import Pydantic models from schemas.py
from .schemas import (
    ThreatEventInput,
    ThreatEventResponse,
    SystemStatusResponse,
    SubsystemStatus, # Needed for SystemStatusResponse
    AlertConfirmationResponse,
    SaciManualAlertRequest
)

# Conceptual: In a real application, the orchestrator might be a class instance
# that this API interacts with, possibly through a dependency injection system.
# from core_logic.guardian_orchestrator import GuardianCentralOrchestrator
# orchestrator = GuardianCentralOrchestrator() # This would need to be async or run in a separate thread

app = FastAPI(
    title="Sistema Guardião - Central API",
    description="Central API Gateway for the Sistema Guardião, providing endpoints for event reporting, system status, and subsystem interactions.",
    version="v1.0.0"
)

# In-memory storage for events (for placeholder purposes)
# In a real system, this would be a database.
db_events: Dict[str, ThreatEventResponse] = {}


@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the Sistema Guardião Central API"}

API_VERSION_PREFIX = "/api/v1"

@app.post(f"{API_VERSION_PREFIX}/events/report",
            response_model=AlertConfirmationResponse,
            status_code=status.HTTP_202_ACCEPTED,
            tags=["Events"],
            summary="Report a new Threat Event")
async def report_threat_event(event_input: ThreatEventInput = Body(..., description="Details of the threat event to report.")):
    """
    Receives a threat event, conceptually validates it, and passes it to the
    GuardianCentralOrchestrator (or stores it in a placeholder DB for now).
    """
    print(f"Received threat event report: {event_input.threat_type} from {event_input.subsystem_source}")

    # Placeholder: Generate event ID and timestamp
    event_id = f"evt_{uuid.uuid4().hex[:10]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.utcnow()

    # Create a ThreatEventResponse object (conceptually, this might come after orchestrator processing)
    full_event_data = ThreatEventResponse(
        event_id=event_id,
        timestamp=timestamp,
        **event_input.model_dump() # Use model_dump() for Pydantic v2+
    )

    # Store in our placeholder DB
    db_events[event_id] = full_event_data

    # Conceptual: Trigger orchestrator processing
    # await orchestrator.coordinate_multi_threat_response([full_event_data_as_internal_model])

    return AlertConfirmationResponse(
        event_id=event_id,
        status="received_and_processing",
        message=f"Threat event '{event_input.threat_type}' from {event_input.subsystem_source} reported successfully. Event ID: {event_id}",
        timestamp=timestamp
    )

@app.get(f"{API_VERSION_PREFIX}/system/status",
           response_model=SystemStatusResponse,
           tags=["System"],
           summary="Get Overall System Status")
async def get_system_status():
    """
    Returns the overall status of Sistema Guardião and its subsystems.
    This is a placeholder and would fetch real status in a production system.
    """
    # Placeholder: Fetch real status from orchestrator or individual subsystems
    # status_from_orchestrator = await orchestrator.get_system_status()

    sample_subsystems = [
        SubsystemStatus(name="SACI", status="operational", alerts_count=2, last_heartbeat=datetime.utcnow()),
        SubsystemStatus(name="CURUPIRA", status="degraded", alerts_count=1, last_heartbeat=datetime.utcnow()),
        SubsystemStatus(name="IARA", status="operational", alerts_count=0, last_heartbeat=datetime.utcnow()),
        SubsystemStatus(name="BOITATA", status="unavailable", alerts_count=0, last_heartbeat=datetime.utcnow()),
        SubsystemStatus(name="ANHANGA", status="operational", alerts_count=0, last_heartbeat=datetime.utcnow()),
    ]

    active_threats = len(db_events) # Placeholder count

    return SystemStatusResponse(
        overall_status="operational_with_some_degraded_subsystems",
        active_threats_count=active_threats,
        subsystems=sample_subsystems,
        timestamp=datetime.utcnow()
    )

@app.get(f"{API_VERSION_PREFIX}/events",
           response_model=List[ThreatEventResponse],
           tags=["Events"],
           summary="List or Filter Threat Events")
async def get_events(
    subsystem: Optional[str] = Query(None, description="Filter events by subsystem source (e.g., 'SACI')."),
    severity_threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Filter events by minimum severity."),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return.")
):
    """
    Returns a list of recent or filtered threat events.
    This is a placeholder and would query a database in a real system.
    """
    print(f"Fetching events with filters: subsystem='{subsystem}', severity_threshold='{severity_threshold}', limit='{limit}'")

    # Placeholder: Filter events from db_events
    results = list(db_events.values())

    if subsystem:
        results = [event for event in results if event.subsystem_source.lower() == subsystem.lower()]

    if severity_threshold is not None:
        results = [event for event in results if event.severity >= severity_threshold]

    return results[:limit]

@app.post(f"{API_VERSION_PREFIX}/saci/manual_alert",
            response_model=AlertConfirmationResponse,
            status_code=status.HTTP_202_ACCEPTED,
            tags=["Subsystems", "SACI"],
            summary="Report a Manual SACI Alert")
async def report_saci_manual_alert(alert_input: SaciManualAlertRequest = Body(..., description="Details for the manual SACI alert.")):
    """
    Triggers a specific alert/action within the SACI subsystem based on manual input.
    Conceptually, this might create a ThreatEvent and send it to the orchestrator
    or directly interact with the SACI subsystem's dedicated API if available.
    """
    print(f"Received SACI manual alert: {alert_input.description} at {alert_input.location}")

    # Placeholder: Convert to a ThreatEvent and process, or directly call SACI
    event_id = f"manual_saci_{uuid.uuid4().hex[:6]}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    timestamp = datetime.utcnow()

    # Example: Create a ThreatEvent-like structure to potentially store or forward
    manual_event_as_threat = ThreatEventResponse(
        event_id=event_id,
        subsystem_source="SACI_MANUAL_INPUT", # Differentiate from automated SACI events
        threat_type="manual_fire_alert", # Specific threat type for manual reports
        severity= (alert_input.urgency / 5.0) if alert_input.urgency else 0.5, # Normalize urgency to severity
        location=alert_input.location,
        timestamp=timestamp,
        metadata={
            "description": alert_input.description,
            "reported_by": alert_input.reported_by,
            **alert_input.metadata
        },
        confidence_score=1.0 # Manual reports often have high confidence initially
    )
    db_events[event_id] = manual_event_as_threat # Store in placeholder DB

    # Conceptual:
    # await orchestrator.coordinate_multi_threat_response([manual_event_as_threat_internal_model])
    # OR: await saci_subsystem_client.trigger_manual_alert(alert_input)

    return AlertConfirmationResponse(
        event_id=event_id,
        status="manual_alert_received",
        message=f"SACI manual alert '{alert_input.description}' received. Event ID: {event_id}",
        timestamp=timestamp
    )

@app.websocket(f"{API_VERSION_PREFIX}/ws/v1/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications.
    Clients connect to this endpoint to receive live updates.

    Conceptual Message Format (Server to Client):
    JSON object representing a summarized ThreatEvent or a specific alert notification.
    Example:
    {
        "alert_id": "evt_...",
        "type": "new_threat_event", // or "event_update", "system_notification"
        "timestamp": "2023-10-27T12:00:00Z",
        "payload": { // Could be a ThreatEventResponse model or a summary
            "event_id": "evt_...",
            "subsystem_source": "SACI",
            "threat_type": "wildfire",
            "severity": 0.8,
            "location": [-19.91, -43.93],
            "message": "High severity wildfire detected near Zone A."
        }
    }
    """
    await websocket.accept()
    print("Client connected to WebSocket /ws/v1/alerts")
    try:
        while True:
            # This is a placeholder. In a real system, this WebSocket would
            # subscribe to a message queue (e.g., Redis Pub/Sub, RabbitMQ, Kafka)
            # where the orchestrator or other services publish new alerts.
            # For now, it just keeps the connection open and could periodically send test messages.

            # Example: Simulating receiving a message from the client (less common for pure notification WebSockets)
            # data = await websocket.receive_text()
            # await websocket.send_text(f"Message text was: {data}")

            # Example: Periodically send a dummy alert (remove in real implementation)
            await asyncio.sleep(15) # Use asyncio.sleep for async websockets
            test_event_id = f"ws_evt_{uuid.uuid4().hex[:6]}"
            dummy_alert_payload = {
                "event_id": test_event_id,
                "subsystem_source": "SYSTEM_TEST",
                "threat_type": "test_alert",
                "severity": 0.5,
                "location": (-0.0, -0.0),
                "message": f"This is a test alert from WebSocket at {datetime.utcnow().isoformat()}"
            }
            await websocket.send_json({
                "alert_id": test_event_id,
                "type": "new_threat_event",
                "timestamp": datetime.utcnow().isoformat(),
                "payload": dummy_alert_payload
            })

    except WebSocketDisconnect:
        print(f"Client disconnected from WebSocket /ws/v1/alerts")
    except Exception as e:
        print(f"Error in WebSocket /ws/v1/alerts: {e}")
        # Attempt to close gracefully if possible
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

if __name__ == "__main__":
    import uvicorn
    # This is for local development/testing of the API directly.
    # In a production setup, a proper ASGI server like Uvicorn or Hypercorn would be used,
    # possibly managed by Docker or another process manager.
    uvicorn.run(app, host="0.0.0.0", port=8000)

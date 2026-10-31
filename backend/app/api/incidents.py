import io
import csv
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.database.models import Incident, DetectionRecord
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut

router = APIRouter(prefix="/incidents", tags=["Incidents"])

@router.get("", response_model=list[IncidentOut])
def list_incidents(
    search: Optional[str] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Incident).order_by(Incident.created_at.desc())
    if status:
        query = query.filter(Incident.status == status.upper())
    if severity:
        query = query.filter(Incident.severity == severity.upper())
    if search:
        term = f"%{search}%"
        query = query.filter(
            (Incident.title.ilike(term)) |
            (Incident.description.ilike(term)) |
            (Incident.location_name.ilike(term))
        )
    return query.all()

@router.post("", response_model=IncidentOut)
def create_incident(incident_in: IncidentCreate, db: Session = Depends(get_db)):
    incident = Incident(
        title=incident_in.title,
        description=incident_in.description or "",
        location_name=incident_in.location_name or "",
        latitude=incident_in.latitude,
        longitude=incident_in.longitude,
        severity=incident_in.severity.upper() if incident_in.severity else "MEDIUM",
        status=incident_in.status.upper() if incident_in.status else "OPEN",
        source_filename=incident_in.source_filename or "",
        associated_detection_id=incident_in.associated_detection_id,
        detection_count=incident_in.detection_count or 0,
        notes=incident_in.notes or ""
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident

@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return incident

@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: str, incident_in: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")

    update_data = incident_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            if field in ["status", "severity"] and isinstance(val, str):
                setattr(incident, field, val.upper())
            else:
                setattr(incident, field, val)

    db.commit()
    db.refresh(incident)
    return incident

@router.delete("/{incident_id}")
def delete_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found.")

    db.delete(incident)
    db.commit()
    return {"success": True, "message": "Incident deleted successfully."}

@router.get("/export/csv")
def export_incidents_csv(db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Incident ID", "Title", "Status", "Severity", "Location",
        "Latitude", "Longitude", "Persons Detected", "Created At", "Notes"
    ])

    for inc in incidents:
        writer.writerow([
            inc.id,
            inc.title,
            inc.status,
            inc.severity,
            inc.location_name,
            inc.latitude or "",
            inc.longitude or "",
            inc.detection_count,
            str(inc.created_at),
            inc.notes
        ])

    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rescue_incidents_report.csv"}
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..crypto import encrypt
from ..db import get_db
from ..llm.base import PROVIDERS
from ..models import Setting
from ..schemas import SettingItem, SettingsView

router = APIRouter(prefix="/api/settings", tags=["settings"])

_KEYS = ["anthropic_api_key", "openai_api_key", "gemini_api_key", "github_token"]


@router.get("", response_model=SettingsView)
def get_settings(db: Session = Depends(get_db)):
    present = {
        row.key: bool(row.value_encrypted)
        for row in db.query(Setting).filter(Setting.key.in_(_KEYS)).all()
    }
    return SettingsView(**{k: present.get(k, False) for k in _KEYS})


@router.put("")
def upsert_setting(item: SettingItem, db: Session = Depends(get_db)):
    if item.key not in _KEYS:
        return {"ok": False, "error": "unknown key"}
    row = db.get(Setting, item.key)
    encrypted = encrypt(item.value) if item.value else b""
    if row:
        row.value_encrypted = encrypted
    else:
        db.add(Setting(key=item.key, value_encrypted=encrypted))
    db.commit()
    return {"ok": True}


@router.delete("/{key}")
def clear_setting(key: str, db: Session = Depends(get_db)):
    row = db.get(Setting, key)
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True}


@router.get("/providers")
def list_providers():
    """What the UI offers in the provider/model dropdowns."""
    return PROVIDERS

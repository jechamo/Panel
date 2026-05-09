from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crypto import encrypt
from ..db import get_db
from ..llm.base import load_catalog
from ..models import Setting
from ..schemas import SettingItem, SettingsView

router = APIRouter(prefix="/api/settings", tags=["settings"])


def _all_setting_keys() -> set[str]:
    """Every key the UI is allowed to write: provider secrets + per-provider extras."""
    keys: set[str] = set()
    for provider, spec in load_catalog().items():
        if spec.get("secret_key"):
            keys.add(spec["secret_key"])
        for extra in spec.get("extra_fields") or []:
            keys.add(f"{provider}__{extra}")
    return keys


@router.get("", response_model=SettingsView)
def get_settings(db: Session = Depends(get_db)):
    rows = db.query(Setting).all()
    present = {row.key: bool(row.value_encrypted) for row in rows}
    # Legacy shape: top-level booleans for the original 4 keys, plus a
    # generic dict for everything else.
    legacy = {
        "anthropic_api_key": present.get("anthropic_api_key", False),
        "openai_api_key": present.get("openai_api_key", False),
        "gemini_api_key": present.get("gemini_api_key", False),
        "github_token": present.get("github_token", False),
    }
    return SettingsView(**legacy, present={k: bool(v) for k, v in present.items()})


@router.put("")
def upsert_setting(item: SettingItem, db: Session = Depends(get_db)):
    allowed = _all_setting_keys()
    if item.key not in allowed:
        raise HTTPException(400, f"Unknown setting key '{item.key}'")
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
    """What the UI offers in the provider/model dropdowns. Reloads on every call."""
    return load_catalog()

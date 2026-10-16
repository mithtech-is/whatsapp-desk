"""Settings / WABA onboarding API for the SPA.

Exposes the WhatsApp Account connection (phone id, token, webhook), the
whatsapp_desk Settings single, teams and agents. Secrets are never returned in
clear text; callers get a boolean `has_token` / `has_app_secret` instead.
"""

from __future__ import annotations

import json

import frappe
from frappe import _

from whatsapp_desk.endpoints.chat import _is_manager

SECRET_FIELDS = ("token", "wd_app_secret")
ACCOUNT_FIELDS = (
    "account_name",
    "status",
    "url",
    "version",
    "phone_id",
    "app_id",
    "business_id",
    "webhook_verify_token",
    "is_default_incoming",
    "is_default_outgoing",
    "wd_calling_enabled",
    "wd_quality_rating",
    "wd_throughput_tier",
    "wd_webhook_last_seen",
)


def _guard_manager():
    if not _is_manager():
        raise frappe.PermissionError(_("Managers only."))


def _webhook_url() -> str:
    return frappe.utils.get_url() + "/api/method/frappe_whatsapp.utils.webhook.webhook"


@frappe.whitelist()
def get_settings():
    _guard_manager()
    accounts = frappe.get_all("WhatsApp Account", pluck="name", order_by="account_name")
    data = []
    for name in accounts:
        doc = frappe.get_doc("WhatsApp Account", name)
        row = {"name": doc.name}
        for f in ACCOUNT_FIELDS:
            row[f] = doc.get(f)
        row["has_token"] = bool(doc.get("token"))
        row["has_app_secret"] = bool(doc.get("wd_app_secret"))
        data.append(row)

    s = frappe.get_single("WhatsApp Settings")
    settings = {
        "wd_phone_masking": s.wd_phone_masking,
        "wd_retention_days": s.wd_retention_days,
        "wd_auto_close_days": s.wd_auto_close_days,
        "wd_voice_enabled": s.wd_voice_enabled,
        "wd_patch_health": s.wd_patch_health,
    }
    return {
        "accounts": data,
        "settings": settings,
        "webhook_url": _webhook_url(),
    }


@frappe.whitelist()
def save_account(payload):
    """Create or update a WhatsApp Account. Secrets only overwritten when provided."""
    _guard_manager()
    if isinstance(payload, str):
        payload = json.loads(payload)

    name = payload.get("name")
    if name and frappe.db.exists("WhatsApp Account", name):
        doc = frappe.get_doc("WhatsApp Account", name)
    else:
        doc = frappe.new_doc("WhatsApp Account")

    for f in ACCOUNT_FIELDS:
        if payload.get(f) is not None:
            doc.set(f, payload[f])

    # Secrets: set only when a non-empty value is supplied.
    for f in SECRET_FIELDS:
        v = payload.get(f)
        if v:
            doc.set(f, v)

    if not doc.get("version"):
        doc.version = "v21.0"

    doc.save()
    frappe.db.commit()
    return {"name": doc.name}


@frappe.whitelist()
def save_settings(payload):
    _guard_manager()
    if isinstance(payload, str):
        payload = json.loads(payload)
    s = frappe.get_single("WhatsApp Settings")
    for f in ("wd_phone_masking", "wd_retention_days", "wd_auto_close_days", "wd_voice_enabled"):
        if payload.get(f) is not None:
            s.set(f, payload[f])
    s.save()
    frappe.db.commit()
    return {"ok": True}


@frappe.whitelist()
def test_connection(account: str):
    """Ping the Meta Graph API for this account's phone number to verify the token."""
    _guard_manager()
    from whatsapp_desk.wa_core import meta_client

    try:
        phone_id = frappe.db.get_value("WhatsApp Account", account, "phone_id")
        if not phone_id:
            return {"ok": False, "error": "No Phone ID set on this account."}
        info = meta_client.get(
            phone_id, account=account, params={"fields": "verified_name,quality_rating"}
        )
        return {"ok": True, "info": info}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@frappe.whitelist()
def teams_and_agents():
    """User Groups (teams) with their members + a flat agent roster."""
    from whatsapp_desk.wa_desk import teams as teams_mod

    team_rows = []
    for g in frappe.get_all("User Group", pluck="name"):
        mem = teams_mod.members(g)
        team_rows.append({"team": g, "members": len(mem), "online": len(teams_mod.online_agents(g))})

    agent_rows = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "System User"},
        fields=["name", "full_name", "wd_wa_availability"],
        order_by="full_name",
        limit=200,
    )
    return {"teams": team_rows, "agents": agent_rows}

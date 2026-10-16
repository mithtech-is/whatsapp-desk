"""Install / migrate lifecycle for whatsapp_desk."""

from __future__ import annotations

import frappe

from whatsapp_desk.setup import analytics, custom_fields, permissions, property_setters, roles, sla


def after_install() -> None:
    _setup()


def after_migrate() -> None:
    _setup()
    # Refresh the health snapshot shown on WhatsApp Settings.
    try:
        from whatsapp_desk.compat import health

        health.refresh_settings_field()
    except Exception:
        pass


def _setup() -> None:
    roles.create()
    custom_fields.create()
    property_setters.create()
    permissions.create()
    sla.ensure_default_sla()
    analytics.ensure_analytics()
    frappe.db.commit()

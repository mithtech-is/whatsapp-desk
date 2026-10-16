app_name = "whatsapp_desk"
app_title = "WhatsApp Desk"
app_publisher = "MithTech"
app_description = (
    "Native-first agent desk, visual chatbot flow builder, SLA and campaigns for the "
    "Frappe WhatsApp apps."
)
app_email = "manoj@polemarch.in"
app_license = "mit"

# ---------------------------------------------------------------------------
# Dependencies — whatsapp_desk is an ADD-ON. It requires all three upstream apps.
# Install order: frappe_whatsapp -> whatsapp_chat -> frappe_whatsapp_chatbot -> whatsapp_desk
# so that our doc_events run AFTER theirs on WhatsApp Message.
# ---------------------------------------------------------------------------
required_apps = [
    "frappe",
    "erpnext",
    "frappe_whatsapp",
    "whatsapp_chat",
    "frappe_whatsapp_chatbot",
]

# ---------------------------------------------------------------------------
# DocType class overrides
# ---------------------------------------------------------------------------
# WhatsApp Message: wrap before_insert with the outbound send guard (window / opt-out /
# rate limit), then call super(). Verified: frappe_whatsapp sends to Meta inside
# before_insert, so this is the single chokepoint every sender funnels through.
override_doctype_class = {
    "WhatsApp Message": "whatsapp_desk.overrides.whatsapp_message.WhatsAppMessageWD",
    "WhatsApp Templates": "whatsapp_desk.overrides.whatsapp_templates.WhatsAppTemplatesWD",
    "Bulk WhatsApp Message": "whatsapp_desk.overrides.bulk_whatsapp_message.BulkWhatsAppMessageWD",
    "WhatsApp Chatbot Flow": "whatsapp_desk.overrides.whatsapp_chatbot_flow.WhatsAppChatbotFlowWD",
}

# ---------------------------------------------------------------------------
# Secured / missing endpoint replacements (§2.1 of the plan).
# NOTE: override_whitelisted_methods remaps the `cmd` string before it is resolved,
# so it also works for methods that don't exist upstream (e.g. set_typing).
# Additional chat-API overrides are added in Phase 0/1 as each is hardened.
# ---------------------------------------------------------------------------
override_whitelisted_methods = {
    # Webhook: HMAC verify + async (§2.1)
    "frappe_whatsapp.utils.webhook.webhook": "whatsapp_desk.endpoints.webhook.webhook",
    # Encrypted Flows data-exchange endpoint (§2.1, #64) — real decryption, upstream was a stub
    "frappe_whatsapp.frappe_whatsapp.api.flow_endpoint.handle_flow_request": "whatsapp_desk.wa_flows.endpoint.handle_flow_request",
    # whatsapp_chat API: permission checks, no contact leak, templates/interactive/status,
    # closed guest path, and the missing set_typing (§2.1)
    "whatsapp_chat.api.message.get_all": "whatsapp_desk.endpoints.chat.get_all",
    "whatsapp_chat.api.message.send": "whatsapp_desk.endpoints.chat.send",
    "whatsapp_chat.api.message.mark_as_read": "whatsapp_desk.endpoints.chat.mark_as_read",
    "whatsapp_chat.api.message.set_typing": "whatsapp_desk.endpoints.chat.set_typing",
    "whatsapp_chat.api.contacts.get": "whatsapp_desk.endpoints.chat.contacts_get",
    "whatsapp_chat.api.contacts.create": "whatsapp_desk.endpoints.chat.contacts_create",
    "whatsapp_chat.api.config.settings": "whatsapp_desk.endpoints.chat.config_settings",
}

# ---------------------------------------------------------------------------
# Document events — our handlers run last (install order).
# ---------------------------------------------------------------------------
doc_events = {
    "WhatsApp Message": {
        "after_insert": "whatsapp_desk.wa_desk.conversation.on_message",
    },
    "WhatsApp Agent Transfer": {
        "after_insert": "whatsapp_desk.wa_desk.assignment.on_agent_transfer",
    },
    # SSRF-harden outbound webhooks targeting WhatsApp Desk doctypes (#66).
    "Webhook": {
        "validate": "whatsapp_desk.wa_platform.webhooks.validate_webhook",
    },
}

# ---------------------------------------------------------------------------
# Fixtures — custom fields & property setters are created programmatically in
# setup/custom_fields.py (idempotent, on install + migrate). Role/permission
# fixtures are exported here once the DocPerms are defined (Phase 0).
# ---------------------------------------------------------------------------
fixtures = [
    {"dt": "Role", "filters": [["name", "in", ["WA Admin", "WA Manager", "WA Agent"]]]},
]

# ---------------------------------------------------------------------------
# SPA at /whatsapp (Phase 1). Vue 3 + frappe-ui, built to public/frontend;
# www/whatsapp.html is the entry (replaced by `yarn copy-html-entry` after build).
# Deep links fall back to the same page for client-side routing.
# ---------------------------------------------------------------------------
website_route_rules = [
    {"from_route": "/whatsapp/<path:app_path>", "to_route": "whatsapp"},
]

# ---------------------------------------------------------------------------
# Install / migrate lifecycle
# ---------------------------------------------------------------------------
after_install = "whatsapp_desk.setup.install.after_install"
after_migrate = "whatsapp_desk.setup.install.after_migrate"

# ---------------------------------------------------------------------------
# Scheduler — retention / log cleanup (stubs wired in Phase 0).
# ---------------------------------------------------------------------------
scheduler_events = {
    "hourly": [
        "whatsapp_desk.wa_desk.sla.tick",
    ],
    "daily": [
        "whatsapp_desk.wa_platform.retention.run_retention",
        "whatsapp_desk.wa_desk.sla.auto_close",
    ],
}

# ---------------------------------------------------------------------------
# Runtime patch layer (§2.2). Guarded monkeypatches on the chatbot engine
# (plain Python classes, not DocTypes). Applied at app import in every process.
# Each patch checks the target signature + installed commit and falls back
# safely on mismatch; status is surfaced on the WhatsApp Settings health page.
# Wrapped so a failure here can never break app load.
# ---------------------------------------------------------------------------
try:
    from whatsapp_desk.compat import patches as _wd_patches

    _wd_patches.apply()
except Exception:  # pragma: no cover - never break app load
    import frappe

    frappe.log_error(frappe.get_traceback(), "whatsapp_desk: patch apply failed at import")

# Installing whatsapp_desk

`whatsapp_desk` is a **native-first add-on**, not a standalone app. It requires Frappe, ERPNext,
and three upstream WhatsApp apps, and it *extends* them (it never forks or replaces them).

---

## 1. Requirements

| Requirement | Version / note |
|-------------|----------------|
| Frappe | **v15 or v16** (validated on v16.20) |
| ERPNext | Required (the conversation model uses ERPNext **Issue + SLA**) |
| Python | 3.10+ |
| Node | Only needed if you rebuild the SPA — a prebuilt bundle ships in `whatsapp_desk/public/frontend` |
| `frappe_whatsapp` | pin `08bc1f6af2e36022d7a5f77641c8ba2ef8c16aaa` (branch `master`) |
| `whatsapp_chat` | pin `4ad3712528e9a56b536bccd190231663f04b8e7b` (branch `develop`) |
| `frappe_whatsapp_chatbot` | pin `e98a655af42be5c0e8cc3912780418e2206d5bdb` (branch `master`) |

The pins are enforced softly at runtime (`whatsapp_desk/compat/pinned.py`): our monkeypatches target
specific upstream code, and each guard **skips with a safe fallback** if upstream has drifted — but
installing the pinned commits is the supported path.

---

## 2. Install order (fresh bench)

```bash
# ERPNext (brings in Frappe)
bench get-app erpnext --branch version-15     # or version-16

# The three upstream WhatsApp apps (use your source URLs), then pin each commit
bench get-app frappe_whatsapp <frappe_whatsapp-repo-url>
bench get-app whatsapp_chat <whatsapp_chat-repo-url> --branch develop
bench get-app frappe_whatsapp_chatbot <frappe_whatsapp_chatbot-repo-url>

# (recommended) pin to the validated commits
( cd apps/frappe_whatsapp        && git checkout 08bc1f6af2e36022d7a5f77641c8ba2ef8c16aaa )
( cd apps/whatsapp_chat          && git checkout 4ad3712528e9a56b536bccd190231663f04b8e7b )
( cd apps/frappe_whatsapp_chatbot && git checkout e98a655af42be5c0e8cc3912780418e2206d5bdb )

# whatsapp_desk itself
bench get-app whatsapp_desk <whatsapp_desk-repo-url>

# Install onto your site (order matters: ERPNext + the 3 apps are installed by required_apps,
# but installing them explicitly first is clearest)
bench --site yoursite.localhost install-app erpnext
bench --site yoursite.localhost install-app frappe_whatsapp whatsapp_chat frappe_whatsapp_chatbot
bench --site yoursite.localhost install-app whatsapp_desk

bench --site yoursite.localhost migrate
bench --site yoursite.localhost clear-cache
bench restart           # or restart your web + worker containers
```

`install-app whatsapp_desk` runs `after_install`, which creates: all `wd_*` custom fields, the
WA Admin/Manager/Agent roles, the WhatsApp SLA (enabling ERPNext *Support Settings →
track_service_level_agreement*), the analytics Number Cards / Dashboard Charts / Query Reports, and
the **WhatsApp Desk** workspace. `migrate` creates the 6 add-on DocTypes.

---

## 3. Post-install configuration

### 3a. The bot/flow worker queue (REQUIRED for the chatbot)
The async chatbot enqueues jobs to a dedicated **`wa_bot`** RQ queue. Your workers must listen on it
or bot/flow jobs never run. Add `wa_bot` to a worker's queue list:

```bash
# bench (Procfile) dev:
bench worker --queue wa_bot,long,default,short

# production (supervisor / docker): add wa_bot to an existing worker's --queue list,
# e.g.  --queue long,default,short,wa_bot
```

### 3b. Connect WhatsApp Business
In the app (**/whatsapp → Settings → Connection**) or in Desk (**WhatsApp Account**):
- `Phone ID`, `Token`, `Business ID`, `App ID`
- Set the **webhook** in Meta → WhatsApp → Configuration to the URL shown on the Settings screen:
  `https://<your-domain>/api/method/frappe_whatsapp.utils.webhook.webhook`
  (Meta requires a **public HTTPS** URL — localhost will not receive webhooks.)
- Choose a **Webhook Verify Token** and enter the same value in Meta.

### 3c. Optional
- **WhatsApp Flows (encrypted forms):** set `WhatsApp Settings → wd_flows_private_key` (PEM).
- **Voice/calling:** `WhatsApp Settings → Enable Voice`. Real audio additionally needs Meta Calling
  API access and a media bridge (VPS) — not required for call logs or IVR design.

---

## 4. Using it
Open **`https://<your-domain>/whatsapp`** (login required; guests are redirected to `/login`).
Nav: Inbox · Flows · Campaigns · Calls · Templates · Analytics · Settings.

---

## 5. Rebuilding the SPA (only if you change the frontend)
A prebuilt bundle ships in the repo, so this is **not** needed for a normal install.

```bash
cd apps/whatsapp_desk/frontend
yarn install
yarn build        # outputs to ../whatsapp_desk/public/frontend + www/whatsapp.html
```
> Build on the **native OS of your node install** — a `node_modules` built on Windows won't run
> under WSL/Linux (esbuild/rollup ship per-platform native binaries).

---

## 6. Production checklist
- [ ] Upstream apps pinned to the commits in §1
- [ ] `wa_bot` added to a worker queue (§3a)
- [ ] WhatsApp Account connected + public HTTPS webhook verified (§3b)
- [ ] `bench --site <site> migrate` run clean
- [ ] CSRF left **on** (do **not** set `ignore_csrf`; the app ships `www/whatsapp.py` which injects the token)
- [ ] Remove any demo/seed data if you loaded it

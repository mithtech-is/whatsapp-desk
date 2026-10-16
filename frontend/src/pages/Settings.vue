<script setup>
import { ref, onMounted } from 'vue'
import { call } from 'frappe-ui'

const loading = ref(true)
const forbidden = ref(false)
const accounts = ref([])
const settings = ref({})
const webhookUrl = ref('')
const teams = ref([])
const agents = ref([])

const active = ref('connection')
const editing = ref(null)        // account being edited (clone)
const saving = ref(false)
const msg = ref('')
const testResult = ref(null)
const copied = ref(false)

async function load() {
  loading.value = true; forbidden.value = false
  try {
    const r = await call('whatsapp_desk.api.v1.settings.get_settings')
    accounts.value = r.accounts
    settings.value = r.settings
    webhookUrl.value = r.webhook_url
    const ta = await call('whatsapp_desk.api.v1.settings.teams_and_agents')
    teams.value = ta.teams; agents.value = ta.agents
  } catch (e) {
    if (e.exc_type === 'PermissionError' || /Managers/.test(e.message || '')) forbidden.value = true
    else msg.value = e.message || 'Failed to load.'
  } finally { loading.value = false }
}

function edit(a) {
  testResult.value = null; msg.value = ''
  editing.value = { ...a, token: '', wd_app_secret: '' }   // secrets blank; only sent if typed
}
function newAccount() {
  editing.value = {
    name: '', account_name: '', url: 'https://graph.facebook.com', version: 'v21.0',
    phone_id: '', app_id: '', business_id: '', webhook_verify_token: '',
    token: '', wd_app_secret: '', is_default_incoming: 1, is_default_outgoing: 1,
  }
}
async function saveAccount() {
  saving.value = true; msg.value = ''
  try {
    await call('whatsapp_desk.api.v1.settings.save_account', { payload: JSON.stringify(editing.value) })
    editing.value = null
    await load()
    msg.value = 'Saved.'
  } catch (e) { msg.value = e.message || 'Save failed.' }
  finally { saving.value = false }
}
async function testConn(a) {
  testResult.value = { account: a.name, loading: true }
  const r = await call('whatsapp_desk.api.v1.settings.test_connection', { account: a.name })
  testResult.value = { account: a.name, ...r }
}
function copyWebhook() {
  navigator.clipboard?.writeText(webhookUrl.value)
  copied.value = true; setTimeout(() => (copied.value = false), 1500)
}
onMounted(load)
</script>

<template>
  <div class="se">
    <header class="se__head">
      <div>
        <h1>Settings</h1>
        <p>Connect WhatsApp Business, manage teams &amp; agents, and tune retention.</p>
      </div>
    </header>

    <div v-if="loading" class="se__empty">Loading…</div>
    <div v-else-if="forbidden" class="se__empty">
      <div class="se__art">🔒</div>
      <p>Settings are available to managers only.</p>
    </div>

    <template v-else>
      <div class="se__tabs">
        <button :class="{ on: active === 'connection' }" @click="active = 'connection'">🔌 Connection</button>
        <button :class="{ on: active === 'team' }" @click="active = 'team'">👥 Teams &amp; Agents</button>
        <button :class="{ on: active === 'ops' }" @click="active = 'ops'">⚙️ Retention &amp; Ops</button>
      </div>

      <!-- CONNECTION -->
      <section v-if="active === 'connection'">
        <div class="webhook">
          <div>
            <div class="webhook__label">Webhook URL · set this in Meta → WhatsApp → Configuration</div>
            <code class="webhook__url">{{ webhookUrl }}</code>
          </div>
          <button class="btn" @click="copyWebhook">{{ copied ? '✓ Copied' : 'Copy' }}</button>
        </div>

        <div class="acc__list">
          <div v-for="a in accounts" :key="a.name" class="acc">
            <div class="acc__main">
              <div class="acc__name">{{ a.account_name || a.name }}
                <span class="st" :data-s="(a.status || '').toLowerCase()">{{ a.status || '—' }}</span>
              </div>
              <div class="acc__meta">
                <span>📱 {{ a.phone_id || 'no phone id' }}</span>
                <span>🔑 token {{ a.has_token ? 'set' : 'missing' }}</span>
                <span v-if="a.wd_quality_rating">⭐ {{ a.wd_quality_rating }}</span>
                <span v-if="a.wd_webhook_last_seen">🕑 seen {{ a.wd_webhook_last_seen }}</span>
              </div>
            </div>
            <div class="acc__act">
              <button class="mini" @click="testConn(a)">Test</button>
              <button class="mini" @click="edit(a)">Edit</button>
            </div>
            <div v-if="testResult && testResult.account === a.name" class="acc__test" :class="{ ok: testResult.ok, bad: testResult.ok === false }">
              <template v-if="testResult.loading">Testing…</template>
              <template v-else-if="testResult.ok">✓ Connected — {{ testResult.info?.verified_name || 'OK' }}</template>
              <template v-else>✕ {{ testResult.error }}</template>
            </div>
          </div>
          <button class="acc__add" @click="newAccount">＋ Add WhatsApp Account</button>
        </div>
      </section>

      <!-- TEAMS -->
      <section v-else-if="active === 'team'">
        <div class="cols">
          <div class="panel">
            <h2>Teams</h2>
            <div v-for="t in teams" :key="t.team" class="line">
              <span class="line__name">👥 {{ t.team }}</span>
              <span class="line__meta">{{ t.online }}/{{ t.members }} online</span>
            </div>
            <p v-if="!teams.length" class="muted">No teams. Create User Groups in Desk.</p>
            <a class="btn btn--ghost" href="/app/user-group/new" target="_blank">＋ New Team (Desk)</a>
          </div>
          <div class="panel">
            <h2>Agents</h2>
            <div v-for="ag in agents" :key="ag.name" class="line">
              <span class="line__name">{{ ag.full_name || ag.name }}</span>
              <span class="dotstate" :data-s="(ag.wd_wa_availability || 'offline').toLowerCase()">{{ ag.wd_wa_availability || 'Offline' }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- OPS -->
      <section v-else class="panel panel--narrow">
        <h2>Retention &amp; Operations</h2>
        <div class="kv"><span>Log retention (days)</span><b>{{ settings.wd_retention_days ?? '—' }}</b></div>
        <div class="kv"><span>Auto-close resolved after (days)</span><b>{{ settings.wd_auto_close_days ?? '—' }}</b></div>
        <div class="kv"><span>Phone masking</span><b>{{ settings.wd_phone_masking ? 'On' : 'Off' }}</b></div>
        <div class="kv"><span>Voice (calling)</span><b>{{ settings.wd_voice_enabled ? 'Enabled' : 'Disabled' }}</b></div>
        <div class="health" v-if="settings.wd_patch_health">
          <div class="health__label">Patch &amp; override health</div>
          <pre>{{ settings.wd_patch_health }}</pre>
        </div>
        <a class="btn btn--ghost" href="/app/whatsapp-settings" target="_blank">Edit in Desk ↗</a>
      </section>

      <p v-if="msg" class="se__msg">{{ msg }}</p>
    </template>

    <!-- Account editor -->
    <div v-if="editing" class="modal">
      <div class="modal__backdrop" @click="editing = null" />
      <div class="modal__box">
        <header class="modal__head">
          <h2>{{ editing.name ? 'Edit' : 'New' }} WhatsApp Account</h2>
          <button class="modal__close" @click="editing = null">×</button>
        </header>
        <div class="modal__body">
          <div class="grid2">
            <label>Account name<input v-model="editing.account_name" placeholder="Main line" /></label>
            <label>Phone ID<input v-model="editing.phone_id" placeholder="1234567890" /></label>
            <label>Business ID<input v-model="editing.business_id" /></label>
            <label>App ID<input v-model="editing.app_id" /></label>
            <label>Graph URL<input v-model="editing.url" /></label>
            <label>API version<input v-model="editing.version" /></label>
          </div>
          <div class="grid2">
            <label>Access token <span class="opt">{{ editing.name ? '(leave blank to keep)' : '' }}</span>
              <input v-model="editing.token" type="password" placeholder="EAAG…" /></label>
            <label>App secret <span class="opt">{{ editing.name ? '(leave blank to keep)' : '' }}</span>
              <input v-model="editing.wd_app_secret" type="password" placeholder="•••" /></label>
          </div>
          <label>Webhook verify token<input v-model="editing.webhook_verify_token" placeholder="a-secret-you-choose" /></label>
          <div class="grid2">
            <label class="chk"><input type="checkbox" v-model="editing.is_default_incoming" :true-value="1" :false-value="0" /> Default incoming</label>
            <label class="chk"><input type="checkbox" v-model="editing.is_default_outgoing" :true-value="1" :false-value="0" /> Default outgoing</label>
          </div>
          <p class="modal__hint">🔒 For security, enter these yourself — tokens are stored encrypted and never shown back.</p>
        </div>
        <footer class="modal__foot">
          <button class="btn" @click="editing = null">Cancel</button>
          <button class="btn btn--green" :disabled="saving" @click="saveAccount">{{ saving ? 'Saving…' : 'Save Account' }}</button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.se { height: 100vh; overflow-y: auto; background: #f8fafc; color: #0f172a; padding: 28px 32px; }
.se__head { margin-bottom: 20px; }
.se__head h1 { font-size: 24px; font-weight: 700; }
.se__head p { color: #64748b; font-size: 14px; margin-top: 2px; }
.se__empty { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 70px 0; color: #94a3b8; }
.se__art { font-size: 44px; opacity: 0.6; }
.btn { font-size: 13px; font-weight: 600; padding: 9px 15px; border-radius: 10px; border: 1px solid #e5e7eb; background: #fff; color: #334155; cursor: pointer; display: inline-block; text-decoration: none; }
.btn:hover { background: #f1f5f9; }
.btn--green { background: #10b981; border-color: #10b981; color: #fff; }
.btn--green:hover { background: #059669; }
.btn--ghost { margin-top: 12px; color: #16a34a; border-color: #bbf7d0; }

.se__tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.se__tabs button { font-size: 13px; font-weight: 600; padding: 8px 15px; border-radius: 999px; color: #64748b; background: #fff; border: 1px solid #e5e7eb; }
.se__tabs button.on { background: #0b3d2e; color: #fff; border-color: #0b3d2e; }

.webhook { display: flex; align-items: center; gap: 14px; background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px; margin-bottom: 18px; }
.webhook > div { flex: 1; min-width: 0; }
.webhook__label { font-size: 12px; color: #64748b; margin-bottom: 6px; }
.webhook__url { display: block; font-family: ui-monospace, monospace; font-size: 12px; color: #0f172a; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 8px; padding: 7px 10px; overflow-x: auto; white-space: nowrap; }

.acc__list { display: flex; flex-direction: column; gap: 12px; }
.acc { background: #fff; border: 1px solid #e5e7eb; border-radius: 14px; padding: 16px 18px; display: grid; grid-template-columns: 1fr auto; gap: 8px 12px; align-items: center; }
.acc__name { font-weight: 700; font-size: 15px; display: flex; align-items: center; gap: 8px; }
.acc__meta { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12px; color: #64748b; margin-top: 4px; }
.acc__act { display: flex; gap: 6px; }
.acc__test { grid-column: 1 / -1; font-size: 12px; font-weight: 600; padding: 7px 10px; border-radius: 8px; background: #f1f5f9; color: #475569; }
.acc__test.ok { background: #dcfce7; color: #15803d; }
.acc__test.bad { background: #fee2e2; color: #b91c1c; }
.acc__add { background: #fff; border: 1px dashed #cbd5e1; border-radius: 14px; padding: 14px; color: #16a34a; font-weight: 600; font-size: 13px; }
.acc__add:hover { background: #f0fdf4; }
.mini { font-size: 12px; font-weight: 600; padding: 6px 12px; border-radius: 8px; border: 1px solid #e5e7eb; background: #fff; color: #475569; }
.mini:hover { background: #f1f5f9; }
.st { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: #f1f5f9; color: #64748b; }
.st[data-s="active"] { background: #dcfce7; color: #15803d; }

.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.panel { background: #fff; border: 1px solid #e5e7eb; border-radius: 16px; padding: 20px; }
.panel--narrow { max-width: 560px; }
.panel h2 { font-size: 14px; font-weight: 700; margin-bottom: 14px; }
.line { display: flex; align-items: center; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
.line:last-child { border-bottom: none; }
.line__name { font-weight: 600; }
.line__meta { font-size: 12px; color: #94a3b8; }
.dotstate { font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 999px; background: #f1f5f9; color: #94a3b8; }
.dotstate[data-s="online"] { background: #dcfce7; color: #15803d; }
.dotstate[data-s="away"] { background: #fef3c7; color: #b45309; }
.muted { color: #94a3b8; font-size: 13px; }

.kv { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
.kv span { color: #64748b; }
.health { margin-top: 14px; }
.health__label { font-size: 12px; font-weight: 600; color: #475569; margin-bottom: 6px; }
.health pre { font-size: 11px; background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px; overflow-x: auto; white-space: pre-wrap; color: #334155; }
.se__msg { margin-top: 14px; font-size: 13px; color: #15803d; }

.modal { position: fixed; inset: 0; z-index: 50; display: grid; place-items: center; }
.modal__backdrop { position: absolute; inset: 0; background: rgba(2,6,23,0.4); }
.modal__box { position: relative; width: 640px; max-width: 94vw; max-height: 90vh; overflow-y: auto; background: #fff; border-radius: 18px; box-shadow: 0 24px 60px rgba(2,6,23,0.25); }
.modal__head { display: flex; align-items: center; padding: 18px 22px; border-bottom: 1px solid #f1f5f9; }
.modal__head h2 { font-size: 17px; font-weight: 700; }
.modal__close { margin-left: auto; font-size: 24px; color: #94a3b8; line-height: 1; }
.modal__body { padding: 20px 22px; display: flex; flex-direction: column; gap: 14px; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.modal__body label { display: flex; flex-direction: column; gap: 5px; font-size: 12px; font-weight: 600; color: #475569; }
.opt { font-weight: 400; color: #94a3b8; }
.modal__body input { border: 1px solid #e5e7eb; border-radius: 9px; padding: 8px 11px; font-size: 13px; font-weight: 400; color: #0f172a; outline: none; }
.modal__body input:focus { border-color: #10b981; }
.chk { flex-direction: row !important; align-items: center; gap: 8px !important; }
.chk input { width: auto; }
.modal__hint { font-size: 12px; color: #64748b; background: #f0fdf4; border: 1px solid #dcfce7; border-radius: 10px; padding: 9px 12px; }
.modal__foot { display: flex; justify-content: flex-end; gap: 10px; padding: 16px 22px; border-top: 1px solid #f1f5f9; }
@media (max-width: 820px) { .cols { grid-template-columns: 1fr; } }
</style>

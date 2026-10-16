<script setup>
import { computed } from 'vue'
import { Handle, Position, useVueFlow } from '@vue-flow/core'

const props = defineProps({
  id: String,
  type: String,
  data: { type: Object, default: () => ({}) },
  selected: Boolean,
})

const { removeNodes } = useVueFlow()

const CONFIG = {
  start: { icon: '▶', color: '#16a34a', title: 'Start', target: false, sources: () => [{ id: null }] },
  text: { icon: '💬', color: '#2563eb', title: 'Send message', sources: () => [{ id: null }] },
  say: { icon: '🗣', color: '#2563eb', title: 'Say', sources: () => [{ id: null }] },
  greeting: { icon: '👋', color: '#2563eb', title: 'Greeting', sources: () => [{ id: null }] },
  media: { icon: '🖼', color: '#2563eb', title: 'Send media', sources: () => [{ id: null }] },
  input: { icon: '⌨️', color: '#7c3aed', title: 'Collect input', sources: () => [{ id: null }] },
  gather: { icon: '☎️', color: '#7c3aed', title: 'Gather', sources: () => [{ id: null }] },
  buttons: { icon: '🔘', color: '#d97706', title: 'Buttons', sources: (dd) => [
    ...(dd.buttons || []).map((b) => ({ id: b.id, label: b.title || b.id })), { id: 'fallback', label: 'fallback' }] },
  menu: { icon: '🔢', color: '#d97706', title: 'Menu', sources: (dd) => [
    ...(dd.buttons || []).map((b) => ({ id: b.id, label: b.title || b.id })), { id: 'fallback', label: 'fallback' }] },
  list: { icon: '📋', color: '#d97706', title: 'Native list', sources: (dd) => [
    ...((dd.sections || []).flatMap((s) => (s.rows || []).map((r) => ({ id: r.id, label: r.title || r.id })))),
    { id: 'fallback', label: 'fallback' }] },
  poll: { icon: '📊', color: '#d97706', title: 'Poll', sources: (dd) => [
    ...((dd.options || []).map((o) => ({ id: o.id, label: o.title || o.id }))),
    { id: 'fallback', label: 'fallback' }] },
  condition: { icon: '◇', color: '#ca8a04', title: 'Condition', sources: () => [
    { id: 'true', label: 'true' }, { id: 'false', label: 'false' }] },
  condition_router: { icon: '🔀', color: '#ca8a04', title: 'Condition router', sources: (dd) => [
    ...((dd.conditions || []).map((c) => ({ id: c.id, label: c.label || c.id }))),
    { id: 'default', label: 'default' }] },
  response_saver: { icon: '💾', color: '#7c3aed', title: 'Response saver', sources: () => [{ id: null }] },
  delay: { icon: '⏱', color: '#64748b', title: 'Delay', sources: () => [{ id: null }] },
  disable_auto_reply: { icon: '🤖', color: '#dc2626', title: 'Disable auto-reply', sources: () => [{ id: null }] },
  set_labels: { icon: '🏷', color: '#059669', title: 'Set chat labels', sources: () => [{ id: null }] },
  phonebook: { icon: '📒', color: '#059669', title: 'Phonebook manager', sources: () => [{ id: null }] },
  wa_form: { icon: '📝', color: '#2563eb', title: 'Send WA form', sources: () => [{ id: null }] },
  make_request: { icon: '🌐', color: '#0284c7', title: 'Make request', sources: () => [
    { id: 'success', label: 'success' }, { id: 'error', label: 'error' }] },
  google: { icon: '🧩', color: '#94a3b8', title: 'Google services (soon)', sources: () => [{ id: null }] },
  set_variable: { icon: '🔧', color: '#0891b2', title: 'Set variable', sources: () => [{ id: null }] },
  api_call: { icon: '🌐', color: '#0284c7', title: 'API call', sources: () => [
    { id: 'success', label: 'success' }, { id: 'error', label: 'error' }] },
  http_callback: { icon: '🌐', color: '#0284c7', title: 'HTTP callback', sources: () => [
    { id: 'success', label: 'success' }, { id: 'error', label: 'error' }] },
  webhook: { icon: '📡', color: '#0284c7', title: 'Webhook', sources: () => [{ id: null }] },
  assign: { icon: '👤', color: '#db2777', title: 'Assign agent', sources: () => [{ id: null }] },
  tag: { icon: '🏷', color: '#059669', title: 'Add tag', sources: () => [{ id: null }] },
  note: { icon: '📝', color: '#059669', title: 'Add note', sources: () => [{ id: null }] },
  timing: { icon: '⏱', color: '#64748b', title: 'Wait', sources: () => [{ id: null }] },
  transfer: { icon: '🙋', color: '#db2777', title: 'Handoff to agent', sources: () => [] },
  goto: { icon: '↪', color: '#9333ea', title: 'Go to flow', sources: () => [] },
  goto_flow: { icon: '↪', color: '#9333ea', title: 'Go to flow', sources: () => [] },
  end: { icon: '⏹', color: '#dc2626', title: 'End', sources: () => [] },
  hangup: { icon: '📴', color: '#dc2626', title: 'Hang up', sources: () => [] },
  ai_response: { icon: '✨', color: '#0d9488', title: 'AI response', sources: () => [
    { id: 'continue', label: 'continue' }, { id: 'handoff', label: 'handoff' }] },
}
const cfg = computed(() => CONFIG[props.type] || { icon: '●', color: '#64748b', title: props.type, sources: () => [{ id: null }] })
const hasTarget = computed(() => cfg.value.target !== false)
const sources = computed(() => cfg.value.sources(props.data || {}))

const d = computed(() => props.data)
const t = computed(() => props.type)
const isMsg = computed(() => ['text', 'say', 'greeting'].includes(t.value))
const isInput = computed(() => ['input', 'gather'].includes(t.value))
const isBtns = computed(() => ['buttons', 'menu'].includes(t.value))
const isApi = computed(() => ['api_call', 'http_callback'].includes(t.value))
const isEnd = computed(() => ['end', 'hangup'].includes(t.value))
const isWebhook = computed(() => t.value === 'webhook')
const isList = computed(() => t.value === 'list')
const isPoll = computed(() => t.value === 'poll')
const isMedia = computed(() => t.value === 'media')
const isRouter = computed(() => t.value === 'condition_router')
const isMakeReq = computed(() => t.value === 'make_request')
const isDelay = computed(() => t.value === 'delay')
const isForm = computed(() => t.value === 'wa_form')

function addButton() { if (!d.value.buttons) d.value.buttons = []; d.value.buttons.push({ id: 'opt' + (d.value.buttons.length + 1), title: '' }) }
function removeButton(i) { d.value.buttons.splice(i, 1) }
function addAssign() { if (!d.value.assignments) d.value.assignments = []; d.value.assignments.push({ name: '', value: '' }) }
function removeAssign(i) { d.value.assignments.splice(i, 1) }
function addSection() { if (!d.value.sections) d.value.sections = []; d.value.sections.push({ title: 'Section', rows: [] }) }
function removeSection(i) { d.value.sections.splice(i, 1) }
function addRow(si) { const s = d.value.sections[si]; if (!s.rows) s.rows = []; s.rows.push({ id: 'r' + (s.rows.length + 1), title: '', description: '' }) }
function removeRow(si, i) { d.value.sections[si].rows.splice(i, 1) }
function addOption() { if (!d.value.options) d.value.options = []; d.value.options.push({ id: 'o' + (d.value.options.length + 1), title: '' }) }
function removeOption(i) { d.value.options.splice(i, 1) }
function addCondition() {
  if (!d.value.conditions) d.value.conditions = []
  d.value.conditions.push({ id: 'c' + (d.value.conditions.length + 1), variable: 'senderMessage',
                            match: 'Exact Match', case_sensitive: false, value: '' })
}
function removeCondition(i) { d.value.conditions.splice(i, 1) }
function addLabel(key) { if (!d.value[key]) d.value[key] = []; d.value[key].push('') }
function removeLabel(key, i) { d.value[key].splice(i, 1) }
function parseJsonInto(key, raw) {
  d.value[key + '_json'] = raw
  try { d.value[key] = JSON.parse(raw || '{}') } catch (e) { /* let the user keep typing */ }
}
function del() { removeNodes([props.id]) }
</script>

<template>
  <div class="nd" :class="{ 'nd--sel': selected }" :style="{ '--accent': cfg.color }">
    <Handle v-if="hasTarget" type="target" :position="Position.Left" class="hdl hdl--in" />

    <header class="nd__head">
      <span class="nd__icon">{{ cfg.icon }}</span>
      <input class="nd__title nodrag" :value="d.label || ''" :placeholder="cfg.title" @input="d.label = $event.target.value" />
      <button class="nd__del nodrag" title="Delete" @click="del">×</button>
    </header>

    <div class="nd__form nodrag nowheel">
      <!-- initial node -->
      <template v-if="t === 'start'">
        <select v-model="d.trigger_type"><option>Chatbot</option><option>Keyword</option><option>Default</option></select>
        <textarea v-model="d.initial_message" rows="2" placeholder="Greeting message…" />
        <input v-model="d.trigger_keywords" placeholder="Triggers: hi, hello" />
        <small class="nd__hint" v-pre>
          Available: <b>{{senderName}}</b>, <b>{{senderMessage}}</b>, <b>{{CustomInput}}</b>
        </small>
      </template>

      <!-- message -->
      <template v-else-if="isMsg">
        <select v-model="d.message_type"><option>Text</option><option>Template</option></select>
        <textarea v-if="d.message_type !== 'Template'" v-model="d.message" rows="3" placeholder="Message… use {{ name }}" />
        <template v-else>
          <input v-model="d.template" placeholder="template_name" />
          <div class="nd__grid">
            <input v-model="d.template_language" placeholder="lang (en)" />
            <input v-model="d.template_params_csv" placeholder="body params, csv (uses {{var}})"
                   @input="d.template_components = [{ type: 'body', parameters: ($event.target.value || '').split(',').map(s => ({ type: 'text', text: s.trim() })) }]" />
          </div>
        </template>
      </template>

      <!-- media -->
      <template v-else-if="isMedia">
        <select v-model="d.media_type"><option>image</option><option>video</option><option>document</option><option>audio</option></select>
        <input v-model="d.media_url" placeholder="https://…/file" />
        <textarea v-if="d.media_type !== 'audio'" v-model="d.caption" rows="2" placeholder="Caption (optional)" />
        <input v-if="d.media_type === 'document'" v-model="d.filename" placeholder="filename.pdf" />
      </template>

      <!-- input -->
      <template v-else-if="isInput">
        <textarea v-model="d.message" rows="2" placeholder="Prompt, e.g. What's your name?" />
        <div class="nd__grid">
          <input v-model="d.store_as" placeholder="store as" />
          <select v-model="d.input_type"><option>Text</option><option>Number</option><option>Email</option><option>Phone</option><option>Date</option></select>
        </div>
      </template>

      <!-- buttons -->
      <template v-else-if="isBtns">
        <textarea v-model="d.message" rows="2" placeholder="Message…" />
        <div class="nd__sub">
          <span>Buttons <small>(≤3 → buttons, 4-10 → list)</small></span>
          <button class="nd__add nodrag" @click="addButton">+ Add</button>
        </div>
        <div v-for="(b, i) in d.buttons || []" :key="i" class="nd__brow">
          <input v-model="b.id" class="nd__bid" placeholder="id" />
          <input v-model="b.title" placeholder="Button label" />
          <button class="nd__x nodrag" @click="removeButton(i)">×</button>
        </div>
      </template>

      <!-- list (native WhatsApp list; sections of rows) -->
      <template v-else-if="isList">
        <textarea v-model="d.message" rows="2" placeholder="Message…" />
        <input v-model="d.list_button" placeholder="CTA button (e.g. Choose)" />
        <div class="nd__sub"><span>Sections</span><button class="nd__add nodrag" @click="addSection">+ Section</button></div>
        <div v-for="(s, si) in d.sections || []" :key="si" class="nd__sec">
          <div class="nd__brow">
            <input v-model="s.title" placeholder="Section title" />
            <button class="nd__x nodrag" @click="removeSection(si)">×</button>
          </div>
          <div v-for="(r, i) in s.rows || []" :key="i" class="nd__brow">
            <input v-model="r.id" class="nd__bid" placeholder="id" />
            <input v-model="r.title" placeholder="Row title" />
            <button class="nd__x nodrag" @click="removeRow(si, i)">×</button>
          </div>
          <button class="nd__add nodrag" @click="addRow(si)">+ Row</button>
        </div>
      </template>

      <!-- poll (interactive poll) -->
      <template v-else-if="isPoll">
        <textarea v-model="d.message" rows="2" placeholder="Poll question…" />
        <label class="nd__check"><input type="checkbox" v-model="d.multiple" /> Allow multiple answers</label>
        <div class="nd__sub"><span>Options</span><button class="nd__add nodrag" @click="addOption">+ Add</button></div>
        <div v-for="(o, i) in d.options || []" :key="i" class="nd__brow">
          <input v-model="o.id" class="nd__bid" placeholder="id" />
          <input v-model="o.title" placeholder="Option" />
          <button class="nd__x nodrag" @click="removeOption(i)">×</button>
        </div>
      </template>

      <!-- condition -->
      <template v-else-if="t === 'condition'">
        <textarea v-model="d.expression" rows="2" class="mono"
                  placeholder="message.lower() == 'yes' or contact.get('wd_team') == 'VIP'" />
        <small class="nd__hint">available: <b>message</b>, <b>contact.*</b>, <b>vars</b>, your variable names</small>
      </template>

      <!-- condition router (Polyg-style multi-row) -->
      <template v-else-if="isRouter">
        <div class="nd__sub"><span>Conditions</span><button class="nd__add nodrag" @click="addCondition">+ Add Condition</button></div>
        <div v-for="(c, i) in d.conditions || []" :key="i" class="nd__rrow">
          <div class="nd__brow">
            <input v-model="c.id" class="nd__bid" placeholder="id" />
            <input v-model="c.variable" placeholder="variable (senderMessage)" />
            <button class="nd__x nodrag" @click="removeCondition(i)">×</button>
          </div>
          <div class="nd__grid">
            <select v-model="c.match">
              <option>Exact Match</option><option>Contains</option><option>Regex</option>
            </select>
            <input v-model="c.value" placeholder="value" />
          </div>
          <label class="nd__check"><input type="checkbox" v-model="c.case_sensitive" /> Case sensitive</label>
        </div>
        <small class="nd__hint">no match → <b>default</b> branch</small>
      </template>

      <!-- set_variable -->
      <template v-else-if="t === 'set_variable'">
        <div class="nd__sub"><span>Assignments</span><button class="nd__add nodrag" @click="addAssign">+ Add</button></div>
        <div v-for="(a, i) in d.assignments || []" :key="i" class="nd__brow">
          <input v-model="a.name" class="nd__bid" placeholder="name" />
          <input v-model="a.value" placeholder="value" />
          <button class="nd__x nodrag" @click="removeAssign(i)">×</button>
        </div>
      </template>

      <!-- api_call -->
      <template v-else-if="isApi">
        <input v-model="d.url" placeholder="https://api…/x" />
        <div class="nd__grid">
          <select v-model="d.method"><option>GET</option><option>POST</option></select>
          <input v-model="d.store_as" placeholder="store as" />
        </div>
        <input v-model="d.response_path" placeholder="response path e.g. data.x" />
      </template>

      <!-- webhook (fire-and-forget POST) -->
      <template v-else-if="isWebhook">
        <input v-model="d.url" placeholder="https://your-webhook/endpoint" />
        <small class="nd__hint">POST, body includes message, vars, contact, issue</small>
      </template>

      <!-- make request (full HTTP: method/headers/body) -->
      <template v-else-if="isMakeReq">
        <input v-model="d.url" placeholder="https://api.example.com/x" />
        <div class="nd__grid">
          <select v-model="d.method">
            <option>GET</option><option>POST</option><option>PUT</option><option>PATCH</option><option>DELETE</option>
          </select>
          <input v-model="d.store_as" placeholder="response → variable" />
        </div>
        <textarea :value="d.headers_json" rows="2" class="mono"
                  placeholder="headers JSON — tokens in {{ var }} notation"
                  @input="parseJsonInto('headers', $event.target.value)" />
        <textarea :value="d.body_json" rows="2" class="mono"
                  placeholder="body JSON — tokens in {{ var }} notation"
                  @input="parseJsonInto('body', $event.target.value)" />
      </template>

      <!-- response saver -->
      <template v-else-if="t === 'response_saver'">
        <textarea v-model="d.message" rows="2" placeholder="Prompt the user…" />
        <input v-model="d.store_as" placeholder="variable name" />
      </template>

      <!-- delay -->
      <template v-else-if="isDelay">
        <div class="nd__grid">
          <input v-model.number="d.amount" type="number" placeholder="30" />
          <select v-model="d.unit"><option>seconds</option><option>minutes</option></select>
        </div>
      </template>

      <!-- disable auto-reply -->
      <template v-else-if="t === 'disable_auto_reply'">
        <small class="nd__hint">Turns off this conversation's bot until a human re-enables it.</small>
      </template>

      <!-- set labels (add + remove) -->
      <template v-else-if="t === 'set_labels'">
        <div class="nd__sub"><span>Add labels</span><button class="nd__add nodrag" @click="() => addLabel('add')">+</button></div>
        <div v-for="(_, i) in d.add || []" :key="'a'+i" class="nd__brow">
          <input v-model="d.add[i]" placeholder="label" /><button class="nd__x nodrag" @click="() => removeLabel('add', i)">×</button>
        </div>
        <div class="nd__sub"><span>Remove labels</span><button class="nd__add nodrag" @click="() => addLabel('remove')">+</button></div>
        <div v-for="(_, i) in d.remove || []" :key="'r'+i" class="nd__brow">
          <input v-model="d.remove[i]" placeholder="label" /><button class="nd__x nodrag" @click="() => removeLabel('remove', i)">×</button>
        </div>
      </template>

      <!-- phonebook manager -->
      <template v-else-if="t === 'phonebook'">
        <input v-model="d.phonebook" placeholder="Phonebook name" />
        <select v-model="d.op"><option value="add">add contact</option><option value="remove">remove contact</option></select>
      </template>

      <!-- WA form (Meta Flow) -->
      <template v-else-if="isForm">
        <textarea v-model="d.message" rows="2" placeholder="Message shown with the form…" />
        <input v-model="d.flow_id" placeholder="Flow ID (from Meta)" />
        <div class="nd__grid">
          <input v-model="d.flow_cta" placeholder="CTA (Open form)" />
          <input v-model="d.flow_screen" placeholder="screen" />
        </div>
        <textarea :value="d.prefill_json" rows="2" class="mono"
                  placeholder="prefill JSON — tokens in {{ var }} notation"
                  @input="parseJsonInto('prefill', $event.target.value)" />
      </template>

      <!-- Google services (coming soon stub) -->
      <template v-else-if="t === 'google'">
        <select v-model="d.service"><option>Sheets</option><option>Calendar</option><option>Drive</option><option>Docs</option></select>
        <input v-model="d.action" placeholder="action (e.g. append-row)" />
        <small class="nd__hint">Coming soon — needs a service account.</small>
      </template>

      <!-- assign agent -->
      <template v-else-if="t === 'assign'">
        <input v-model="d.wd_agent" placeholder="Agent (User email)" />
        <input v-model="d.description" placeholder="Note (optional)" />
      </template>

      <!-- tag -->
      <template v-else-if="t === 'tag'">
        <input v-model="d.tag" placeholder="tag-name (uses {{var}})" />
      </template>

      <!-- note (internal comment on Issue) -->
      <template v-else-if="t === 'note'">
        <textarea v-model="d.content" rows="2" placeholder="Internal note on the conversation…" />
      </template>

      <!-- timing -->
      <template v-else-if="t === 'timing'">
        <input v-model.number="d.delay" type="number" placeholder="delay (seconds)" />
      </template>

      <!-- transfer -->
      <template v-else-if="t === 'transfer'">
        <input v-model="d.wd_team" placeholder="Team (User Group)" />
        <input v-model="d.wd_agent" placeholder="Agent (optional, User email)" />
        <input v-model="d.queue_message" placeholder="Message while waiting (optional)" />
      </template>

      <!-- goto -->
      <template v-else-if="t === 'goto' || t === 'goto_flow'">
        <input v-model="d.target_flow" placeholder="Target flow name" />
      </template>

      <!-- end -->
      <template v-else-if="isEnd">
        <textarea v-model="d.completion_message" rows="2" placeholder="Completion message…" />
      </template>
    </div>

    <!-- outputs -->
    <Handle v-if="sources.length === 1 && sources[0].id == null" type="source" :position="Position.Right" class="hdl hdl--out" />
    <template v-else>
      <div v-for="(s, i) in sources" :key="s.id || i" class="brn" :style="{ bottom: `${8 + (sources.length - 1 - i) * 22}px` }">
        <span class="brn__label">{{ s.label }}</span>
        <Handle type="source" :id="s.id" :position="Position.Right" class="hdl hdl--out" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.nd { position: relative; width: 260px; border-radius: 12px; background: #fff; border: 1px solid #e5e7eb; box-shadow: 0 4px 12px rgba(2,6,23,0.08); font-size: 12px; }
.nd--sel { box-shadow: 0 0 0 2px var(--accent), 0 6px 16px rgba(2,6,23,0.12); }
.nd__head { display: flex; align-items: center; gap: 7px; padding: 7px 9px; border-top-left-radius: 12px; border-top-right-radius: 12px; background: color-mix(in srgb, var(--accent) 12%, #fff); border-bottom: 1px solid #f1f5f9; }
.nd__icon { width: 22px; height: 22px; display: grid; place-items: center; border-radius: 7px; background: var(--accent); color: #fff; font-size: 12px; flex-shrink: 0; }
.nd__title { flex: 1; min-width: 0; border: none; background: transparent; font-weight: 650; font-size: 13px; color: #0f172a; outline: none; padding: 2px 0; }
.nd__del { width: 20px; height: 20px; border-radius: 6px; color: #94a3b8; font-size: 16px; line-height: 1; }
.nd__del:hover { background: #fee2e2; color: #dc2626; }
.nd__form { padding: 8px 9px; display: flex; flex-direction: column; gap: 6px; }
.nd__form input, .nd__form select, .nd__form textarea { width: 100%; border: 1px solid #e5e7eb; border-radius: 7px; padding: 6px 8px; font-size: 12px; color: #0f172a; background: #fff; outline: none; }
.nd__form input:focus, .nd__form select:focus, .nd__form textarea:focus { border-color: var(--accent); }
.nd__form textarea { resize: vertical; }
.mono { font-family: ui-monospace, monospace; }
.nd__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.nd__sub { display: flex; align-items: center; justify-content: space-between; font-size: 10px; text-transform: uppercase; font-weight: 700; color: #94a3b8; margin-top: 2px; }
.nd__add { font-size: 11px; color: #16a34a; font-weight: 700; }
.nd__brow { display: flex; align-items: center; gap: 4px; }
.nd__bid { max-width: 56px; }
.nd__x { color: #94a3b8; font-size: 15px; line-height: 1; padding: 0 2px; }
.nd__x:hover { color: #dc2626; }
.hdl { width: 11px; height: 11px; border: 2px solid #fff; }
.hdl--in { background: #94a3b8; }
.hdl--out { background: var(--accent); }
.brn { position: absolute; right: -7px; display: flex; align-items: center; gap: 5px; }
.brn__label { font-size: 9px; color: #64748b; background: #fff; border: 1px solid #e5e7eb; padding: 0 4px; border-radius: 5px; }
.nd__sec { border: 1px dashed #e5e7eb; border-radius: 7px; padding: 5px; display: flex; flex-direction: column; gap: 5px; }
.nd__check { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #475569; }
.nd__check input { width: auto; }
.nd__hint { font-size: 10px; color: #94a3b8; }
.nd__rrow { border: 1px dashed #e5e7eb; border-radius: 7px; padding: 5px; display: flex; flex-direction: column; gap: 5px; margin-bottom: 4px; }
</style>

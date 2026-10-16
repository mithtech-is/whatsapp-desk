<script setup>
import { computed } from 'vue'

const props = defineProps({ node: { type: Object, required: true } })
const d = computed(() => props.node.data)

function ensure(key, def) {
  if (d.value[key] === undefined) d.value[key] = def
}

// buttons repeater
function addButton() {
  ensure('buttons', [])
  d.value.buttons.push({ id: 'opt' + (d.value.buttons.length + 1), title: '' })
}
function removeButton(i) { d.value.buttons.splice(i, 1) }

// assignments repeater
function addAssign() {
  ensure('assignments', [])
  d.value.assignments.push({ name: '', value: '' })
}
function removeAssign(i) { d.value.assignments.splice(i, 1) }

const t = computed(() => props.node.type)
const isMessage = computed(() => ['text', 'say', 'greeting'].includes(t.value))
const isInput = computed(() => ['input', 'gather'].includes(t.value))
const isButtons = computed(() => ['buttons', 'menu'].includes(t.value))
const isApi = computed(() => ['api_call', 'http_callback'].includes(t.value))
const isEnd = computed(() => ['end', 'hangup'].includes(t.value))
</script>

<template>
  <div class="space-y-4 text-sm">
    <!-- label -->
    <div>
      <label class="wd-label">Label</label>
      <input v-model="d.label" class="wd-in" placeholder="Node label" />
    </div>

    <!-- start -->
    <template v-if="t === 'start'">
      <div>
        <label class="wd-label">Greeting message</label>
        <textarea v-model="d.initial_message" rows="3" class="wd-in" placeholder="Hi! Welcome…" />
      </div>
      <div>
        <label class="wd-label">Trigger keywords (comma-separated)</label>
        <input v-model="d.trigger_keywords" class="wd-in" placeholder="hi, hello, help" />
      </div>
    </template>

    <!-- message -->
    <template v-else-if="isMessage">
      <div>
        <label class="wd-label">Message type</label>
        <select v-model="d.message_type" class="wd-in"><option>Text</option><option>Template</option></select>
      </div>
      <div v-if="d.message_type !== 'Template'">
        <label class="wd-label">Message</label>
        <textarea v-model="d.message" rows="4" class="wd-in" placeholder="Type the message… use {{ name }} for variables" />
      </div>
      <div v-else>
        <label class="wd-label">Template name</label>
        <input v-model="d.template" class="wd-in" placeholder="approved_template_name" />
      </div>
    </template>

    <!-- input / gather -->
    <template v-else-if="isInput">
      <div>
        <label class="wd-label">Prompt</label>
        <textarea v-model="d.message" rows="3" class="wd-in" placeholder="What's your name?" />
      </div>
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="wd-label">Store as</label>
          <input v-model="d.store_as" class="wd-in" placeholder="name" />
        </div>
        <div>
          <label class="wd-label">Input type</label>
          <select v-model="d.input_type" class="wd-in">
            <option>Text</option><option>Number</option><option>Email</option><option>Phone</option><option>Date</option>
          </select>
        </div>
      </div>
      <div>
        <label class="wd-label">Validation error</label>
        <input v-model="d.validation_error" class="wd-in" placeholder="Please try again." />
      </div>
    </template>

    <!-- buttons / menu -->
    <template v-else-if="isButtons">
      <div>
        <label class="wd-label">Message</label>
        <textarea v-model="d.message" rows="3" class="wd-in" placeholder="How can we help?" />
      </div>
      <div>
        <div class="mb-1 flex items-center">
          <label class="wd-label !mb-0">Buttons</label>
          <button class="ml-auto wd-chip" @click="addButton">+ Add</button>
        </div>
        <div v-for="(b, i) in d.buttons || []" :key="i" class="mb-2 flex items-center gap-2">
          <input v-model="b.id" class="wd-in !w-20" placeholder="id" />
          <input v-model="b.title" class="wd-in flex-1" placeholder="Button label" />
          <button class="wd-x" @click="removeButton(i)">×</button>
        </div>
        <p v-if="!(d.buttons && d.buttons.length)" class="text-xs text-ink-gray-4">No buttons yet.</p>
      </div>
    </template>

    <!-- condition -->
    <template v-else-if="t === 'condition'">
      <div>
        <label class="wd-label">Expression (Python, uses variables)</label>
        <textarea v-model="d.expression" rows="3" class="wd-in font-mono" placeholder="vars.get('score', 0) > 5" />
        <p class="mt-1 text-xs text-ink-gray-4">Branches: <b>true</b> / <b>false</b></p>
      </div>
    </template>

    <!-- set_variable -->
    <template v-else-if="t === 'set_variable'">
      <div>
        <div class="mb-1 flex items-center">
          <label class="wd-label !mb-0">Assignments</label>
          <button class="ml-auto wd-chip" @click="addAssign">+ Add</button>
        </div>
        <div v-for="(a, i) in d.assignments || []" :key="i" class="mb-2 flex items-center gap-2">
          <input v-model="a.name" class="wd-in !w-24" placeholder="name" />
          <input v-model="a.value" class="wd-in flex-1" placeholder="value / {{ var }}" />
          <button class="wd-x" @click="removeAssign(i)">×</button>
        </div>
      </div>
    </template>

    <!-- api_call -->
    <template v-else-if="isApi">
      <div>
        <label class="wd-label">URL</label>
        <input v-model="d.url" class="wd-in" placeholder="https://api.example.com/x" />
      </div>
      <div class="grid grid-cols-2 gap-2">
        <div>
          <label class="wd-label">Method</label>
          <select v-model="d.method" class="wd-in"><option>GET</option><option>POST</option></select>
        </div>
        <div>
          <label class="wd-label">Store response as</label>
          <input v-model="d.store_as" class="wd-in" placeholder="result" />
        </div>
      </div>
      <div>
        <label class="wd-label">Response path</label>
        <input v-model="d.response_path" class="wd-in" placeholder="data.summary" />
      </div>
      <p class="text-xs text-ink-gray-4">Branches: <b>success</b> / <b>error</b></p>
    </template>

    <!-- timing -->
    <template v-else-if="t === 'timing'">
      <div>
        <label class="wd-label">Delay (seconds)</label>
        <input v-model.number="d.delay" type="number" class="wd-in" placeholder="30" />
      </div>
    </template>

    <!-- transfer -->
    <template v-else-if="t === 'transfer'">
      <div>
        <label class="wd-label">Team (User Group)</label>
        <input v-model="d.wd_team" class="wd-in" placeholder="Support" />
      </div>
    </template>

    <!-- goto -->
    <template v-else-if="t === 'goto' || t === 'goto_flow'">
      <div>
        <label class="wd-label">Target flow</label>
        <input v-model="d.target_flow" class="wd-in" placeholder="Another flow name" />
      </div>
    </template>

    <!-- end / hangup -->
    <template v-else-if="isEnd">
      <div>
        <label class="wd-label">Completion message</label>
        <textarea v-model="d.completion_message" rows="3" class="wd-in" placeholder="Goodbye!" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.wd-label { display: block; margin-bottom: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .03em; color: var(--ink-gray-5, #94a3b8); }
.wd-in {
  width: 100%;
  border-radius: 8px;
  border: 1px solid var(--outline-gray-2, #e2e8f0);
  background: var(--surface-white, #fff);
  padding: 7px 10px;
  font-size: 13px;
  color: var(--ink-gray-8, #1e293b);
  outline: none;
}
.wd-in:focus { border-color: #16a34a; }
.wd-chip { font-size: 11px; color: #16a34a; font-weight: 600; }
.wd-x { color: var(--ink-gray-4, #94a3b8); font-size: 16px; line-height: 1; padding: 0 4px; }
.wd-x:hover { color: #ef4444; }
</style>

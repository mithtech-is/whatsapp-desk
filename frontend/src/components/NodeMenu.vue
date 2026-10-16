<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['add', 'close'])

// Catalog matches polyg.in's node palette (All / Message / Request / Input / Logic).
// Each row shows an icon, title, one-line description, and a status dot.
const CATALOG = [
  // Message
  { type: 'text', icon: '💬', color: '#2563eb', cat: 'Message', title: 'Send Message', desc: 'Send a text, media, or interactive message' },
  { type: 'media', icon: '🖼', color: '#2563eb', cat: 'Message', title: 'Send Media', desc: 'Send an image, video, document, or audio' },
  { type: 'text', icon: '📄', color: '#2563eb', cat: 'Message', title: 'Send WA Template', desc: 'Send a Meta-approved template', variant: 'template' },
  { type: 'wa_form', icon: '📝', color: '#2563eb', cat: 'Message', title: 'Send WA Form', desc: 'Send a WhatsApp Flow form to collect responses' },
  { type: 'buttons', icon: '🔘', color: '#2563eb', cat: 'Message', title: 'Buttons', desc: 'Interactive reply buttons (≤3) or auto-list (4–10)' },
  { type: 'list', icon: '📋', color: '#2563eb', cat: 'Message', title: 'Native List', desc: 'Native WhatsApp list with sections' },
  { type: 'poll', icon: '📊', color: '#2563eb', cat: 'Message', title: 'Poll', desc: 'Native poll with one or multiple answers' },
  // Request
  { type: 'make_request', icon: '🌐', color: '#0284c7', cat: 'Request', title: 'Make Request', desc: 'Call external APIs — method, headers, body, response var', dot: '#0284c7' },
  { type: 'google', icon: '🧩', color: '#94a3b8', cat: 'Request', title: 'Google Services', desc: 'Sheets, Calendar, Drive & Docs via service account', dot: '#f59e0b', badge: 'Soon' },
  // Input
  { type: 'input', icon: '⌨️', color: '#7c3aed', cat: 'Input', title: 'Collect Input', desc: 'Ask a question and validate the reply' },
  { type: 'response_saver', icon: '💾', color: '#7c3aed', cat: 'Input', title: 'Response Saver', desc: 'Save the user response into a named variable' },
  // Logic
  { type: 'condition_router', icon: '🔀', color: '#ca8a04', cat: 'Logic', title: 'Condition Router', desc: 'Multiple conditions with Exact / Contains / Regex matching' },
  { type: 'condition', icon: '◇', color: '#ca8a04', cat: 'Logic', title: 'Condition', desc: 'Simple true/false branch on an expression' },
  { type: 'set_variable', icon: '🔧', color: '#0891b2', cat: 'Logic', title: 'Set Variable', desc: 'Assign values to flow variables' },
  { type: 'delay', icon: '⏱', color: '#64748b', cat: 'Logic', title: 'Delay', desc: 'Wait for N seconds or minutes before continuing' },
  { type: 'disable_auto_reply', icon: '🤖', color: '#dc2626', cat: 'Logic', title: 'Disable Auto-Reply', desc: 'Temporarily stop the bot for this conversation' },
  { type: 'set_labels', icon: '🏷', color: '#059669', cat: 'Logic', title: 'Set Chat Labels', desc: 'Add or remove labels on the conversation' },
  { type: 'phonebook', icon: '📒', color: '#059669', cat: 'Logic', title: 'Phonebook Manager', desc: 'Add or remove the contact from a phonebook' },
  { type: 'transfer', icon: '🙋', color: '#db2777', cat: 'Logic', title: 'Handoff to Agent', desc: 'Hand the conversation to a team or agent' },
  { type: 'assign', icon: '👤', color: '#db2777', cat: 'Logic', title: 'Assign Agent', desc: 'Assign the conversation to a specific agent' },
  { type: 'note', icon: '🗒', color: '#059669', cat: 'Logic', title: 'Add Note', desc: 'Attach an internal note to the conversation' },
  { type: 'ai_response', icon: '✨', color: '#0d9488', cat: 'Logic', title: 'AI Response', desc: 'Reply with the AI assistant, optionally hand off' },
  { type: 'start', icon: '▶', color: '#16a34a', cat: 'Logic', title: 'Initial Node', desc: 'Entry point — Chatbot trigger and built-in variables' },
  { type: 'goto', icon: '↪', color: '#9333ea', cat: 'Logic', title: 'Go to Flow', desc: 'Jump to another flow' },
  { type: 'end', icon: '⏹', color: '#dc2626', cat: 'Logic', title: 'End', desc: 'Finish the conversation' },
]
const CATS = ['All', 'Message', 'Request', 'Input', 'Logic']

const q = ref('')
const cat = ref('All')
const items = computed(() => CATALOG.filter((n) => {
  if (cat.value !== 'All' && n.cat !== cat.value) return false
  const s = q.value.trim().toLowerCase()
  return !s || n.title.toLowerCase().includes(s) || n.desc.toLowerCase().includes(s)
}))
</script>

<template>
  <transition name="nm">
    <div v-if="open" class="nm">
      <div class="nm__backdrop" @click="emit('close')" />
      <div class="nm__panel">
        <header class="nm__head">
          <span class="nm__title">🧩 Node Menu</span>
          <button class="nm__close" @click="emit('close')">×</button>
        </header>
        <input v-model="q" class="nm__search" placeholder="Search nodes…" />
        <div class="nm__cats">
          <button v-for="c in CATS" :key="c" class="nm__cat" :class="{ on: cat === c }" @click="cat = c">{{ c }}</button>
        </div>
        <div class="nm__list">
          <button v-for="n in items" :key="(n.type || '') + ':' + (n.variant || '')" class="nm__item"
                  @click="emit('add', { type: n.type, variant: n.variant, title: n.title })">
            <span class="nm__icon" :style="{ background: n.color + '22', color: n.color }">{{ n.icon }}</span>
            <span class="nm__body">
              <span class="nm__name">
                {{ n.title }}
                <span v-if="n.badge" class="nm__badge">{{ n.badge }}</span>
              </span>
              <span class="nm__desc">{{ n.desc }}</span>
            </span>
            <span class="nm__dot" :style="{ background: n.dot || n.color }" />
          </button>
          <p v-if="!items.length" class="nm__empty">No matching nodes.</p>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.nm { position: absolute; inset: 0; z-index: 40; }
.nm__backdrop { position: absolute; inset: 0; background: rgba(2,6,23,0.2); }
.nm__panel { position: absolute; top: 0; right: 0; height: 100%; width: 360px; background: #fff; box-shadow: -8px 0 24px rgba(2,6,23,0.12); display: flex; flex-direction: column; }
.nm__head { display: flex; align-items: center; padding: 16px; border-bottom: 1px solid #e5e7eb; }
.nm__title { font-weight: 700; font-size: 15px; }
.nm__close { margin-left: auto; font-size: 22px; color: #94a3b8; line-height: 1; }
.nm__search { margin: 12px 16px 8px; border: 1px solid #e5e7eb; border-radius: 10px; padding: 9px 12px; font-size: 13px; outline: none; }
.nm__search:focus { border-color: #10b981; }
.nm__cats { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 16px 10px; }
.nm__cat { font-size: 12px; font-weight: 600; padding: 4px 11px; border-radius: 999px; color: #64748b; background: #f1f5f9; }
.nm__cat.on { background: #10b981; color: #fff; }
.nm__list { flex: 1; overflow-y: auto; padding: 4px 10px 16px; }
.nm__item { display: flex; align-items: center; gap: 12px; width: 100%; text-align: left; padding: 10px 10px; border-radius: 12px; }
.nm__item:hover { background: #f8fafc; }
.nm__icon { width: 40px; height: 40px; border-radius: 11px; display: grid; place-items: center; font-size: 17px; flex-shrink: 0; }
.nm__body { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.nm__name { font-weight: 650; font-size: 14px; color: #0f172a; }
.nm__desc { font-size: 12px; color: #64748b; }
.nm__dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.nm__badge { font-size: 9px; font-weight: 700; text-transform: uppercase; color: #f59e0b; background: #fef3c7; padding: 1px 6px; border-radius: 999px; margin-left: 4px; vertical-align: middle; }
.nm__empty { padding: 20px; text-align: center; color: #94a3b8; font-size: 13px; }

.nm-enter-active .nm__panel, .nm-leave-active .nm__panel { transition: transform .22s ease; }
.nm-enter-from .nm__panel, .nm-leave-to .nm__panel { transform: translateX(100%); }
.nm-enter-active .nm__backdrop, .nm-leave-active .nm__backdrop { transition: opacity .22s ease; }
.nm-enter-from .nm__backdrop, .nm-leave-to .nm__backdrop { opacity: 0; }
</style>

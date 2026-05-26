<script setup>
import { onMounted, ref } from 'vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiDownload, mdiRefresh } from '@mdi/js';
import { useApiRequest } from '@/composables/useApiRequest';
import { toasted } from '@/utils/utils';
import {
  downloadWarningLetterPdf,
  getVeryOverdueLetters,
  savePdfBlob,
} from '../api/borrowApi';

const listReq = useApiRequest();
const letters = ref([]);
const thresholdDays = ref(14);
const downloadingId = ref('');

function loadLetters() {
  listReq.send(
    () => getVeryOverdueLetters(),
    (res) => {
      if (!res?.success) {
        toasted(false, '', res?.error || 'Could not load overdue letters.');
        return;
      }
      const payload = res?.data || {};
      letters.value = payload.letters || [];
      thresholdDays.value = payload.threshold_days ?? 14;
    }
  );
}

async function exportPdf(letter) {
  const borrowId = letter?.borrow_id;
  if (!borrowId) return;

  downloadingId.value = borrowId;
  try {
    const blob = await downloadWarningLetterPdf(borrowId);
    const safeId = String(letter.member_id_number || borrowId).replace(/[^\w.-]+/g, '_');
    savePdfBlob(blob, `overdue_warning_${safeId}.pdf`);
    toasted(true, 'Warning letter downloaded.');
  } catch (error) {
    toasted(false, '', error?.message || 'Could not export PDF.');
  } finally {
    downloadingId.value = '';
  }
}

onMounted(loadLetters);
</script>

<template>
  <div class="page">
    <header class="page-header">
      <div>
        <h1>Very Overdue Warning Letters</h1>
        <p>
          Students with materials overdue by {{ thresholdDays }}+ days. Review each case and export a
          formal warning letter as PDF.
        </p>
      </div>
      <button type="button" class="btn-refresh" :disabled="listReq.pending.value" @click="loadLetters">
        <BaseIcon :path="mdiRefresh" size="18" />
        Refresh
      </button>
    </header>

    <div v-if="listReq.pending.value" class="status">Loading overdue records…</div>
    <div v-else-if="!letters.length" class="status empty">No very overdue borrows at this time.</div>

    <div v-else class="letter-list">
      <article v-for="letter in letters" :key="letter.borrow_id" class="letter-card">
        <div class="letter-main">
          <h2>{{ letter.member_name }}</h2>
          <p class="meta">ID: {{ letter.member_id_number }} · {{ letter.member_email || 'No email' }}</p>
          <p class="book">
            <strong>{{ letter.material_title }}</strong>
            <span v-if="letter.material_author"> — {{ letter.material_author }}</span>
          </p>
          <dl class="details">
            <div>
              <dt>Borrowed</dt>
              <dd>{{ letter.borrow_date }}</dd>
            </div>
            <div>
              <dt>Due</dt>
              <dd>{{ letter.due_date }}</dd>
            </div>
            <div>
              <dt>Days overdue</dt>
              <dd class="overdue">{{ letter.overdue_days }}</dd>
            </div>
            <div>
              <dt>Library</dt>
              <dd>{{ letter.library_name }}</dd>
            </div>
          </dl>
        </div>
        <button
          type="button"
          class="btn-export"
          :disabled="downloadingId === letter.borrow_id"
          @click="exportPdf(letter)"
        >
          <BaseIcon :path="mdiDownload" size="18" />
          {{ downloadingId === letter.borrow_id ? 'Exporting…' : 'Export PDF' }}
        </button>
      </article>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 1.5rem;
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  font-size: 1.5rem;
  color: #0f172a;
}

.page-header p {
  margin: 0.35rem 0 0;
  color: #64748b;
  font-size: 0.9rem;
  max-width: 36rem;
}

.btn-refresh,
.btn-export {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 0.75rem;
  padding: 0.5rem 0.9rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  border: 1px solid rgba(203, 213, 225, 0.8);
  background: white;
  color: #334155;
}

.btn-export {
  align-self: flex-start;
  border-color: rgba(239, 68, 68, 0.35);
  color: #b91c1c;
  background: #fef2f2;
}

.status {
  padding: 1rem;
  border-radius: 0.75rem;
  background: #f8fafc;
  color: #475569;
}

.status.empty {
  background: #fffbeb;
  color: #92400e;
}

.letter-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.letter-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.1rem;
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.7);
  background: white;
}

.letter-main h2 {
  margin: 0;
  font-size: 1.05rem;
  color: #0f172a;
}

.meta {
  margin: 0.2rem 0 0.5rem;
  font-size: 0.8rem;
  color: #64748b;
}

.book {
  margin: 0 0 0.75rem;
  font-size: 0.9rem;
  color: #334155;
}

.details {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.5rem 1rem;
  margin: 0;
}

.details dt {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #94a3b8;
}

.details dd {
  margin: 0.1rem 0 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.details dd.overdue {
  color: #b91c1c;
}

@media (max-width: 640px) {
  .letter-card {
    flex-direction: column;
  }

  .details {
    grid-template-columns: 1fr;
  }
}
</style>

export function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  if (Array.isArray(payload?.libraries)) return payload.libraries;
  if (Array.isArray(payload?.users)) return payload.users;
  return [];
}

export function normalizeRole(value) {
  return String(value || '')
    .trim()
    .toUpperCase()
    .replace(/^ROLE_/, '');
}

export function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

export function amount(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

export function formatDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString();
}

export function getUserId(user) {
  return user?.id || user?.user_id || user?.userId || user?.uuid || null;
}

export function sameId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;
  return String(a) === String(b);
}

export function belongsToCurrentUser(row, currentUserId) {
  if (!currentUserId) return false;
  const ids = [
    row?.member,
    row?.member_id,
    row?.memberId,
    row?.member_uuid,
    row?.member?.id,
    row?.user,
    row?.user_id,
    row?.userId,
    row?.created_by,
  ];
  return ids.some((id) => sameId(id, currentUserId));
}

export function parseInputDate(value, endOfDay = false) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  if (endOfDay) {
    date.setHours(23, 59, 59, 999);
  } else {
    date.setHours(0, 0, 0, 0);
  }
  return date;
}

export function rowDate(row, fields = ['created_at', 'borrow_date', 'return_date', 'reserve_date']) {
  const raw = fields.map((field) => row?.[field]).find(Boolean);
  const date = new Date(raw || 0);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function filterByDateRange(rows, fromDate, toDate, dateFields) {
  const from = parseInputDate(fromDate);
  const to = parseInputDate(toDate, true);
  if (!from && !to) return rows;

  return rows.filter((row) => {
    const date = rowDate(row, dateFields);
    if (!date) return !from && !to;
    if (from && date < from) return false;
    if (to && date > to) return false;
    return true;
  });
}

export function memberDepartment(row) {
  return String(row?.department || row?.member_department || '').trim();
}

export function belongsToDepartment(row, department) {
  if (!department) return true;
  const dept = String(department).trim().toLowerCase();
  const memberDept = memberDepartment(row).toLowerCase();
  const nameDept = String(row?.member_name || '').toLowerCase();
  return memberDept === dept || nameDept.includes(dept);
}

export function rowLibraryId(row) {
  return (
    row?.library_id ??
    row?.library ??
    row?.material_library_id ??
    row?.member_library_id ??
    row?.material?.library_id ??
    null
  );
}

export function filterByLibrary(rows, libraryId) {
  if (!libraryId) return rows;
  return rows.filter((row) => sameId(rowLibraryId(row), libraryId));
}

export function monthBucketSeries(rows, fields = ['created_at', 'borrow_date']) {
  const keys = [];
  const now = new Date();

  for (let index = 5; index >= 0; index -= 1) {
    const date = new Date(now.getFullYear(), now.getMonth() - index, 1);
    keys.push({
      label: date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' }),
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`,
    });
  }

  const counts = new Map(keys.map((item) => [item.key, 0]));
  rows.forEach((row) => {
    const date = rowDate(row, fields);
    if (!date) return;
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    if (counts.has(key)) {
      counts.set(key, (counts.get(key) || 0) + 1);
    }
  });

  return {
    labels: keys.map((item) => item.label),
    data: keys.map((item) => counts.get(item.key) || 0),
  };
}

export function defaultDateRange() {
  const to = new Date();
  const from = new Date();
  from.setMonth(from.getMonth() - 1);
  return {
    from: from.toISOString().slice(0, 10),
    to: to.toISOString().slice(0, 10),
  };
}

export function exportToCsv(filename, headers, rows) {
  const escape = (value) => {
    const text = String(value ?? '');
    if (/[",\n]/.test(text)) {
      return `"${text.replace(/"/g, '""')}"`;
    }
    return text;
  };

  const lines = [
    headers.map((header) => escape(header.label)).join(','),
    ...rows.map((row) => headers.map((header) => escape(row[header.key])).join(',')),
  ];

  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

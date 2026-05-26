/**
 * Report definitions per role. Each report has columns and a row builder key
 * resolved in Reports.vue from loaded datasets.
 */
export const REPORTS_BY_ROLE = {
  MEMBER: [
    {
      id: 'my-borrows',
      label: 'Borrowing history',
      description: 'All borrows on your account within the selected date range.',
    },
    {
      id: 'my-fines',
      label: 'Fine statement',
      description: 'Overdue fines from returns, paid and outstanding.',
    },
    {
      id: 'my-reservations',
      label: 'Reservation history',
      description: 'Materials you reserved and their status.',
    },
  ],
  'STACK STAFF': [
    {
      id: 'circulation-summary',
      label: 'Circulation summary',
      description: 'Issues, returns, and overdue counts for the period.',
    },
    {
      id: 'overdue-list',
      label: 'Overdue borrows',
      description: 'Items past due date that need follow-up.',
    },
    {
      id: 'fines-report',
      label: 'Fines report',
      description: 'Return fines generated in the selected period.',
    },
  ],
  'FRONT DESK STAFF': [
    {
      id: 'circulation-summary',
      label: 'Shelf circulation summary',
      description: 'Borrow and return activity for your library branch.',
    },
    {
      id: 'transfer-report',
      label: 'Transfer requests',
      description: 'Material transfer requests and their status.',
    },
    {
      id: 'fines-report',
      label: 'Fines report',
      description: 'Fines from returns processed at the desk.',
    },
  ],
  'TECHNICAL STAFF': [
    {
      id: 'catalog-inventory',
      label: 'Catalog inventory',
      description: 'Physical and digital materials with availability.',
    },
    {
      id: 'low-stock',
      label: 'Low stock alert',
      description: 'Physical items with one or fewer copies available.',
    },
    {
      id: 'borrow-activity',
      label: 'Borrow activity',
      description: 'Borrow records to see collection usage trends.',
    },
  ],
  ADMIN: [
    {
      id: 'circulation-summary',
      label: 'Branch circulation',
      description: 'Circulation KPIs for your assigned library.',
    },
    {
      id: 'member-roster',
      label: 'Member roster',
      description: 'Registered members at your library branch.',
    },
    {
      id: 'fines-report',
      label: 'Fine revenue',
      description: 'Fines collected and outstanding for your branch.',
    },
    {
      id: 'reservation-report',
      label: 'Reservations',
      description: 'Reservation queue and fulfillment status.',
    },
  ],
  'SUPER ADMIN': [
    {
      id: 'system-overview',
      label: 'System overview',
      description: 'Cross-library counts for members, borrows, and fines.',
    },
    {
      id: 'circulation-summary',
      label: 'Circulation summary',
      description: 'System-wide borrow and return activity.',
    },
    {
      id: 'library-comparison',
      label: 'Library comparison',
      description: 'Side-by-side metrics per library branch.',
    },
    {
      id: 'fines-report',
      label: 'Fine revenue',
      description: 'All fines across branches in the period.',
    },
  ],
  'DEPARTMENT HEAD': [
    {
      id: 'department-usage',
      label: 'Department usage',
      description: 'Borrows and reservations by members in your department.',
    },
    {
      id: 'department-members',
      label: 'Department members',
      description: 'Members registered under your department.',
    },
    {
      id: 'popular-materials',
      label: 'Popular materials',
      description: 'Most borrowed titles among your department.',
    },
  ],
};

export function reportsForRole(role) {
  const normalized = String(role || '')
    .toUpperCase()
    .replace(/^ROLE_/, '')
    .trim();
  return REPORTS_BY_ROLE[normalized] || [];
}

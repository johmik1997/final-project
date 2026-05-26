import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export function exportReportPdf({ title, subtitle, headers, rows, filename }) {
  const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });
  const darkColor = [15, 23, 42];
  const primaryColor = [245, 158, 11];

  doc.setFillColor(...darkColor);
  doc.rect(0, 0, 297, 28, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(16);
  doc.text('HU-DLRBS Library Report', 14, 14);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'normal');
  doc.text(title, 14, 22);

  doc.setTextColor(...darkColor);
  doc.setFontSize(9);
  if (subtitle) {
    doc.text(subtitle, 14, 36);
  }
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, subtitle ? 42 : 36);

  autoTable(doc, {
    startY: subtitle ? 48 : 42,
    margin: { left: 14, right: 14 },
    head: [headers.map((header) => header.label)],
    body: rows.map((row) => headers.map((header) => String(row[header.key] ?? ''))),
    theme: 'striped',
    headStyles: {
      fillColor: primaryColor,
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 9,
    },
    bodyStyles: {
      fontSize: 8,
      textColor: darkColor,
    },
  });

  const safeName = String(filename || 'report')
    .toLowerCase()
    .replace(/[^a-z0-9_-]/g, '_');
  doc.save(`${safeName}.pdf`);
}

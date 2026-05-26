import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export function generatePaymentReceipt(payment) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  const primaryColor = [245, 158, 11];
  const darkColor = [15, 23, 42];
  const lightGray = [241, 245, 249];
  const paidAmount = Number(payment?.amount || 0);
  const amountLabel = `ETB ${paidAmount.toFixed(2)}`;

  doc.setFillColor(...darkColor);
  doc.rect(0, 0, 210, 40, 'F');

  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(22);
  doc.text('HU-DLRBS LIBRARY SYSTEM', 20, 25);

  doc.setTextColor(245, 158, 11);
  doc.setFontSize(10);
  doc.text('OFFICIAL PAYMENT RECEIPT', 145, 25);

  doc.setTextColor(...darkColor);
  doc.setFontSize(10);
  doc.setFont('helvetica', 'bold');
  doc.text('RECEIPT INFORMATION', 20, 55);

  doc.setFont('helvetica', 'normal');
  doc.text(`Transaction ID: ${payment?.payment_intent_id || payment?.id || 'N/A'}`, 20, 63);
  doc.text(
    `Payment Date: ${
      payment?.payment_date
        ? String(payment.payment_date).slice(0, 19).replace('T', ' ')
        : new Date().toLocaleString()
    }`,
    20,
    70
  );
  doc.text(`Payment Method: ${payment?.payment_method || 'Online Card'}`, 20, 77);

  doc.setFont('helvetica', 'bold');
  doc.text('MEMBER DETAILS', 120, 55);

  doc.setFont('helvetica', 'normal');
  doc.text(`Name: ${payment?.member_name || 'Library Patron'}`, 120, 63);
  doc.text(`ID Number: ${payment?.member_id_number || payment?.member || 'N/A'}`, 120, 70);
  doc.text(`Library Branch: ${payment?.library_name || 'Central Library'}`, 120, 77);

  doc.setDrawColor(226, 232, 240);
  doc.line(20, 85, 190, 85);

  autoTable(doc, {
    startY: 95,
    margin: { left: 20, right: 20 },
    head: [['Material Title', 'Fee Type', 'Paid Amount']],
    body: [
      [
        payment?.material_title || payment?.material || 'Library Circulation Overdue Fee',
        payment?.fee_type || 'Overdue Fine',
        amountLabel,
      ],
    ],
    theme: 'striped',
    headStyles: {
      fillColor: primaryColor,
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 10,
    },
    bodyStyles: {
      textColor: darkColor,
      fontSize: 9,
    },
    columnStyles: {
      0: { cellWidth: 100 },
      1: { cellWidth: 40 },
      2: { cellWidth: 30, halign: 'right' },
    },
  });

  const finalY = (doc.lastAutoTable?.finalY || 110) + 15;

  doc.setFillColor(...lightGray);
  doc.rect(120, finalY - 5, 70, 20, 'F');

  doc.setTextColor(...darkColor);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(11);
  doc.text('TOTAL PAID:', 125, finalY + 7);

  doc.setTextColor(16, 185, 129);
  doc.setFontSize(14);
  doc.text(amountLabel, 160, finalY + 7);

  doc.setTextColor(148, 163, 184);
  doc.setFont('helvetica', 'italic');
  doc.setFontSize(9);
  doc.text('Thank you for choosing our Library Services.', 20, finalY + 35);
  doc.text('This is a computer generated document. No signature required.', 20, finalY + 41);

  const safeTitle = String(payment?.material_title || 'receipt')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '_');
  doc.save(`receipt_${payment?.id || 'payment'}_${safeTitle}.pdf`);
}

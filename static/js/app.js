/* ── FBR Invoice App — client JS ── */

/* Toast */
function showToast(msg, type = 'default', duration = 3500) {
  const c = document.getElementById('toast-container');
  if (!c) return;
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => { t.style.opacity = '0'; t.style.transition = 'opacity 300ms'; setTimeout(() => t.remove(), 300); }, duration);
}

/* HTMX global response handler */
document.body.addEventListener('htmx:afterRequest', function(e) {
  const status = e.detail.xhr.status;
  const hdr = e.detail.xhr.getResponseHeader('X-Toast');
  if (hdr) {
    const { msg, type } = JSON.parse(hdr);
    showToast(msg, type);
  }
  if (status >= 400 && !hdr) {
    showToast('Something went wrong. Please try again.', 'error');
  }
});

document.body.addEventListener('htmx:responseError', function(e) {
  showToast('Network error. Check your connection.', 'error');
});

/* ── Line items logic ── */
let itemIndex = 0;

function addLineItem() {
  itemIndex++;
  const tbody = document.getElementById('line-items-body');
  if (!tbody) return;
  const row = document.createElement('tr');
  row.id = `item-row-${itemIndex}`;
  row.innerHTML = `
    <td><input type="text" name="items[${itemIndex}][description]" placeholder="Item description" required></td>
    <td><input type="text" name="items[${itemIndex}][hscode]" placeholder="e.g. 1006.30" style="width:100px"></td>
    <td><input type="number" name="items[${itemIndex}][qty]" value="1" min="0.01" step="any" style="width:70px" oninput="recalcRow(${itemIndex})"></td>
    <td><input type="number" name="items[${itemIndex}][unit_price]" value="0" min="0" step="any" style="width:100px" oninput="recalcRow(${itemIndex})"></td>
    <td>
      <select name="items[${itemIndex}][tax_rate]" style="width:75px" onchange="recalcRow(${itemIndex})">
        <option value="0">0%</option>
        <option value="5">5%</option>
        <option value="17" selected>17%</option>
      </select>
    </td>
    <td class="computed right" id="tax-${itemIndex}">0</td>
    <td class="computed right font-mono" id="total-${itemIndex}"><strong>0</strong></td>
    <td><button type="button" class="del-btn" onclick="removeLineItem(${itemIndex})" title="Remove item">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4h8v2"/></svg>
    </button></td>
  `;
  tbody.appendChild(row);
  recalcAll();
}

function removeLineItem(idx) {
  const row = document.getElementById(`item-row-${idx}`);
  if (row) row.remove();
  recalcAll();
}

function fmt(n) { return 'Rs ' + Math.round(n).toLocaleString('en-PK'); }

function recalcRow(idx) {
  const qty   = parseFloat(document.querySelector(`[name="items[${idx}][qty]"]`)?.value)        || 0;
  const price = parseFloat(document.querySelector(`[name="items[${idx}][unit_price]"]`)?.value) || 0;
  const rate  = parseFloat(document.querySelector(`[name="items[${idx}][tax_rate]"]`)?.value)   || 0;
  const subtotal = qty * price;
  const tax      = subtotal * rate / 100;
  const total    = subtotal + tax;
  const taxEl   = document.getElementById(`tax-${idx}`);
  const totalEl = document.getElementById(`total-${idx}`);
  if (taxEl)   taxEl.textContent   = fmt(tax);
  if (totalEl) totalEl.innerHTML   = `<strong>${fmt(total)}</strong>`;
  recalcAll();
}

function recalcAll() {
  let subtotal = 0, totalTax = 0;
  document.querySelectorAll('#line-items-body tr').forEach(row => {
    const id = row.id.replace('item-row-', '');
    const qty   = parseFloat(row.querySelector(`[name="items[${id}][qty]"]`)?.value)        || 0;
    const price = parseFloat(row.querySelector(`[name="items[${id}][unit_price]"]`)?.value) || 0;
    const rate  = parseFloat(row.querySelector(`[name="items[${id}][tax_rate]"]`)?.value)   || 0;
    const sub = qty * price;
    const tax = sub * rate / 100;
    subtotal += sub;
    totalTax += tax;
  });
  const grand = subtotal + totalTax;
  const setEl = (id, v) => { const el = document.getElementById(id); if(el) el.textContent = v; };
  setEl('total-subtotal', fmt(subtotal));
  setEl('total-gst',      fmt(totalTax));
  setEl('total-grand',    fmt(grand));
}

/* Seed one row on form load */
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('line-items-body')) {
    const existing = document.querySelectorAll('#line-items-body tr').length;
    if (existing === 0) addLineItem();
    /* wire up existing rows (edit mode) */
    document.querySelectorAll('#line-items-body tr').forEach(row => {
      const id = row.id.replace('item-row-', '');
      row.querySelectorAll('input[type=number], select').forEach(el => {
        el.addEventListener('input', () => recalcRow(parseInt(id)));
      });
    });
    recalcAll();
  }
});

/* Active nav link highlight */
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-item[data-path]').forEach(el => {
    const p = el.dataset.path;
    if (p === '/' ? path === '/' : path.startsWith(p)) {
      el.classList.add('active');
    }
  });
});

/* Close modal on overlay click */
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.remove();
  }
});

/* Filter tab helper */
function setFilter(el, value, targetId) {
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  htmx.trigger(`#${targetId}`, 'filterChange', { value });
}

/* Confirm dialog helper */
function confirmAction(msg, callback) {
  if (window.confirm(msg)) callback();
}

/* Print invoice */
function printInvoice() { window.print(); }

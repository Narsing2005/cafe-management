// Sidebar toggle (mobile)
document.addEventListener('click', e => {
  if (e.target.closest('#menuToggle')) {
    document.querySelector('.sidebar')?.classList.toggle('open');
  }
});

// Auto-dismiss flashes
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => {
    f.style.transition = 'opacity .4s';
    f.style.opacity = '0';
    setTimeout(() => f.remove(), 400);
  });
}, 4000);

// Order form: live total
function recalcOrderTotal() {
  let total = 0;
  document.querySelectorAll('.order-line').forEach(row => {
    const price = parseFloat(row.dataset.price || '0');
    const qty = parseInt(row.querySelector('input[name="qty[]"]').value || '0', 10);
    const sub = price * (isNaN(qty) ? 0 : qty);
    row.querySelector('.subtotal').textContent = '₹' + sub.toFixed(2);
    total += sub;
  });
  const t = document.getElementById('orderTotal');
  if (t) t.textContent = '₹' + total.toFixed(2);
}
document.addEventListener('input', e => {
  if (e.target.matches('input[name="qty[]"]')) recalcOrderTotal();
});
document.addEventListener('DOMContentLoaded', recalcOrderTotal);

// Confirm deletes
document.addEventListener('submit', e => {
  if (e.target.matches('.confirm-form')) {
    if (!confirm(e.target.dataset.confirm || 'Are you sure?')) e.preventDefault();
  }
});

/* ========== Customer cart ========== */
const CART_KEY = 'cafe_cart_v1';
const getCart = () => JSON.parse(localStorage.getItem(CART_KEY) || '[]');
const setCart = c => { localStorage.setItem(CART_KEY, JSON.stringify(c)); renderCart(); };

function addToCart(id, name, price) {
  const cart = getCart();
  const ex = cart.find(c => c.id === id);
  if (ex) ex.qty++; else cart.push({ id, name, price, qty: 1 });
  setCart(cart);
  showToast(`${name} added to cart`);
}
function changeQty(id, delta) {
  const cart = getCart().map(c => c.id === id ? { ...c, qty: c.qty + delta } : c)
                        .filter(c => c.qty > 0);
  setCart(cart);
}
function clearCart() { setCart([]); }

function renderCart() {
  const list = document.getElementById('cartList');
  const totalEl = document.getElementById('cartTotal');
  const countEl = document.getElementById('cartCount');
  if (!list) return;
  const cart = getCart();
  list.innerHTML = cart.length ? '' : '<p style="color:var(--muted)">Your cart is empty.</p>';
  let total = 0, count = 0;
  cart.forEach(c => {
    total += c.price * c.qty; count += c.qty;
    const row = document.createElement('div');
    row.className = 'cart-item';
    row.innerHTML = `
      <div><strong>${c.name}</strong><br><span style="color:var(--muted);font-size:12px">₹${c.price.toFixed(2)}</span></div>
      <div style="display:flex;gap:6px;align-items:center">
        <button class="btn ghost sm" onclick="changeQty(${c.id},-1)">−</button>
        <span>${c.qty}</span>
        <button class="btn ghost sm" onclick="changeQty(${c.id},1)">+</button>
      </div>`;
    list.appendChild(row);
  });
  totalEl.textContent = '₹' + total.toFixed(2);
  countEl.textContent = count;
  countEl.style.display = count ? 'grid' : 'none';
}

function toggleCart() { document.getElementById('cartDrawer').classList.toggle('open'); }

async function placeOrder() {
  const name = document.getElementById('custName').value.trim() || 'Guest';
  const cart = getCart();
  if (!cart.length) { showToast('Cart is empty'); return; }
  const res = await fetch('/api/place_order', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, cart })
  });
  const data = await res.json();
  if (data.ok) {
    clearCart();
    document.getElementById('billBox').innerHTML = `
      <h3>Thank you, ${name}!</h3>
      <p>Order <strong>#${data.order_id}</strong> placed.</p>
      <p>Total: <strong style="color:var(--accent-2)">₹${data.total.toFixed(2)}</strong></p>`;
    toggleCart();
  } else {
    showToast(data.error || 'Failed to place order');
  }
}

function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'flash info'; t.textContent = msg;
  let host = document.querySelector('.flashes');
  if (!host) { host = document.createElement('div'); host.className = 'flashes'; document.body.appendChild(host); }
  host.appendChild(t);
  setTimeout(() => t.remove(), 2500);
}

document.addEventListener('click', e => {
  const b = e.target.closest('.add-btn');
  if (b) {
    addToCart(parseInt(b.dataset.id, 10), b.dataset.name, parseFloat(b.dataset.price));
  }
});

document.addEventListener('DOMContentLoaded', renderCart);

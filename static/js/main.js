/* ==========================================================
   SHOPIFY — main.js
   UI interactions only (no backend). Vanilla JS.
   ========================================================== */
document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();

  /* ---------- Sticky navbar shadow ---------- */
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => navbar?.classList.toggle('scrolled', window.scrollY > 10));

  /* ---------- Mobile menu toggle ---------- */
  const openMenu = () => document.body.classList.add('menu-open');
  const closeMenu = () => document.body.classList.remove('menu-open');
  document.getElementById('menu-toggle')?.addEventListener('click', openMenu);
  document.getElementById('menu-close')?.addEventListener('click', closeMenu);
  document.getElementById('mobile-overlay')?.addEventListener('click', closeMenu);
  document.addEventListener('keydown', e => e.key === 'Escape' && closeMenu());

  /* ---------- Search drawer ---------- */
  document.getElementById('search-toggle')?.addEventListener('click', () => {
    const bar = document.getElementById('search-bar');
    bar.classList.toggle('open');
    if (bar.classList.contains('open')) bar.querySelector('input')?.focus();
  });

  /* ---------- Hero slider ---------- */
  const slider = document.getElementById('hero-slider');
  if (slider) {
    const slides = slider.querySelectorAll('.hero-slide');
    const dots = slider.querySelectorAll('.hero-dot');
    let current = 0, timer;
    const go = i => {
      slides[current].classList.remove('active'); dots[current].classList.remove('active');
      current = (i + slides.length) % slides.length;
      slides[current].classList.add('active'); dots[current].classList.add('active');
    };
    const start = () => { clearInterval(timer); timer = setInterval(() => go(current + 1), 6000); };
    dots.forEach((d, i) => d.addEventListener('click', () => { go(i); start(); }));
    start();
  }

  /* ---------- Add to cart + toast ---------- */
  const badge = document.getElementById('cart-badge');
  document.querySelectorAll('[data-add-to-cart]').forEach(btn => {
    btn.addEventListener('click', e => {
      e.preventDefault();
      const qtyInput = btn.closest('form')?.querySelector('[data-qty] input');
      const qty = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;
      if (badge) {
        badge.textContent = (parseInt(badge.textContent, 10) || 0) + qty;
        badge.classList.remove('bump'); void badge.offsetWidth; badge.classList.add('bump');
      }
      showToast(`${btn.dataset.name || 'Item'} added to cart`);
      // Django: send fetch() POST to your add-to-cart view here (include CSRF token)
    });
  });

  /* ---------- Quantity selectors (+ / -) ---------- */
  document.querySelectorAll('[data-qty]').forEach(wrap => {
    const input = wrap.querySelector('input');
    const update = v => {
      input.value = Math.max(1, v);
      input.dispatchEvent(new Event('change', { bubbles: true }));
    };
    wrap.querySelector('[data-qty-minus]')?.addEventListener('click', () => update(+input.value - 1));
    wrap.querySelector('[data-qty-plus]')?.addEventListener('click', () => update(+input.value + 1));
    input.addEventListener('input', () => { if (+input.value < 1) input.value = 1; });
  });

  /* ---------- Cart totals ---------- */
  const fmt = n => '$' + n.toFixed(2);
  const recalcCart = () => {
    const rows = document.querySelectorAll('.cart-row');
    let total = 0;
    rows.forEach(row => {
      const price = parseFloat(row.dataset.price);
      const qty = parseInt(row.querySelector('[data-qty] input').value, 10) || 1;
      const sub = price * qty; total += sub;
      row.querySelector('[data-subtotal]').textContent = fmt(sub);
    });
    const s = document.getElementById('cart-subtotal'), t = document.getElementById('cart-total');
    if (s) s.textContent = fmt(total);
    if (t) t.textContent = fmt(total);
    if (!rows.length && document.getElementById('cart-full')) {
      document.getElementById('cart-full').style.display = 'none';
      document.getElementById('cart-empty').classList.remove('hidden');
    }
    if (badge && document.getElementById('cart-full')) {
      badge.textContent = [...rows].reduce((a, r) => a + (parseInt(r.querySelector('input').value, 10) || 1), 0);
    }
  };
  document.querySelectorAll('.cart-row [data-qty] input').forEach(i => i.addEventListener('change', recalcCart));
  document.querySelectorAll('[data-remove]').forEach(btn => btn.addEventListener('click', () => {
    const row = btn.closest('.cart-row');
    row.classList.add('removing');
    setTimeout(() => { row.remove(); recalcCart(); showToast('Item removed'); }, 400);
  }));

  /* ---------- Product thumbnails ---------- */
  const mainImg = document.getElementById('main-image');
  document.querySelectorAll('[data-thumb]').forEach(t => t.addEventListener('click', () => {
    document.querySelectorAll('[data-thumb]').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    mainImg.classList.add('fade');
    setTimeout(() => { mainImg.src = t.dataset.thumb; mainImg.onload = () => mainImg.classList.remove('fade'); }, 200);
  }));

  /* ---------- Wishlist ---------- */
  document.querySelectorAll('[data-wishlist]').forEach(b => b.addEventListener('click', () => {
    b.classList.toggle('active');
    showToast(b.classList.contains('active') ? 'Added to wishlist' : 'Removed from wishlist');
  }));

  /* ---------- Shop filters ---------- */
  const range = document.getElementById('price-range');
  range?.addEventListener('input', () => document.getElementById('price-value').textContent = '$' + range.value);
  document.getElementById('filter-toggle')?.addEventListener('click', () => document.getElementById('filters').classList.toggle('open'));

  /* ---------- Form validation UI (checkout + contact) ---------- */
  document.querySelectorAll('#checkout-form, #contact-form').forEach(form => {
    const validate = field => {
      const g = field.closest('.form-group'); if (!g) return true;
      const ok = field.checkValidity() && (!field.required || field.value.trim() !== '');
      g.classList.toggle('is-valid', ok && field.value !== '');
      g.classList.toggle('is-invalid', !ok);
      return ok;
    };
    form.querySelectorAll('[required]').forEach(f => f.addEventListener('blur', () => validate(f)));
    form.addEventListener('submit', e => {
      e.preventDefault(); // remove when wiring to Django
      const valid = [...form.querySelectorAll('[required]')].map(validate).every(Boolean);
      if (valid) { showToast(form.id === 'checkout-form' ? 'Order placed — thank you!' : 'Message sent!'); form.reset();
        form.querySelectorAll('.is-valid').forEach(g => g.classList.remove('is-valid')); }
      else form.querySelector('.is-invalid .field')?.focus();
    });
  });

  /* ---------- Scroll reveal ---------- */
  const io = new IntersectionObserver(entries => entries.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
  }), { threshold: 0.12 });
  document.querySelectorAll('.reveal').forEach((el, i) => { el.style.transitionDelay = (i % 4) * 80 + 'ms'; io.observe(el); });
});

/* ---------- Global toast helper ---------- */
let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast'); if (!t) return;
  document.getElementById('toast-msg').textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

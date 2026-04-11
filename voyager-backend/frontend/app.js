/* ============================================================
   VOYAGE — frontend/app.js (PRODUCTION READY)
   ============================================================ */

// FIX: Removed the trailing slash to prevent // errors
const API = 'https://mini-travel-booking-website.onrender.com/api';

/* ── SESSION ─────────────────────────────────────────────── */
const Auth = {
  save:    (token, user) => { localStorage.setItem('voy_token', token); localStorage.setItem('voy_user', JSON.stringify(user)); },
  clear:   ()            => { localStorage.removeItem('voy_token'); localStorage.removeItem('voy_user'); },
  token:   ()            => localStorage.getItem('voy_token'),
  user:    ()            => { const u = localStorage.getItem('voy_user'); return u ? JSON.parse(u) : null; },
  loggedIn:()            => !!localStorage.getItem('voy_token'),
};

/* ── API HELPER ──────────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (Auth.token()) headers['Authorization'] = 'Bearer ' + Auth.token();
  
  try {
    // FIX: Clean the path to ensure no double slashes happen (e.g., api//auth)
    const cleanPath = path.startsWith('/') ? path.slice(1) : path;
    const url = `${API}/${cleanPath}`;
    
    const res  = await fetch(url, { ...options, headers });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    return data;
  } catch (err) {
    if (err instanceof TypeError) {
      showToast('❌ Cannot reach server. Please check your internet or server status.');
    } else {
      showToast('❌ ' + err.message);
    }
    throw err;
  }
}

// ... rest of your original functions (doLogin, doRegister, etc.) remain the same ...
// Note: Ensure doLogin() calls apiFetch('auth/login') and NOT apiFetch('/auth/login') 
// although the fix above handles both safely now.
/* ── INIT ────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  restoreSession();
  initNavScroll();
  initDates();
  initTripTypeRadios();
  animateStats();
});

/* ── SESSION RESTORE ─────────────────────────────────────── */
function restoreSession() {
  const user = Auth.user();
  if (user && Auth.loggedIn()) updateNavLoggedIn(user);
}

/* ── NAV ─────────────────────────────────────────────────── */
function toggleMenu() {
  document.getElementById('mobileMenu')?.classList.toggle('open');
}
function initNavScroll() {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 60));
}
/* ── NAV: UPDATED WITH ADMIN CHECK ───────────────────────── */
function updateNavLoggedIn(user) {
  const el = document.querySelector('.nav-actions');
  if (!el) return;

  const first = user.name ? user.name.split(' ')[0] : 'Traveller';
  
  // Check if this specific user is the Master Admin
  const isAdmin = (user.email === 'admin@gmail.com');

  el.innerHTML = `
    <span style="color:var(--gold,#c9a96e);font-size:.85rem;padding:8px 4px">Hi, ${first}</span>
    
    <button class="btn-ghost" onclick="showMyBookings()">My Trips</button>

    ${isAdmin ? `<button class="btn-ghost" onclick="showAllUserBookings()" style="color:#2ecc71; border:1px solid #2ecc71; margin:0 5px;">User Bookings</button>` : ''}
    
    <button class="btn-primary" onclick="logoutUser()">Logout</button>
  `;
}
function updateNavGuest() {
  const el = document.querySelector('.nav-actions');
  if (!el) return;
  el.innerHTML = `
    <button class="btn-ghost" onclick="openModal('loginModal')">Sign In</button>
    <button class="btn-primary" onclick="openModal('loginModal')">Join Free</button>`;
}

/* ── MODAL HELPERS ───────────────────────────────────────── */
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.style.display = 'flex'; document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.style.display = 'none'; document.body.style.overflow = ''; }
}
function closeModalOnBg(event, id) {
  if (event.target === event.currentTarget) closeModal(id);
}

/* ── LOGIN MODAL TABS ────────────────────────────────────── */
function switchModalTab(btn, tab) {
  document.querySelectorAll('.modal-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const loginPanel    = document.getElementById('modal-login');
  const registerPanel = document.getElementById('modal-register');
  if (loginPanel)    loginPanel.style.display    = (tab === 'login')    ? '' : 'none';
  if (registerPanel) registerPanel.style.display = (tab === 'register') ? '' : 'none';
}

/* ── AUTH: LOGIN ─────────────────────────────────────────── */
/* ── AUTH: LOGIN (Updated with Admin Redirect) ─────────── */
/* ── AUTH: LOGIN (Fixed for Seamless Admin) ──────────────── */
function doLogin() {
  const panel = document.getElementById('modal-login');
  const email = panel?.querySelector('input[type=email]')?.value.trim();
  const password = panel?.querySelector('input[type=password]')?.value;

  if (!email || !password) {
    showToast('❌ Please enter your email and password.');
    return;
  }

  apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password })
  })
    .then(data => {
      // 1. Save session
      Auth.save(data.token, data.user);
      
      // 2. Update the Nav (This now adds the "User Bookings" button automatically)
      updateNavLoggedIn(data.user);
      
      // 3. Close the modal
      closeModal('loginModal');

      // 4. Feedback
      if (email === 'admin@gmail.com') {
        showToast('🔑 Admin Dashboard Access Enabled.');
      } else {
        showToast('👋 Welcome back, ' + data.user.name.split(' ')[0] + '!');
      }
    })
    .catch(() => {
      // Errors handled by apiFetch toast
    });
}

/* ── AUTH: REGISTER ──────────────────────────────────────── */
function doRegister() {
  const panel    = document.getElementById('modal-register');
  const name     = panel?.querySelector('input[type=text]')?.value.trim();
  const email    = panel?.querySelector('input[type=email]')?.value.trim();
  const password = panel?.querySelector('input[type=password]')?.value;
  if (!name || !email || !password) { showToast('❌ All fields are required.'); return; }
  if (password.length < 6) { showToast('❌ Password must be at least 6 characters.'); return; }
  apiFetch('/auth/register', { method: 'POST', body: JSON.stringify({ name, email, password }) })
    .then(() => {
      showToast('🎉 Account created! Please sign in.');
      const loginTabBtn = document.querySelector('.modal-tab');
      switchModalTab(loginTabBtn, 'login');
    }).catch(() => {});
}

/* ── AUTH: LOGOUT ────────────────────────────────────────── */
function logoutUser() {
  Auth.clear();
  updateNavGuest();
  showToast('👋 Logged out.');
}

/* ── SEARCH TAB SWITCHER ─────────────────────────────────── */
function switchTab(btn, tabId) {
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(p => p.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const panel = document.getElementById('tab-' + tabId);
  if (panel) panel.classList.add('active');
}

/* ── SWAP LOCATIONS ──────────────────────────────────────── */
function swapLocations() {
  const from = document.getElementById('fromField');
  const to   = document.getElementById('toField');
  if (from && to) { const tmp = from.value; from.value = to.value; to.value = tmp; }
}

/* ── TASK 1 & 2: FLIGHT SEARCH ───────────────────────────── */
// State kept in module-level vars so sortResults() / filterDirect()
// can re-run the same search with updated params.
let _lastFlightParams = {};

async function searchFlights() {
  // TASK 4: use extractSearchTerm for safe IATA/city parsing
  const from = extractSearchTerm(document.getElementById('fromField')?.value);
  const to   = extractSearchTerm(document.getElementById('toField')?.value);

  // Read the current sort + filter controls
  const sortEl   = document.querySelector('.results-filters select');
  const directEl = document.querySelector('.results-filters input[type=checkbox]');
  const sortBy     = sortEl?.value   || 'price';
  const directOnly = directEl?.checked || false;

  // Save params so the filter/sort controls can reuse them
  _lastFlightParams = { from, to, sort_by: sortBy, direct_only: directOnly };

  await _fetchAndRenderFlights(_lastFlightParams);
}

// Called by onchange="sortResults(this.value)"
// TASK 1: Now actually re-fetches with the new sort param
async function sortResults(sortBy) {
  if (!_lastFlightParams.from && !_lastFlightParams.to) {
    // Nothing searched yet — just show a toast, don't fetch
    showToast('Search for flights first, then sort.');
    return;
  }
  _lastFlightParams.sort_by = sortBy;
  await _fetchAndRenderFlights(_lastFlightParams);
}

// Called by onchange="filterDirect(this)"
// TASK 1: Now actually re-fetches with direct_only param
async function filterDirect(checkbox) {
  if (!_lastFlightParams.from && !_lastFlightParams.to) {
    showToast('Search for flights first, then filter.');
    return;
  }
  _lastFlightParams.direct_only = checkbox.checked;
  await _fetchAndRenderFlights(_lastFlightParams);
}

// Core fetch + render — shared by search, sort, and filter
async function _fetchAndRenderFlights(params) {
  showResultsPanel('✈️ Searching flights...', '<p style="color:#8a94aa;padding:2rem 0">Loading from database...</p>');

  const qs = new URLSearchParams();
  if (params.from)        qs.set('from',        params.from);
  if (params.to)          qs.set('to',          params.to);
  if (params.sort_by)     qs.set('sort_by',     params.sort_by);
  if (params.direct_only) qs.set('direct_only', 'true');

  let flights = [];
  try {
    // TASK 2: single source of truth — no FLIGHTS fallback array
    const data = await apiFetch('/flights/?' + qs.toString());
    flights = data.flights || [];
  } catch (_) {
    showResultsPanel(
      '✈️ Connection Error',
      '<p style="color:#8a94aa;padding:2rem 0">Could not reach the server. ' +
      'Make sure Flask is running: <code>python app.py</code></p>'
    );
    return;
  }

  if (!flights.length) {
    const msg = params.direct_only
      ? 'No direct flights found for that route. Try unchecking "Direct flights only".'
      : 'No flights found. Try just the city name, e.g. "Dubai" or "London".';
    showResultsPanel('✈️ No Flights Found', `<p style="color:#8a94aa;padding:2rem 0">${msg}</p>`);
    return;
  }

  // TASK 3: format price using helper — never use pre-formatted strings
  const html = flights.map(f => {
    const priceDisplay = formatPrice(f.price);
    const stopsClass   = f.stops === 'Non-stop' ? 'direct' : 'stops';
    return `
      <div class="result-card"
           onclick="quickBookFlight(${f.id},'${f.to_city}',${f.price},'${f.airline}','${f.duration}','${f.from_code}','${f.to_code}')">
        <div class="result-card-header">
          <span class="airline-name">${f.airline}</span>
          <span class="flight-class flight-stops ${stopsClass}">${f.stops}</span>
        </div>
        <div class="flight-route">
          <div>
            <div class="flight-time">${f.from_code}</div>
            <div class="flight-code">${f.from_city}</div>
          </div>
          <div class="flight-line">
            <div class="flight-duration">${f.duration}</div>
            <span></span>
          </div>
          <div>
            <div class="flight-time">${f.to_code}</div>
            <div class="flight-code">${f.to_city}</div>
          </div>
        </div>
        <div class="result-card-footer">
          <div>
            <div class="result-price">${priceDisplay}</div>
            <div class="result-per">per person · ${f.schedule}</div>
          </div>
          <button class="btn-outline"
            onclick="event.stopPropagation();
                     quickBookFlight(${f.id},'${f.to_city}',${f.price},'${f.airline}','${f.duration}','${f.from_code}','${f.to_code}')">
            Select →
          </button>
        </div>
      </div>`;
  }).join('');

  const label = params.direct_only ? ' · Direct only' : '';
  showResultsPanel(`✈️ Available Flights (${flights.length} found${label})`, html);
}

/* ── TASK 5: FLIGHT BOOKING — snapshot price + duration ──── */
// All flight-specific data (price, duration, route) is captured AT
// booking time and stored in the details JSON blob.
// Future price changes in the flights table won't alter this record.
function quickBookFlight(id, toCity, price, airline, duration, fromCode, toCode) {
  startBooking('flight', `${toCity} Flight`, price, {
    flight_id:  id,
    airline:    airline,
    from_code:  fromCode,
    to_code:    toCode,
    duration:   duration,
    // Snapshot: price_at_booking is the numeric price locked at this moment
    price_at_booking: price,
    booked_at:  new Date().toISOString(),
  });
}

/* ── HOTEL SEARCH ────────────────────────────────────────── */
function searchHotels() {
  const dest    = document.querySelector('#tab-hotels .field input')?.value || 'your destination';
  const checkin = document.getElementById('checkin')?.value || '';
  const checkout= document.getElementById('checkout')?.value || '';

  const hotels = [
    { name:'The Grand Oberoi', location:'Mumbai', price: 18500, rating:'4.9', id:1 },
    { name:'Ayana Resort',     location:'Bali',   price: 22000, rating:'4.8', id:2 },
    { name:'Sakura Palace',    location:'Kyoto',  price: 15200, rating:'4.7', id:3 },
  ];

  const html = hotels.map(h => `
    <div class="result-card" onclick="openModal('hotelModal')">
      <div class="result-card-header">
        <span class="airline-name">${h.name}</span>
        <span class="flight-class">⭐ ${h.rating}</span>
      </div>
      <div style="color:#8a94aa;font-size:.85rem;margin-bottom:.75rem">
        📍 ${h.location}
        ${checkin ? ` &nbsp;·&nbsp; ${checkin} → ${checkout}` : ''}
      </div>
      <div class="result-card-footer">
        <div>
          <div class="result-price">${formatPrice(h.price)}</div>
          <div class="result-per">per night</div>
        </div>
        <button class="btn-outline" onclick="event.stopPropagation();openModal('hotelModal')">View →</button>
      </div>
    </div>`
  ).join('');

  showResultsPanel('🏨 Hotels in ' + dest, html);
}

/* ── PACKAGE SEARCH ──────────────────────────────────────── */
function searchPackages() {
  const inputs = document.querySelectorAll('#tab-packages .field input');
  const dest   = inputs[1]?.value || 'top destinations';

  const pkgs = [
    { name:'Maldives Bliss',  price: 99000,  duration:'7 Days'  },
    { name:'Europe Explorer', price: 189000, duration:'10 Days' },
    { name:'Japan Serenity',  price: 125000, duration:'6 Days'  },
  ];

  const html = pkgs.map(p => `
    <div class="result-card" onclick="openModal('packageModal')">
      <div class="result-card-header">
        <span class="airline-name">${p.name}</span>
        <span class="flight-class">${p.duration}</span>
      </div>
      <div class="result-card-footer">
        <div>
          <div class="result-price">${formatPrice(p.price)}</div>
          <div class="result-per">per person</div>
        </div>
        <button class="btn-outline" onclick="event.stopPropagation();openModal('packageModal')">Enquire →</button>
      </div>
    </div>`
  ).join('');

  showResultsPanel('🌍 Packages to ' + dest, html);
}

/* ── RESULTS PANEL ───────────────────────────────────────── */
function showResultsPanel(title, html) {
  const panel   = document.getElementById('resultsPanel');
  const titleEl = document.getElementById('resultsTitle');
  const grid    = document.getElementById('resultsGrid');
  if (!panel) return;
  if (titleEl) titleEl.textContent = title;
  if (grid)    grid.innerHTML = html || '<p style="color:#888;padding:2rem">Searching...</p>';
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
function closeResults() {
  const panel = document.getElementById('resultsPanel');
  if (panel) panel.style.display = 'none';
}

/* ── DESTINATION QUICK BOOK ──────────────────────────────── */
// TASK 3: prices stored as numbers, formatted via helper
const DEST_PRICES = { Maldives: 89000, Santorini: 120000, Bali: 45000, Tokyo: 75000, Paris: 110000 };

function quickBook(destination) {
  const price = DEST_PRICES[destination] || 50000;
  startBooking('package', destination, price, { destination });
}

/* ── BOOKING FLOW ────────────────────────────────────────── */
let _pendingBooking = {};

function startBooking(type, name, price, details) {
  if (!Auth.loggedIn()) {
    showToast('⚠️ Please sign in to book.');
    openModal('loginModal');
    return;
  }
  _pendingBooking = { type, name, price, details };
  if (type === 'hotel')   { openModal('hotelModal');   return; }
  if (type === 'package') { openModal('packageModal'); return; }
  // Flights go directly to confirmation
  doConfirmBooking();
}

// TASK 5: price and flight snapshot already in _pendingBooking.details
function doConfirmBooking() {
  const priceNum = Number(_pendingBooking.price) || 0;
  apiFetch('/bookings/create', {
    method: 'POST',
    body: JSON.stringify({
      type:    _pendingBooking.type || 'flight',
      price:   priceNum,
      // details already contains price_at_booking, duration, route codes
      details: { item: _pendingBooking.name, ..._pendingBooking.details }
    })
  }).then(data => {
    showToast('🎉 Booking #' + data.booking_id + ' confirmed!');
    _pendingBooking = {};
  }).catch(() => {});
}

function confirmBooking(type) {
  if (!Auth.loggedIn()) {
    showToast('⚠️ Please sign in first.');
    closeModal('hotelModal');
    closeModal('packageModal');
    openModal('loginModal');
    return;
  }
  const priceEl  = document.querySelector('#hotelModal .price-row.total span:last-child');
  const rawPrice = priceEl ? priceEl.textContent : String(_pendingBooking.price || '0');
  // TASK 3: strip all non-numeric chars to get a clean number
  const priceNum = parseFloat(rawPrice.replace(/[^0-9.]/g, '')) || Number(_pendingBooking.price) || 0;
  const name     = type === 'hotel'
    ? (document.querySelector('#hotelModal h3')?.textContent || 'Hotel Booking')
    : (document.querySelector('#packageModal select')?.value  || 'Package Booking');

  apiFetch('/bookings/create', {
    method: 'POST',
    // TASK 5: snapshot the price into the details blob
    body: JSON.stringify({
      type,
      price: priceNum,
      details: {
        item:             name,
        price_at_booking: priceNum,
        booked_at:        new Date().toISOString(),
      }
    })
  }).then(data => {
    closeModal('hotelModal');
    closeModal('packageModal');
    showToast('🎉 Booking #' + data.booking_id + ' confirmed!');
    _pendingBooking = {};
  }).catch(() => {});
}

/* ── MY BOOKINGS ─────────────────────────────────────────── */
async function showMyBookings() {
  const panel   = document.getElementById('resultsPanel');
  const titleEl = document.getElementById('resultsTitle');
  const grid    = document.getElementById('resultsGrid');
  if (!panel) return;
  if (titleEl) titleEl.textContent = '🧳 My Bookings';
  if (grid)    grid.innerHTML = '<p style="color:#8a94aa;padding:2rem 0">Loading...</p>';
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const data     = await apiFetch('/bookings/my');
    const bookings = data.bookings || [];
    if (!bookings.length) {
      grid.innerHTML = '<p style="color:#8a94aa;padding:2rem 0">No bookings yet. Start exploring!</p>';
      return;
    }
    grid.innerHTML = bookings.map(b => {
      const display = b.price_display || formatPrice(b.price);
      const snapshotNote = b.details?.price_at_booking
        ? ` <small style="color:#8a94aa">(booked at ${formatPrice(b.details.price_at_booking)})</small>`
        : '';

      // --- DELETION LOGIC ---
      const isConfirmed = b.status === 'confirmed';
      const isPending = b.status === 'pending_deletion';

      // Create the button/status label
      const deleteUI = isConfirmed 
        ? `<button class="btn-outline" 
                   style="color:#e74c3c; border-color:#e74c3c; padding:4px 10px; font-size:11px; margin-top:5px;" 
                   onclick="requestDeletion(${b.id})">Request Deletion</button>`
        : (isPending ? `<span style="color:var(--gold); font-size:11px; font-weight:bold;">⏳ Deletion Pending Admin Approval</span>` : '');

      return `
        <div class="result-card">
          <div class="result-card-header">
            <span class="airline-name">${b.details?.item || (b.type + ' Booking')}</span>
            <span class="flight-class" style="color:${b.status === 'confirmed' ? '#2ecc71' : 'var(--gold)'}">
              ${b.status.replace('_', ' ')}
            </span>
          </div>
          <div style="color:#8a94aa;font-size:.82rem;margin-bottom:.75rem">
            Booking #${b.id} &nbsp;·&nbsp; ${new Date(b.created_at).toLocaleDateString('en-IN')}
            ${b.details?.duration ? ` &nbsp;·&nbsp; ✈ ${b.details.duration}` : ''}
          </div>
          <div class="result-card-footer">
            <div class="result-price">${display}${snapshotNote}</div>
            <div style="text-align:right">
               <span style="color:#8a94aa;font-size:.8rem;display:block;margin-bottom:5px;">${b.type}</span>
               ${deleteUI}
            </div>
          </div>
        </div>`;
    }).join('');
  } catch (_) {
    grid.innerHTML = '<p style="color:#8a94aa;padding:2rem 0">Could not load bookings. Is Flask running?</p>';
  }
}

/* Add this helper function below if you haven't already */
async function requestDeletion(bookingId) {
    if (!confirm("Are you sure you want to ask the admin to delete this booking?")) return;
    try {
        // This calls the user-side route to change status to 'pending_deletion'
        await apiFetch('/bookings/request-delete', {
            method: 'POST',
            body: JSON.stringify({ booking_id: bookingId })
        });
        showToast('📩 Deletion request sent to Admin.');
        showMyBookings(); // Refresh the UI
    } catch (err) {
        console.error("Deletion request failed", err);
    }
}

/* ── NEWSLETTER ──────────────────────────────────────────── */
function subscribeNewsletter() {
  const input = document.getElementById('newsletterEmail');
  const email = input?.value.trim();
  if (!email || !email.includes('@')) { showToast('❌ Please enter a valid email.'); return; }
  if (input) input.value = '';
  showToast('📬 Subscribed! Exclusive deals on their way.');
}

/* ── TOAST ───────────────────────────────────────────────── */
function showToast(msg) {
  const toast = document.getElementById('toast');
  if (!toast) return;
  toast.textContent = msg;
  toast.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => toast.classList.remove('show'), 3500);
}

/* ── STATS COUNTER ───────────────────────────────────────── */
function animateStats() {
  const observer = new IntersectionObserver(entries => {
    if (!entries[0].isIntersecting) return;
    document.querySelectorAll('.stat-num').forEach(el => {
      const target  = parseInt(el.dataset.target) || 0;
      const isLarge = target > 9999;
      let current   = 0;
      const step    = Math.ceil(target / 80);
      const timer   = setInterval(() => {
        current = Math.min(current + step, target);
        el.textContent = isLarge
          ? (current >= 1000000 ? (current/1000000).toFixed(1)+'M' : (current/1000).toFixed(0)+'K')
          : current;
        if (current >= target) clearInterval(timer);
      }, 20);
    });
    observer.disconnect();
  }, { threshold: 0.5 });
  const bar = document.querySelector('.stats-bar');
  if (bar) observer.observe(bar);
}

/* ── DATES ───────────────────────────────────────────────── */
function initDates() {
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type=date]').forEach(el => el.min = today);
  const dep = document.getElementById('departDate');
  const ret = document.getElementById('returnDate');
  if (dep) {
    const d = new Date(); d.setDate(d.getDate() + 3);
    dep.value = d.toISOString().split('T')[0];
    dep.addEventListener('change', () => { if (ret) ret.min = dep.value; });
  }
  if (ret) {
    const d = new Date(); d.setDate(d.getDate() + 10);
    ret.value = d.toISOString().split('T')[0];
  }
}

/* ── TRIP TYPE RADIO ─────────────────────────────────────── */
function initTripTypeRadios() {
  document.querySelectorAll('input[name=trip]').forEach(r => {
    r.addEventListener('change', function () {
      const wrap = document.getElementById('returnDateWrap');
      if (wrap) wrap.style.display = this.value === 'oneway' ? 'none' : '';
    });
  });

}
/* ── ADMIN: SHOW ALL USER BOOKINGS ────────────────────────── */
async function showAllUserBookings() {
  const panel   = document.getElementById('resultsPanel');
  const titleEl = document.getElementById('resultsTitle');
  const grid    = document.getElementById('resultsGrid');
  
  if (!panel) return;
  if (titleEl) titleEl.textContent = '📋 All User Bookings (Master View)';
  if (grid)    grid.innerHTML = '<p style="color:#8a94aa;padding:2rem 0">Fetching all platform data...</p>';
  
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });

  try {
    const data = await apiFetch('/admin/stats');
    const bookings = data.recent_bookings || [];

    if (!bookings.length) {
      grid.innerHTML = '<p style="color:#8a94aa;padding:2rem 0">No bookings found on the platform.</p>';
      return;
    }

    grid.innerHTML = bookings.map(b => {
      // Logic for Deletion Requests
      let adminActions = '';
      const isRequestingDelete = (b.status === 'pending_deletion');

      if (isRequestingDelete) {
        adminActions = `
          <div style="margin-top:12px; display:flex; gap:10px; border-top:1px solid #34495e; padding-top:12px;">
            <button class="btn-primary" 
                    style="background:#2ecc71; padding:6px 12px; font-size:12px;" 
                    onclick="handleAdminDelete(${b.id}, 'approve')">Approve Delete</button>
            <button class="btn-outline" 
                    style="color:#e74c3c; border-color:#e74c3c; padding:6px 12px; font-size:12px;" 
                    onclick="handleAdminDelete(${b.id}, 'reject')">Reject</button>
          </div>
        `;
      }

      return `
        <div class="result-card" style="border-left: 4px solid ${isRequestingDelete ? '#e74c3c' : 'var(--gold)'};">
          <div class="result-card-header">
            <span class="airline-name">${b.user_name} <small style="opacity:0.7;">(${b.email})</small></span>
            <span class="flight-class" style="color:${isRequestingDelete ? '#e74c3c' : '#2ecc71'}">
              ${b.status.replace('_', ' ')}
            </span>
          </div>
          <div style="color:#8a94aa;font-size:.82rem;margin-bottom:.75rem">
            Type: <strong>${b.type.toUpperCase()}</strong> &nbsp;·&nbsp; 
            ID: #${b.id} &nbsp;·&nbsp; 
            Date: ${new Date(b.created_at).toLocaleDateString('en-IN')}
          </div>
          <div class="result-card-footer">
            <div class="result-price">${formatPrice(b.price)}</div>
            <span style="color:#8a94aa;font-size:.8rem">Total Revenue</span>
          </div>
          ${adminActions}
        </div>`;
    }).join('');
  } catch (err) {
    grid.innerHTML = `<p style="color:#e74c3c;padding:2rem 0">❌ Error: ${err.message}</p>`;
  }
}

/**
 * Helper to handle the Admin decision
 * Calls: POST /api/admin/handle-deletion
 */
async function handleAdminDelete(bookingId, action) {
    const confirmMsg = action === 'approve' 
        ? "Permanently DELETE this booking from the database?" 
        : "Reject this deletion request?";
        
    if (!confirm(confirmMsg)) return;

    try {
        const data = await apiFetch('/admin/handle-deletion', {
            method: 'POST',
            body: JSON.stringify({ booking_id: bookingId, action: action })
        });
        
        showToast('✅ ' + data.message);
        // Refresh the admin panel to show updated statuses
        showAllUserBookings(); 
    } catch (err) {
        console.error("Admin action failed", err);
    }
}

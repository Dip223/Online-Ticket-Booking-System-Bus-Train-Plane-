/* ============================================================
   static/script.js  —  BD Ticket complete frontend logic
   ============================================================ */

const API = "http://127.0.0.1:5000";

/* ── Admin emails (must match admin_routes.py) ────────────── */
const ADMIN_EMAILS = [
  "zihadmuzahid2003@gmail.com",
  "md.soheleleven05@gmail.com"
];

/* ── helpers ──────────────────────────────────────────────── */
function getToken() { return localStorage.getItem("token") || ""; }

function authHeader() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + getToken()
  };
}

function showToast(msg, type) {
  const el = document.getElementById("toast");
  if (!el) return;
  el.innerHTML = `<i class="fas fa-${type === "ok" ? "check-circle" : "exclamation-circle"}"></i> ${msg}`;
  el.className = "toast " + (type || "ok") + " show";
  setTimeout(() => el.classList.remove("show"), 3500);
}

function showAlert(id, msg, type) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = `<i class="fas fa-${type === "err" ? "exclamation-circle" : "check-circle"}"></i> ${msg}`;
  el.className = "alert " + type;
  el.style.display = "flex";
}

/* ── LOGIN ────────────────────────────────────────────────── */
function login() {
  const email    = (document.getElementById("email")?.value    || "").trim();
  const password = (document.getElementById("password")?.value || "").trim();

  if (!email || !password) {
    showAlert("loginAlert", "Please fill in all fields", "err");
    return;
  }

  const btn = document.querySelector(".btn-login");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
  }

  fetch(API + "/login", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email, password })
  })
  .then(r => r.json())
  .then(d => {
    if (d.token) {
      localStorage.setItem("token",   d.token);
      localStorage.setItem("user_id", d.user_id  || "");
      localStorage.setItem("name",    d.name     || "");
      localStorage.setItem("email",   d.email    || email);
      localStorage.setItem("role",    d.role     || "user");

      const isAdmin = ADMIN_EMAILS.includes(email.toLowerCase());

      if (isAdmin) {
        showAlert("loginAlert", `<i class="fas fa-crown" style="color:#f59e0b;margin-right:6px"></i> Welcome Admin! Redirecting to Admin Panel...`, "ok");
        if (btn) btn.innerHTML = '<i class="fas fa-shield-alt"></i> Entering Admin Panel...';
        setTimeout(() => { window.location = "/admin"; }, 1200);
      } else {
        showAlert("loginAlert", "Login successful! Redirecting...", "ok");
        if (btn) btn.innerHTML = '<i class="fas fa-check"></i> Success!';
        setTimeout(() => { window.location = "/dashboard"; }, 800);
      }
    } else {
      showAlert("loginAlert", d.message || "Login failed ❌", "err");
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-sign-in-alt"></i>Login to Account';
      }
    }
  })
  .catch(() => {
    showAlert("loginAlert", "Cannot reach server. Is Flask running?", "err");
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-sign-in-alt"></i>Login to Account';
    }
  });
}

/* ── REGISTER – STEP 1: send OTP ─────────────────────────── */
function register() {
  const name     = (document.getElementById("name")?.value     || "").trim();
  const email    = (document.getElementById("email")?.value    || "").trim();
  const password = (document.getElementById("password")?.value || "").trim();

  if (!name || !email || !password) {
    showAlert("regAlert", "All fields are required", "err"); return;
  }
  if (password.length < 6) {
    showAlert("regAlert", "Password must be at least 6 characters", "err"); return;
  }

  fetch(API + "/send-register-otp", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ name, email, password })
  })
  .then(r => r.json())
  .then(d => {
    const ok = d.message && (d.message.includes("sent") || d.message.includes("OTP"));
    showAlert("regAlert", d.message, ok ? "ok" : "err");
    if (ok) {
      const ob = document.getElementById("otpBox");
      if (ob) ob.style.display = "block";
      const sd1 = document.getElementById("sd1");
      const sl1 = document.getElementById("sl1");
      const sd2 = document.getElementById("sd2");
      if (sd1) { sd1.className = "step-dot done"; sd1.innerHTML = '<i class="fas fa-check" style="font-size:12px"></i>'; }
      if (sl1) sl1.className = "step-line done";
      if (sd2) sd2.className = "step-dot active";
      if (typeof startTimer === "function") startTimer();
    }
  })
  .catch(() => showAlert("regAlert", "Server error — is Flask running?", "err"));
}

/* ── REGISTER – STEP 2: verify OTP ───────────────────────── */
function verifyRegisterOTP() {
  const email = (document.getElementById("email")?.value || "").trim();
  const otp   = (document.getElementById("otp")?.value   || "").trim();

  if (otp.length !== 6) { showAlert("regAlert", "Enter the 6-digit OTP", "err"); return; }

  fetch(API + "/verify-register-otp", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email, otp })
  })
  .then(r => r.json())
  .then(d => {
    const ok = d.message && d.message.toLowerCase().includes("success");
    showAlert("regAlert", d.message, ok ? "ok" : "err");
    if (ok) setTimeout(() => window.location = "/", 1600);
  });
}

/* ── LOGOUT ───────────────────────────────────────────────── */
function logout() { localStorage.clear(); window.location = "/"; }

/* ── NAVIGATION ───────────────────────────────────────────── */
function goBus()   { window.location = "/bus";   }
function goTrain() { window.location = "/train"; }
function goPlane() { window.location = "/plane"; }
function goToDashboard() { window.location = "/dashboard"; }

/* ── DASHBOARD ROUTE LOADING ──────────────────────────────── */
let _routes  = [];
let _curType = "bus";

function loadRoutes(type) {
  _curType = type || "bus";
  fetch(API + "/" + _curType + "-routes")
    .then(r => r.json())
    .then(data => {
      _routes = data.routes || [];

      const srcSet = [...new Set(_routes.map(r => r.from))];
      const srcEl  = document.getElementById("source");
      if (srcEl) {
        srcEl.innerHTML = srcSet.map(s => `<option value="${s}">${s}</option>`).join("");
      }

      updateDestinations();

      const opEl = document.getElementById("operator");
      if (opEl) {
        opEl.innerHTML = (data.operators || []).map(o => `<option value="${o}">${o}</option>`).join("");
      }
    })
    .catch(err => console.warn("loadRoutes error:", err));
}

function updateDestinations() {
  const srcEl  = document.getElementById("source");
  const destEl = document.getElementById("destination");
  if (!srcEl || !destEl) return;

  const src     = srcEl.value;
  const matches = _routes.filter(r => r.from === src);
  destEl.innerHTML = matches
    .map(r => `<option value="${r.to}|${r.price}">${r.to} — ৳${r.price}</option>`)
    .join("");
  showPrice();
}

function showPrice() {
  const destEl = document.getElementById("destination");
  if (!destEl) return;
  const price  = (destEl.value || "").split("|")[1] || "0";
  const disp   = document.getElementById("priceDisplay") || document.getElementById("price");
  if (disp) disp.textContent = price;
}

/* ── PAYMENT METHOD TOGGLE ───────────────────────────────── */
function togglePaymentFields() {
  const method = document.getElementById("paymentMethod")?.value;
  const mobileFields = document.getElementById("mobilePaymentFields");
  const cardFields = document.getElementById("cardPaymentFields");

  if (!mobileFields || !cardFields) return;

  if (method === "card") {
    mobileFields.style.display = "none";
    cardFields.style.display = "block";
  } else {
    mobileFields.style.display = "block";
    cardFields.style.display = "none";
  }
}

/* ── BOOK (Dashboard with Payment) ───────────────────────── */
function book() {
  if (!getToken()) { alert("Please login first"); window.location = "/"; return; }

  const srcEl       = document.getElementById("source");
  const destEl      = document.getElementById("destination");
  const opEl        = document.getElementById("operator");
  const payMethodEl = document.getElementById("paymentMethod");

  if (!srcEl || !destEl) return;

  const destVal     = (destEl.value || "").split("|");
  const source      = srcEl.value;
  const destination = destVal[0];
  const price       = destVal[1] || "0";
  const operator    = opEl ? opEl.value : "";
  const paymentMethod = payMethodEl ? payMethodEl.value : "bkash";
  const type        = _curType.charAt(0).toUpperCase() + _curType.slice(1);
  const journeyDate = document.getElementById("journeyDate")?.value || new Date().toISOString().split('T')[0];
  const seatNo      = document.getElementById("seatNo")?.value || "A1";
  const seatClass   = document.getElementById("seatClass")?.value || "Economy";

  if (!destination) { showToast("Please select a destination ❌", "err"); return; }
  if (!operator)    { showToast("Please select an operator ❌",    "err"); return; }

  let payload = {
    source, destination, price, type, operator, payment_method: paymentMethod,
    journey_date: journeyDate, seat_no: seatNo, seat_class: seatClass
  };

  if (paymentMethod === "card") {
    payload.card_holder = document.getElementById("cardHolder")?.value || "";
    payload.card_number = document.getElementById("cardNumber")?.value || "";
    payload.expiry      = document.getElementById("expiry")?.value || "";
    payload.cvv         = document.getElementById("cvv")?.value || "";
  } else {
    payload.phone = document.getElementById("phone")?.value || "";
    payload.pin   = document.getElementById("pin")?.value || "";
  }

  fetch(API + "/book", {
    method:  "POST",
    headers: authHeader(),
    body:    JSON.stringify(payload)
  })
  .then(r => { if (r.status === 401) { localStorage.clear(); window.location = "/"; } return r.json(); })
  .then(d => {
    const ok = d.message && (d.message.includes("✅") || d.message.toLowerCase().includes("success"));
    showToast(d.message, ok ? "ok" : "err");
    if (ok) {
      setTimeout(loadBookings, 900);
      setTimeout(loadNotifications, 1000);
      if (d.redirect_url) setTimeout(() => window.location = d.redirect_url, 1500);
    }
  })
  .catch(() => showToast("Server error ❌", "err"));
}

/* ── BOOK (individual transport pages with Payment) ──────── */
function bookFromPage(type, routesArray) {
  if (!getToken()) { alert("Please login first"); window.location = "/"; return; }

  const srcEl       = document.getElementById("source");
  const destEl      = document.getElementById("destination");
  const opEl        = document.getElementById("operator");
  const payMethodEl = document.getElementById("paymentMethod");

  if (!srcEl || !destEl) return;

  const destVal     = (destEl.value || "").split("|");
  const source      = srcEl.value;
  const destination = destVal[0];
  const price       = destVal[1] || "0";
  const operator    = opEl ? opEl.value : "";
  const paymentMethod = payMethodEl ? payMethodEl.value : "bkash";
  const journeyDate = document.getElementById("journeyDate")?.value || new Date().toISOString().split('T')[0];
  const seatNo      = document.getElementById("seatNo")?.value || "A1";
  const seatClass   = document.getElementById("seatClass")?.value || "Economy";

  if (!destination) { showToast("Select destination ❌", "err"); return; }
  if (!operator)    { showToast("Select operator ❌",    "err"); return; }

  let payload = {
    source, destination, price, type, operator, payment_method: paymentMethod,
    journey_date: journeyDate, seat_no: seatNo, seat_class: seatClass
  };

  if (paymentMethod === "card") {
    payload.card_holder = document.getElementById("cardHolder")?.value || "";
    payload.card_number = document.getElementById("cardNumber")?.value || "";
    payload.expiry      = document.getElementById("expiry")?.value || "";
    payload.cvv         = document.getElementById("cvv")?.value || "";
  } else {
    payload.phone = document.getElementById("phone")?.value || "";
    payload.pin   = document.getElementById("pin")?.value || "";
  }

  fetch(API + "/book", {
    method:  "POST",
    headers: authHeader(),
    body:    JSON.stringify(payload)
  })
  .then(r => { if (r.status === 401) { localStorage.clear(); window.location = "/"; } return r.json(); })
  .then(d => {
    const ok = d.message && (d.message.includes("✅") || d.message.toLowerCase().includes("success"));
    showToast(d.message, ok ? "ok" : "err");
    if (ok) {
      setTimeout(loadNotifications, 1000);
      if (d.redirect_url) setTimeout(() => window.location = d.redirect_url, 1500);
    }
  })
  .catch(() => showToast("Server error ❌", "err"));
}

/* ── LOAD BOOKINGS (Dashboard) ────────────────────────────── */
function loadBookings() {
  if (!getToken()) return;
  const container = document.getElementById("bkContainer");
  if (!container) return;

  fetch(API + "/my-bookings", { headers: { "Authorization": "Bearer " + getToken() } })
    .then(r => { if (r.status === 401) { localStorage.clear(); window.location = "/"; } return r.json(); })
    .then(data => {
      const total  = data.length;
      const buses  = data.filter(b => b.ticket?.type === "Bus").length;
      const trains = data.filter(b => b.ticket?.type === "Train").length;
      const planes = data.filter(b => b.ticket?.type === "Plane").length;

      const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
      set("sTot",    total);
      set("sBus",    buses);
      set("sTrn",    trains);
      set("sPln",    planes);
      set("bkCount", total);

      if (total === 0) {
        container.innerHTML = `
          <div class="empty">
            <i class="fas fa-ticket-alt"></i>
            <h3>No bookings yet</h3>
            <p>Use the search above to book your first ticket!</p>
          </div>`;
        return;
      }

      const icons = { Bus: "🚌", Train: "🚆", Plane: "✈️" };
      const cls   = { Bus: "bus", Train: "train", Plane: "plane" };

      container.innerHTML = [...data].reverse().map(b => {
        if (!b.ticket) return "";
        const t   = b.ticket;
        const pay = b.payment || {};
        return `
          <div class="bk-card">
            <div class="bk-icon ${cls[t.type] || 'bus'}">${icons[t.type] || "🎫"}</div>
            <div class="bk-info">
              <div class="bk-route">${t.source} → ${t.destination}</div>
              <div class="bk-meta">
                <span><i class="fas fa-tag"></i>${t.type}</span>
                <span><i class="fas fa-building"></i>${b.operator || "N/A"}</span>
                <span><i class="fas fa-credit-card"></i>${pay.method || "N/A"}</span>
                ${pay.transaction_id ? `<span><i class="fas fa-receipt"></i>${pay.transaction_id}</span>` : ""}
              </div>
            </div>
            <div class="bk-right">
              <div class="bk-amount">৳${t.price}</div>
              <div class="confirmed-badge">✅ Confirmed</div>
            </div>
          </div>`;
      }).join("");
    })
    .catch(() => {
      if (container) container.innerHTML = `
        <div class="empty"><i class="fas fa-exclamation-circle"></i>
          <h3>Could not load bookings</h3>
          <p>Check server connection.</p>
        </div>`;
    });
}

/* ── NOTIFICATIONS ────────────────────────────────────────── */
function loadNotifications() {
  if (!getToken()) return;

  fetch(API + "/notifications", {
    headers: { "Authorization": "Bearer " + getToken() }
  })
  .then(res => {
    if (res.status === 401) { localStorage.clear(); window.location = "/"; return; }
    return res.json();
  })
  .then(data => {
    if (data && data.unread_count !== undefined) {
      updateNotificationBadge(data.unread_count);
    }
  })
  .catch(err => console.error("Error loading notifications:", err));
}

function updateNotificationBadge(count) {
  const badge = document.getElementById("notifBadge");
  if (!badge) return;
  if (count > 0) {
    badge.style.display = "inline-block";
    badge.textContent = count > 99 ? "99+" : count;
  } else {
    badge.style.display = "none";
  }
}

function viewNotifications() {
  if (!getToken()) { alert("Please login first"); window.location = "/"; return; }
  window.location = "/notifications-page";
}

function markNotificationAsRead(notificationId) {
  fetch(API + "/notifications/mark-read", {
    method: "POST",
    headers: authHeader(),
    body: JSON.stringify({ notification_id: notificationId })
  })
  .then(res => res.json())
  .then(() => {
    loadNotifications();
    if (window.location.pathname === "/notifications-page") location.reload();
  })
  .catch(err => console.error("Error marking as read:", err));
}

function markAllNotificationsAsRead() {
  fetch(API + "/notifications/mark-all-read", {
    method: "POST",
    headers: authHeader()
  })
  .then(res => res.json())
  .then(() => {
    loadNotifications();
    if (window.location.pathname === "/notifications-page") location.reload();
  })
  .catch(err => console.error("Error marking all as read:", err));
}

/* ── FORGOT PASSWORD ──────────────────────────────────────── */
function sendResetOTP() {
  const email = (document.getElementById("resetEmail")?.value || "").trim();
  if (!email) { showAlert("resetAlert", "Enter your email address", "err"); return; }

  fetch(API + "/forgot-password", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email })
  })
  .then(r => r.json())
  .then(d => {
    showAlert("resetAlert", d.message, d.message.includes("sent") ? "ok" : "err");
    if (d.message.includes("sent")) {
      document.getElementById("s1")?.classList.remove("active");
      document.getElementById("s2")?.classList.add("active");
      updateResetStep(2);
      if (typeof startResetTimer === "function") startResetTimer();
    }
  });
}

function verifyResetOTP() {
  const otp = (document.getElementById("resetOTP")?.value || "").trim();
  if (otp.length !== 6) { showAlert("resetAlert", "Enter the 6-digit OTP", "err"); return; }
  showAlert("resetAlert", "OTP accepted! Now set your new password.", "ok");
  document.getElementById("s2")?.classList.remove("active");
  document.getElementById("s3")?.classList.add("active");
  updateResetStep(3);
}

function resetPassword() {
  const email   = (document.getElementById("resetEmail")?.value   || "").trim();
  const otp     = (document.getElementById("resetOTP")?.value     || "").trim();
  const newpass = (document.getElementById("newpass")?.value      || "");
  const confirm = (document.getElementById("confirmpass")?.value  || "");

  if (newpass !== confirm) { showAlert("resetAlert", "Passwords do not match ❌", "err"); return; }
  if (newpass.length < 6)  { showAlert("resetAlert", "Password must be 6+ characters", "err"); return; }

  fetch(API + "/reset-password", {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ email, otp, password: newpass })
  })
  .then(r => r.json())
  .then(d => {
    const ok = d.message && (d.message.includes("success") || d.message.includes("updated"));
    showAlert("resetAlert", d.message, ok ? "ok" : "err");
    if (ok) setTimeout(() => window.location = "/", 1800);
  });
}

function updateResetStep(n) {
  [1, 2, 3].forEach(i => {
    const dot = document.getElementById("pd" + i);
    if (!dot) return;
    dot.className = "p-dot " + (i < n ? "done" : i === n ? "active" : "idle");
  });
  [1, 2].forEach(i => {
    const ln = document.getElementById("pl" + i);
    if (ln) ln.className = "p-line " + (i < n ? "done" : "");
  });
}

/* ================= SMS OTP FUNCTIONS (For Train & Plane Booking) ================= */

let otpTimerGlobal = 60;
let otpIntervalGlobal;

async function sendOTP() {
    const nid = document.getElementById("nidNumber")?.value.trim();
    const mobile = document.getElementById("mobileNumber")?.value.trim();
    
    if (!nid || nid.length < 10) {
        showMessage("verifyMsg", "Please enter a valid NID number (10-17 digits)", "err");
        return;
    }
    if (!mobile || !mobile.match(/^01[0-9]{9}$/)) {
        showMessage("verifyMsg", "Please enter a valid 11-digit Bangladesh phone number (01XXXXXXXXX)", "err");
        return;
    }
    
    const sendBtn = document.getElementById("sendOtpBtn");
    if (!sendBtn) return;
    
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    
    try {
        const response = await fetch(API + "/send-sms-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone_number: mobile, nid: nid })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage("verifyMsg", data.message, "ok");
            const otpSection = document.getElementById("otpSection");
            if (otpSection) otpSection.style.display = "block";
            startOTPTimerGlobal();
        } else {
            showMessage("verifyMsg", data.message, "err");
            sendBtn.disabled = false;
            sendBtn.innerHTML = 'Send OTP';
        }
    } catch (err) {
        showMessage("verifyMsg", "Failed to send OTP. Please try again.", "err");
        sendBtn.disabled = false;
        sendBtn.innerHTML = 'Send OTP';
    }
}

function startOTPTimerGlobal() {
    const sendBtn = document.getElementById("sendOtpBtn");
    if (!sendBtn) return;
    otpTimerGlobal = 60;
    otpIntervalGlobal = setInterval(() => {
        otpTimerGlobal--;
        if (otpTimerGlobal >= 0) {
            sendBtn.innerHTML = `Resend (${otpTimerGlobal}s)`;
        }
        if (otpTimerGlobal <= 0) {
            clearInterval(otpIntervalGlobal);
            sendBtn.disabled = false;
            sendBtn.innerHTML = 'Send OTP';
        }
    }, 1000);
}

async function verifyOTP() {
    const mobile = document.getElementById("mobileNumber")?.value.trim();
    const otp = document.getElementById("otpCode")?.value.trim();
    
    if (!otp || otp.length !== 6) {
        showMessage("verifyMsg", "Please enter the 6-digit OTP", "err");
        return;
    }
    
    const verifyBtn = document.getElementById("verifyOtpBtn");
    if (!verifyBtn) return;
    
    verifyBtn.disabled = true;
    verifyBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
    
    try {
        const response = await fetch(API + "/verify-sms-otp", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ phone_number: mobile, otp: otp })
        });
        
        const data = await response.json();
        
        if (data.verified) {
            showMessage("verifyMsg", "✓ Identity verified successfully!", "ok");
            window.isVerified = true;
            localStorage.setItem("temp_mobile", mobile);
            localStorage.setItem("temp_nid", document.getElementById("nidNumber")?.value.trim() || "");
            
            // Enable continue button
            const continueBtn = document.getElementById("continueBtn");
            if (continueBtn) {
                continueBtn.disabled = false;
                continueBtn.style.opacity = "1";
                continueBtn.style.cursor = "pointer";
            }
            
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = 'Verified ✓';
            verifyBtn.style.background = "#10b981";
            
            showToast("Identity verified! Click Continue to proceed.", "ok");
        } else {
            showMessage("verifyMsg", data.message || "Invalid OTP. Please try again.", "err");
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = 'Verify';
        }
    } catch (err) {
        console.error("Verification error:", err);
        showMessage("verifyMsg", "Verification failed. Please try again.", "err");
        verifyBtn.disabled = false;
        verifyBtn.innerHTML = 'Verify';
    }
}

function showMessage(elementId, msg, type) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = msg;
    el.className = "msg-box " + type;
    el.style.display = "block";
    setTimeout(() => {
        if (el.className === "msg-box " + type) {
            el.style.display = "none";
            el.className = "msg-box";
        }
    }, 5000);
}

function continueToSchedule() {
    if (!window.isVerified && !localStorage.getItem("temp_mobile")) {
        showToast("Please verify your identity first! ❌", "err");
        return;
    }
    
    // Get the transport type from URL or hidden input
    const path = window.location.pathname;
    let transport = "train";
    if (path.includes("bus")) transport = "bus";
    else if (path.includes("plane")) transport = "plane";
    else if (path.includes("train")) transport = "train";
    
    // Redirect to schedule selection page
    window.location = `/schedule-selection?type=${transport}`;
}

/* ── INIT: notifications on dashboard ─────────────────────── */
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", function () {
    if (getToken() && window.location.pathname === "/dashboard") {
      loadNotifications();
      setInterval(loadNotifications, 30000);
    }
  });
} else {
  if (getToken() && window.location.pathname === "/dashboard") {
    loadNotifications();
    setInterval(loadNotifications, 30000);
  }
}
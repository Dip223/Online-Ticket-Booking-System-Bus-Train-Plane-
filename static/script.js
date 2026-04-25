const API = "http://127.0.0.1:5000";


// ================= HELPER =================
function getToken() {
    return localStorage.getItem("token");
}

function authHeader() {
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + getToken()
    };
}

function handleAuthError(res) {
    if (res.status === 401) {
        alert("Session expired. Please login again ❌");
        localStorage.removeItem("token");
        window.location = "/";
    }
}


// ================= LOGIN =================
function login() {
    fetch(API + "/login", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) {
            alert("Login Success ✅");
            localStorage.setItem("token", data.token);
            window.location = "/dashboard";
        } else {
            alert(data.message || "Login Failed ❌");
        }
    });
}


// ================= REGISTER =================
let otpTimer = 60;

function register() {
    fetch(API + "/send-register-otp", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            password: document.getElementById("password").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        document.getElementById("otpBox").style.display = "block";
        startOTPTimer();
    });
}


// ================= OTP TIMER =================
function startOTPTimer() {
    let btn = document.getElementById("resendBtn");

    if (!btn) return;

    btn.disabled = true;

    let interval = setInterval(() => {
        btn.innerText = "Resend OTP (" + otpTimer + "s)";
        otpTimer--;

        if (otpTimer < 0) {
            clearInterval(interval);
            btn.disabled = false;
            btn.innerText = "Resend OTP";
            otpTimer = 60;
        }
    }, 1000);
}


// ================= VERIFY OTP =================
function verifyRegisterOTP() {
    fetch(API + "/verify-register-otp", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            email: document.getElementById("email").value,
            otp: document.getElementById("otp").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);

        if (data.message.toLowerCase().includes("success")) {
            window.location = "/";
        }
    });
}


// ================= NAVIGATION =================
function goBus() { window.location = "/bus"; }
function goTrain() { window.location = "/train"; }
function goPlane() { window.location = "/plane"; }


// ================= LOAD ROUTES =================
function loadPlaneRoutes() {
    fetch(API + "/plane-routes")
    .then(res => res.json())
    .then(data => fillRoutesAndOperators(data, "Plane"));
}

function loadBusRoutes() {
    fetch(API + "/bus-routes")
    .then(res => res.json())
    .then(data => fillRoutesAndOperators(data, "Bus"));
}

function loadTrainRoutes() {
    fetch(API + "/train-routes")
    .then(res => res.json())
    .then(data => fillRoutesAndOperators(data, "Train"));
}


// ================= FILL ROUTES =================
function fillRoutesAndOperators(data, type) {
    let routeSelect = document.getElementById("route");
    let operatorSelect = document.getElementById("operator");

    if (!routeSelect || !operatorSelect) return;

    routeSelect.innerHTML = "";
    operatorSelect.innerHTML = "";

    data.routes.forEach(r => {
        routeSelect.innerHTML += `
            <option value="${r.from}|${r.to}|${r.price}|${type}">
                ${r.from} → ${r.to} (৳${r.price})
            </option>
        `;
    });

    data.operators.forEach(op => {
        operatorSelect.innerHTML += `
            <option value="${op}">${op}</option>
        `;
    });
}


// ================= BOOK =================
function book() {
    let routeValue = document.getElementById("route").value;
    let operator = document.getElementById("operator").value;

    if (!routeValue) {
        alert("Select route first ❌");
        return;
    }

    if (!getToken()) {
        alert("Please login first ❌");
        window.location = "/";
        return;
    }

    let val = routeValue.split("|");

    fetch(API + "/book", {
        method: "POST",
        headers: authHeader(),
        body: JSON.stringify({
            source: val[0],
            destination: val[1],
            price: val[2],
            type: val[3],
            operator: operator,
            payment: document.getElementById("payment").value
        })
    })
    .then(res => {
        handleAuthError(res);
        return res.json();
    })
    .then(data => {
        alert(data.message);
    });
}


// ================= LOAD BOOKINGS =================
function loadBookings() {
    if (!getToken()) return;

    fetch(API + "/my-bookings", {
        headers: {
            "Authorization": "Bearer " + getToken()
        }
    })
    .then(res => {
        handleAuthError(res);
        return res.json();
    })
    .then(data => {
        let html = "";

        if (data.length === 0) {
            html = "<p>No bookings yet 😕</p>";
        }

        data.forEach(b => {
            html += `
                <div style="border:1px solid #ccc; margin:10px; padding:10px; border-radius:8px;">
                    <b>${b.ticket.type}</b><br>
                    ${b.ticket.source} → ${b.ticket.destination}<br>
                    Operator: ${b.operator || "N/A"}<br>
                    Price: ৳${b.ticket.price}<br>
                    <span style="color:green">${b.payment}</span>
                </div>
            `;
        });

        document.getElementById("tickets").innerHTML = html;
    });
}


// ================= PASSWORD RESET =================
function sendResetOTP() {
    fetch(API + "/forgot-password", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            email: document.getElementById("email").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function resetPassword() {
    fetch(API + "/reset-password", {
        method:"POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            email: document.getElementById("email").value,
            otp: document.getElementById("otp").value,
            password: document.getElementById("newpass").value
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}


// ================= AUTO LOAD =================
window.onload = function() {
    loadBookings();
};
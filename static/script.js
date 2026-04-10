const API = "http://127.0.0.1:5000";

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
        if (data._id) {
            alert("Login Success ✅");
            localStorage.setItem("user_id", data._id);
            window.location = "/dashboard";
        } else {
            alert("Login Failed ❌");
        }
    });
}


// ================= REGISTER =================
function register() {
    fetch(API + "/register", {
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
        window.location = "/";
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


// ================= FILL ROUTES + OPERATORS =================
function fillRoutesAndOperators(data, type) {
    let routeSelect = document.getElementById("route");
    let operatorSelect = document.getElementById("operator");

    if (!routeSelect || !operatorSelect) return;

    routeSelect.innerHTML = "";
    operatorSelect.innerHTML = "";

    // Routes
    data.routes.forEach(r => {
        routeSelect.innerHTML += `
            <option value="${r.from}|${r.to}|${r.price}|${type}">
                ${r.from} → ${r.to} (৳${r.price})
            </option>
        `;
    });

    // Operators
    data.operators.forEach(op => {
        operatorSelect.innerHTML += `
            <option value="${op}">${op}</option>
        `;
    });
}


// ================= BOOKING =================
function book(type) {
    let routeValue = document.getElementById("route").value;
    let operator = document.getElementById("operator").value;

    if (!routeValue) {
        alert("Please select a route ❌");
        return;
    }

    let val = routeValue.split("|");

    fetch(API + "/book", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
            user_id: localStorage.getItem("user_id"),
            source: val[0],
            destination: val[1],
            price: val[2],
            type: val[3],
            operator: operator, // ✅ NEW
            payment: document.getElementById("payment").value
        })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    });
}

// optional (not required but kept)
function bookPlane() { book("Plane"); }
function bookBus() { book("Bus"); }
function bookTrain() { book("Train"); }


// ================= LOAD BOOKINGS =================
function loadBookings() {
    fetch(API + "/my-bookings?user_id=" + localStorage.getItem("user_id"))
    .then(res => res.json())
    .then(data => {
        let html = "";

        data.forEach(b => {
    html += `
        <div style="border:1px solid #ccc; margin:10px; padding:10px;">
            <b>${b.ticket.type}</b><br>
            ${b.ticket.source} → ${b.ticket.destination}<br>
            Operator: ${b.operator} <br>
            Price: ৳${b.ticket.price}<br>
            ${b.payment}
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
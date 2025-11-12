/* ====== CONFIG ====== */
const API_BASE = "http://127.0.0.1:8000";  // Django backend server base
const ENDPOINTS = {
  signup:       "/api/auth/signup/",
  verifyOTP:    "/api/auth/verify-otp/",
  login:        "/api/auth/login/",
  google:       "/api/auth/google/",
  resumeUpload: "/api/resume/upload/",
};

/* ====== TOKEN STORAGE ====== */

// Save JWT tokens (called after login or OTP verify)
function saveTokens({ access, refresh }) {
  localStorage.setItem("access", access);
  localStorage.setItem("refresh", refresh);
}

// Store logged-in user info (optional, for dashboard greeting)
function saveUser({ name, email }) {
  localStorage.setItem("user", JSON.stringify({ name, email }));
}

// Get access token
function getAccess() {
  return localStorage.getItem("access");
}

// Quick auth check for protected pages (like dashboard)
function requireAuthOrRedirect() {
  if (!getAccess()) {
    alert("⚠️ Session expired or not logged in!");
    window.location.href = "login.html";
  }
}

// Logout user
function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("user");
  sessionStorage.removeItem("signupEmail");
  alert("You’ve been logged out.");
  window.location.href = "login.html";
}

/* ====== FETCH HELPERS ====== */

// Generic JSON POST (no auth required)
async function postJSON(path, body) {
  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res;
}

// Authenticated multipart/form-data (for file uploads)
async function postFile(path, formData) {
  const token = getAccess();
  if (!token) {
    alert("Session expired! Please log in again.");
    window.location.href = "login.html";
    return;
  }

  const res = await fetch(API_BASE + path, {
    method: "POST",
    headers: { "Authorization": "Bearer " + token },
    body: formData, // Browser auto sets multipart boundaries
  });

  return res;
}

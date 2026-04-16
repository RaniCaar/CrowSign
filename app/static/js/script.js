const form = document.getElementById("loginForm");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const profileSelect = document.getElementById("profile");
const feedback = document.getElementById("feedback");
const guestButton = document.getElementById("guestMode");
const togglePasswordBtn = document.querySelector(".toggle-password");

function setFieldError(input, message) {
  const msgEl = document.querySelector(`.field-message[data-for="${input.id}"]`);
  if (msgEl) msgEl.textContent = message || "";
  if (message) {
    input.classList.add("input-error");
  } else {
    input.classList.remove("input-error");
  }
}

function clearStatus() {
  feedback.textContent = "";
  feedback.classList.remove("success", "error");
}

function validateForm() {
  let isValid = true;
  clearStatus();

  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  if (!email) {
    setFieldError(emailInput, "Ingresa tu correo o nombre de usuario.");
    isValid = false;
  } else {
    setFieldError(emailInput, "");
  }

  if (!password) {
    setFieldError(passwordInput, "La contraseña es obligatoria.");
    isValid = false;
  } else if (password.length < 4) {
    setFieldError(passwordInput, "Usa al menos 4 caracteres.");
    isValid = false;
  } else {
    setFieldError(passwordInput, "");
  }

  if (!isValid) {
    document.querySelector(".login-card")?.classList.add("shake");
    setTimeout(() => {
      document.querySelector(".login-card")?.classList.remove("shake");
    }, 320);
  }

  return isValid;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  clearStatus();

  if (!validateForm()) {
    feedback.textContent = "Revisa los campos resaltados antes de continuar.";
    feedback.classList.add("error");
    return;
  }

  const profile = profileSelect.value;
  const userName = emailInput.value.split("@")[0] || "explorador";

  feedback.textContent = "Verificando credenciales con el búho...";
  feedback.classList.remove("error");
  feedback.classList.add("success");

  setTimeout(() => {
    feedback.textContent =
      `✨ ¡Bienvenido, ${userName}! ` +
      (profile === "teacher"
        ? "Modo docente activado. El búho está listo para guiar a tus estudiantes."
        : profile === "student"
        ? "Modo estudiante activado. Practiquemos nuevas señas juntos."
        : "Modo invitado activado. Explora el lector de señas libremente.");
        
    sessionStorage.setItem('hootsign_session', JSON.stringify({ email: userName, profile }));
    setTimeout(() => window.location.href = 'lector.html', 1500);
  }, 700);
});

guestButton.addEventListener("click", () => {
  clearStatus();
  profileSelect.value = "guest";
  feedback.textContent =
    "Has entrado en modo invitado. Explorando el lector de señas libremente...";
  feedback.classList.add("success");
  sessionStorage.setItem('hootsign_session', JSON.stringify({ email: "Invitado", profile: "guest" }));
  setTimeout(() => window.location.href = 'lector.html', 1000);
});

togglePasswordBtn.addEventListener("click", () => {
  const isPassword = passwordInput.type === "password";
  passwordInput.type = isPassword ? "text" : "password";
  togglePasswordBtn.textContent = isPassword ? "🙈" : "👁";
});

document.getElementById("forgotPassword")?.addEventListener("click", () => {
  clearStatus();
  feedback.textContent =
    "Próximamente podrás recuperar tu contraseña. Por ahora, usa una cuenta temporal o modo invitado.";
  feedback.classList.add("success");
});


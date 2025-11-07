// Navigation helper - loads page in SPA manner (if desired)
function navigate(page) {
  window.location.href = page + ".html";
}

// Toast notification helper
function showToast(message, type) {
  const container = document.getElementById("toast-container");
  const color = type === "success" ? "bg-green-500" : "bg-red-500";
  const html = `<div class="${color} text-white p-3 rounded-lg shadow-xl mb-3 transition-opacity duration-300 transform translate-y-0 opacity-100">${message}</div>`;
  container.insertAdjacentHTML("beforeend", html);
  const newToast = container.lastElementChild;
  setTimeout(() => {
    newToast.classList.add("opacity-0", "translate-y-2");
    newToast.addEventListener("transitionend", () => newToast.remove());
  }, 3000);
}

// Simple debounce helper
function debounce(func, wait = 300) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

// Example: Attach to navigation links automatically to enable SPA behavior (if implemented)
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("nav a").forEach(link => {
    if (link.href && !link.target) {
      link.addEventListener("click", e => {
        e.preventDefault();
        const page = link.getAttribute("href").replace(".html", "");
        navigate(page);
      });
    }
  });
});

// Global utility to validate email format
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(String(email).toLowerCase());
}

// More shared functions can be added here such as API wrappers, auth token handlers, form helpers, etc.

// Export functions if using modules (optional)
// export { showToast, navigate, validateEmail };

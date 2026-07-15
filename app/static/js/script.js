document.addEventListener("DOMContentLoaded", function () {
  /* ── Theme Toggle ── */
  const themeToggle = document.getElementById("theme-toggle");
  const root = document.documentElement;
  const themeMeta = document.querySelector('meta[name="theme-color"]');

  const applyTheme = (theme) => {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("portfolio-theme", theme);
    if (themeToggle) {
      themeToggle.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      );
      themeToggle.setAttribute(
        "title",
        theme === "dark" ? "Light mode" : "Dark mode"
      );
    }
    if (themeMeta) {
      themeMeta.setAttribute("content", theme === "light" ? "#ffffff" : "#050505");
    }
  };

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
    applyTheme(root.getAttribute("data-theme") || "dark");
  }

  /* ── Mobile Menu ── */
  const menuButton = document.querySelector(".mobile-menu-btn");
  const nav = document.querySelector(".primary-nav");

  if (menuButton && nav) {
    menuButton.addEventListener("click", () => {
      const isExpanded = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!isExpanded));
      nav.classList.toggle("is-open");
      menuButton.querySelector("i").className = !isExpanded
        ? "fa-solid fa-xmark"
        : "fa-solid fa-bars";
    });

    document.querySelectorAll(".primary-nav a").forEach((link) => {
      link.addEventListener("click", () => {
        if (nav.classList.contains("is-open")) {
          nav.classList.remove("is-open");
          menuButton.setAttribute("aria-expanded", "false");
          menuButton.querySelector("i").className = "fa-solid fa-bars";
        }
      });
    });
  }

  /* ── Navbar scroll effect ── */
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => {
      header.classList.toggle("scrolled", window.scrollY > 30);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ── Scroll reveal ── */
  const reveals = document.querySelectorAll(".reveal");
  if (reveals.length > 0 && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
    );
    reveals.forEach((el) => observer.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("visible"));
  }



  /* Contact form AJAX */
  const contactForm = document.querySelector("[data-contact-form]");
  if (contactForm) {
    const statusBox = contactForm.querySelector("[data-contact-status]");
    const submitButton = contactForm.querySelector(".contact-submit");
    const submitLabel = submitButton ? submitButton.querySelector("span") : null;
    const clearErrors = () => {
      contactForm.querySelectorAll(".form-error.js-error").forEach((item) => item.remove());
      contactForm.querySelectorAll(".form-input.is-invalid").forEach((item) => item.classList.remove("is-invalid"));
    };
    const setStatus = (message, type) => {
      if (!statusBox) return;
      statusBox.textContent = message || "";
      statusBox.className = `contact-form-status ${type ? "is-" + type : ""}`;
    };
    const showErrors = (errors) => {
      Object.entries(errors || {}).forEach(([field, messages]) => {
        const input = contactForm.querySelector(`[name="${field}"]`);
        const error = document.createElement("p");
        error.className = "form-error js-error";
        error.textContent = Array.isArray(messages) ? messages.join(" ") : String(messages);
        if (input) {
          input.classList.add("is-invalid");
          input.closest(".form-group")?.appendChild(error);
        } else {
          contactForm.appendChild(error);
        }
      });
    };

    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearErrors();
      setStatus("Sending your message...", "loading");
      if (submitButton) submitButton.disabled = true;
      if (submitLabel) submitLabel.textContent = "Sending";

      try {
        const response = await fetch(contactForm.action || window.location.href, {
          method: "POST",
          body: new FormData(contactForm),
          headers: {
            "X-Requested-With": "XMLHttpRequest",
            Accept: "application/json",
          },
        });
        const payload = await response.json();
        if (!response.ok || payload.ok === false) {
          showErrors(payload.errors || { form: ["Please check the form and try again."] });
          setStatus("Please fix the highlighted fields.", "error");
          return;
        }
        contactForm.reset();
        setStatus(payload.message || "Message sent successfully.", payload.email_sent === false ? "warning" : "success");
      } catch (error) {
        setStatus("Something went wrong. Please try again or email me directly.", "error");
      } finally {
        if (submitButton) submitButton.disabled = false;
        if (submitLabel) submitLabel.textContent = "Send Message";
      }
    });
  }

  /* Pointer tilt for premium cards */
  const canTilt = window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (canTilt) {
    document.querySelectorAll(".project-story, .blog-card, .resource-card-premium").forEach((card) => {
      card.addEventListener("pointermove", (event) => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;
        card.style.setProperty("--tilt-x", `${(-y * 4).toFixed(2)}deg`);
        card.style.setProperty("--tilt-y", `${(x * 4).toFixed(2)}deg`);
      });
      card.addEventListener("pointerleave", () => {
        card.style.removeProperty("--tilt-x");
        card.style.removeProperty("--tilt-y");
      });
    });
  }

  /* ── Auto-dismiss alerts ── */
  document.querySelectorAll(".alert").forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-8px)";
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  });
});

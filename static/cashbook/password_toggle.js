document.querySelectorAll("[data-password-toggle]").forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.getAttribute("aria-controls"));
    if (!input) return;

    const isVisible = input.type === "password";
    input.type = isVisible ? "text" : "password";
    button.setAttribute("aria-pressed", String(isVisible));

    const label = isVisible ? button.dataset.hideLabel : button.dataset.showLabel;
    button.setAttribute("aria-label", label);
    button.title = label;
  });
});

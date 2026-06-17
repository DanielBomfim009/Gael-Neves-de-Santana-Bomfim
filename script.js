const panelTriggers = document.querySelectorAll("[data-panel-target]");
const panelClosers = document.querySelectorAll("[data-close-panel]");

function openPanel(id) {
  const panel = document.getElementById(id);
  if (!panel) return;
  const trigger = document.querySelector(`[data-panel-target="${id}"]`);
  panel.hidden = false;
  panel.classList.add("is-open");
  if (trigger) {
    trigger.setAttribute("aria-expanded", "true");
  }
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closePanel(id) {
  const panel = document.getElementById(id);
  if (!panel) return;
  const trigger = document.querySelector(`[data-panel-target="${id}"]`);
  panel.classList.remove("is-open");
  if (trigger) {
    trigger.setAttribute("aria-expanded", "false");
  }
  window.setTimeout(() => {
    panel.hidden = true;
  }, 180);
  const invite = document.getElementById("convite");
  if (invite) {
    invite.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

panelTriggers.forEach((trigger) => {
  trigger.setAttribute("aria-expanded", "false");
  trigger.addEventListener("click", () => {
    openPanel(trigger.dataset.panelTarget);
  });
});

panelClosers.forEach((closer) => {
  closer.addEventListener("click", () => {
    closePanel(closer.dataset.closePanel);
  });
});

const panelTriggers = document.querySelectorAll("[data-panel-target]");
const panelClosers = document.querySelectorAll("[data-close-panel]");

function openPanel(id) {
  const panel = document.getElementById(id);
  if (!panel) return;
  panel.hidden = false;
  panel.classList.add("is-open");
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function closePanel(id) {
  const panel = document.getElementById(id);
  if (!panel) return;
  panel.classList.remove("is-open");
  window.setTimeout(() => {
    panel.hidden = true;
  }, 180);
  const invite = document.getElementById("convite");
  if (invite) {
    invite.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

panelTriggers.forEach((trigger) => {
  trigger.addEventListener("click", () => {
    openPanel(trigger.dataset.panelTarget);
  });
});

panelClosers.forEach((closer) => {
  closer.addEventListener("click", () => {
    closePanel(closer.dataset.closePanel);
  });
});

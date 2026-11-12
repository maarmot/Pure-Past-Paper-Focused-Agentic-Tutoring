try {
  await import("./app.mjs");
} catch {
  document.getElementById("topic").textContent = "Roadmap unavailable";
  const message = document.getElementById("alert");
  message.hidden = false;
  message.textContent =
    "The application could not start. Restart the local server and reload this page. Your saved data stays in this browser.";
  for (const control of document.querySelectorAll("main button, header button"))
    control.disabled = true;
}

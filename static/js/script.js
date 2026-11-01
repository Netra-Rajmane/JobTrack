document.addEventListener("DOMContentLoaded", () => {
  // Dismiss flash notifications automatically after a short delay.
  document.querySelectorAll(".flash").forEach((message) => {
    window.setTimeout(() => {
      if (message.isConnected) message.remove();
    }, 5000);
  });
});

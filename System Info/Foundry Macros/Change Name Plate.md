const drawingId = "CMQEQhZZ2Fa16W6M"; // <-- Replace with your drawing's ID

const drawing = canvas.drawings.get(drawingId);
if (!drawing) return ui.notifications.warn("Drawing not found.");

await drawing.document.update({
  text: "Veyric Thorne"
});

const viewport = document.querySelector(".viewport");
if (!viewport) {
  // Not on the landing page.
  return;
}

const videos = Array.from(viewport.querySelectorAll("video"));
if (videos.length === 0) {
  return;
}

let current = 0;
let startX = 0;

function show(index) {
  const safeIndex = ((index % videos.length) + videos.length) % videos.length;
  current = safeIndex;

  videos.forEach((v, i) => {
    v.classList.toggle("active", i === current);
    v.pause();
    v.muted = true;
    v.currentTime = 0;
  });

  videos[current].play().catch(() => {});
}

videos.forEach(video => {
  video.addEventListener("click", () => {
    video.muted = !video.muted;
    if (!video.muted) {
      video.currentTime = 0;
      video.play().catch(() => {});
    }
  });
});

viewport.addEventListener("touchstart", e => {
  startX = e.touches[0].clientX;
}, { passive: true });

viewport.addEventListener("touchend", e => {
  const deltaX = e.changedTouches[0].clientX - startX;
  if (Math.abs(deltaX) < 40) return;

  show(deltaX < 0 ? current + 1 : current - 1);
}, { passive: true });

show(0);

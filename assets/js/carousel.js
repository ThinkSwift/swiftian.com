const videos = Array.from(document.querySelectorAll(".viewport video"));
let current = 0;
let startX = 0;

function show(index) {
  videos.forEach((v, i) => {
    v.classList.toggle("active", i === index);
    v.pause();
    v.muted = true;
    v.currentTime = 0;
  });

  videos[index].play().catch(() => {});
}

videos.forEach(video => {
  video.addEventListener("click", () => {
    video.muted = !video.muted;
    if (!video.muted) {
      video.currentTime = 0;
      video.play();
    }
  });
});

const viewport = document.querySelector(".viewport");

viewport.addEventListener("touchstart", e => {
  startX = e.touches[0].clientX;
});

viewport.addEventListener("touchend", e => {
  const deltaX = e.changedTouches[0].clientX - startX;
  if (Math.abs(deltaX) < 40) return;

  if (deltaX < 0) {
    current = (current + 1) % videos.length;
  } else {
    current = (current - 1 + videos.length) % videos.length;
  }
  show(current);
});

show(current);

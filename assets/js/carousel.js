(() => {
  const root = document.querySelector("[data-carousel]");
  if (!root) return;

  const frame = root.querySelector("[data-frame]");
  const videos = Array.from(root.querySelectorAll("video.clip"));
  const prev = root.querySelector(".nav-prev");
  const next = root.querySelector(".nav-next");
  const dotsHost = document.querySelector("[data-dots]");
  const audioToggle = root.querySelector("[data-audio-toggle]");

  if (!frame || videos.length === 0 || !dotsHost) return;

  let index = 0;
  let startX = 0;

  const dots = videos.map((_, i) => {
    const d = document.createElement("span");
    if (i === 0) d.classList.add("is-active");
    dotsHost.appendChild(d);
    return d;
  });

  function stopAll() {
    videos.forEach(v => {
      v.pause();
      v.muted = true;
      v.currentTime = 0;
      v.classList.remove("is-active");
    });
  }

  function show(i) {
    index = (i + videos.length) % videos.length;

    stopAll();

    const v = videos[index];
    v.classList.add("is-active");
    dots.forEach((d, di) => d.classList.toggle("is-active", di === index));

    v.play().catch(() => {});
  }

  function step(dir) {
    show(index + dir);
  }

  prev?.addEventListener("click", () => step(-1));
  next?.addEventListener("click", () => step(1));

  // Tap video: toggle mute
  videos.forEach(v => {
    v.addEventListener("click", () => {
      const isActive = v.classList.contains("is-active");
      if (!isActive) return;

      v.muted = !v.muted;
      if (!v.muted) {
        v.currentTime = 0;
        v.play().catch(() => {});
        audioToggle.textContent = "Tap to mute";
      } else {
        audioToggle.textContent = "Tap to listen";
      }
    });
  });

  // Optional button (same behavior as tapping video)
  audioToggle?.addEventListener("click", () => {
    const v = videos[index];
    v.muted = !v.muted;
    if (!v.muted) {
      v.currentTime = 0;
      v.play().catch(() => {});
      audioToggle.textContent = "Tap to mute";
    } else {
      audioToggle.textContent = "Tap to listen";
    }
  });

  // Swipe (mobile)
  frame.addEventListener("touchstart", e => {
    startX = e.touches[0].clientX;
  }, { passive: true });

  frame.addEventListener("touchend", e => {
    const dx = e.changedTouches[0].clientX - startX;
    if (Math.abs(dx) < 40) return;
    step(dx < 0 ? 1 : -1);
    audioToggle.textContent = "Tap to listen";
  }, { passive: true });

  show(0);
})();

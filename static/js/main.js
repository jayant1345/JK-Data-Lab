'use strict';

// ── Scroll Progress Bar ───────────────────────────────────
(function () {
  const bar = document.getElementById('scroll-progress');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const pct = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  }, { passive: true });
})();

// ── Navbar scroll effect ──────────────────────────────────
(function () {
  const nav = document.getElementById('navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  }, { passive: true });
})();

// ── Mobile nav toggle ─────────────────────────────────────
(function () {
  const toggle = document.getElementById('nav-toggle');
  const links = document.getElementById('nav-links');
  if (!toggle || !links) return;
  toggle.addEventListener('click', () => links.classList.toggle('open'));
  document.addEventListener('click', (e) => {
    if (!toggle.contains(e.target) && !links.contains(e.target)) links.classList.remove('open');
  });
})();

// ── Typing effect ─────────────────────────────────────────
(function () {
  const el = document.getElementById('typed-text');
  if (!el) return;
  const phrases = ['Data Science Consulting', 'AI & ML Development', 'NLP Solutions', 'RAG Systems', 'Python Automation', 'Interactive Dashboards'];
  let phraseIdx = 0, charIdx = 0, deleting = false;
  function tick() {
    const phrase = phrases[phraseIdx];
    el.textContent = deleting ? phrase.slice(0, charIdx--) : phrase.slice(0, charIdx++);
    let delay = deleting ? 60 : 90;
    if (!deleting && charIdx > phrase.length) { delay = 1800; deleting = true; }
    else if (deleting && charIdx < 0) { deleting = false; charIdx = 0; phraseIdx = (phraseIdx + 1) % phrases.length; delay = 400; }
    setTimeout(tick, delay);
  }
  tick();
})();

// ── Portfolio filter ──────────────────────────────────────
(function () {
  const btns = document.querySelectorAll('.portfolio-filter .filter-btn[data-filter]');
  const cards = document.querySelectorAll('#portfolio-grid .project-card');
  if (!btns.length) return;
  btns.forEach(btn => {
    btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.dataset.filter;
      cards.forEach(card => {
        const show = filter === 'all' || card.dataset.category === filter;
        card.style.display = show ? '' : 'none';
      });
    });
  });
})();

// ── Testimonials slider ───────────────────────────────────
(function () {
  const track = document.getElementById('testimonials-track');
  const dotsContainer = document.getElementById('slider-dots');
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  if (!track) return;
  const cards = track.children;
  let current = 0;
  const total = cards.length;
  if (!total) return;

  // Build dots
  if (dotsContainer) {
    for (let i = 0; i < total; i++) {
      const dot = document.createElement('div');
      dot.className = 'dot' + (i === 0 ? ' active' : '');
      dot.addEventListener('click', () => goto(i));
      dotsContainer.appendChild(dot);
    }
  }

  function goto(idx) {
    current = (idx + total) % total;
    const cardWidth = cards[0].offsetWidth + 24; // gap
    track.style.transform = `translateX(-${current * cardWidth}px)`;
    if (dotsContainer) {
      dotsContainer.querySelectorAll('.dot').forEach((d, i) => d.classList.toggle('active', i === current));
    }
  }

  if (prevBtn) prevBtn.addEventListener('click', () => goto(current - 1));
  if (nextBtn) nextBtn.addEventListener('click', () => goto(current + 1));

  // Auto-advance
  setInterval(() => goto(current + 1), 5000);
})();

// ── Animated counters ─────────────────────────────────────
(function () {
  const counters = document.querySelectorAll('.stat-counter');
  if (!counters.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.target, 10);
      let count = 0;
      const step = Math.ceil(target / 60);
      const timer = setInterval(() => {
        count = Math.min(count + step, target);
        el.textContent = count;
        if (count >= target) clearInterval(timer);
      }, 30);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(c => observer.observe(c));
})();

// ── Skill bar animation ───────────────────────────────────
(function () {
  const fills = document.querySelectorAll('.skill-fill');
  if (!fills.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.width = entry.target.dataset.width + '%';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });
  fills.forEach(f => observer.observe(f));
})();

// ── AOS (scroll reveal) ───────────────────────────────────
(function () {
  const els = document.querySelectorAll('[data-aos]');
  if (!els.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('aos-animate'); observer.unobserve(e.target); } });
  }, { threshold: 0.1 });
  els.forEach(el => observer.observe(el));
})();

// ── Smooth scroll for anchor links ────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// ── Auto-dismiss flash messages ───────────────────────────
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => f.remove());
}, 6000);

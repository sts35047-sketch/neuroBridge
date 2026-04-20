// ===== RESPONSIVE MENU MANAGEMENT =====

/**
 * Initialize responsive mobile menu for all templates
 * Call this function in your template's main script
 */
function initResponsiveMenu() {
  const hamburger = document.querySelector('.hamburger');
  const mobileNav = document.querySelector('.mobile-nav');
  
  if (!hamburger || !mobileNav) return;

  // Toggle mobile menu
  hamburger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    hamburger.classList.toggle('open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close on link click
  mobileNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', closeMobileMenu);
  });

  // Close on outside click
  mobileNav.addEventListener('click', (e) => {
    if (e.target === mobileNav) closeMobileMenu();
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeMobileMenu();
  });

  // Close menu function
  function closeMobileMenu() {
    mobileNav.classList.remove('open');
    hamburger.classList.remove('open');
    document.body.style.overflow = '';
  }

  // Expose globally
  window.closeMobileMenu = closeMobileMenu;
}

/**
 * Adaptive Three.js scaling for responsive canvas
 * Use this in dashboard and pages with 3D visualization
 */
function getAdaptiveThreeScale() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const aspect = w / h;
  
  let scale = 1;
  if (w < 360) scale = 0.45;
  else if (w < 420) scale = 0.54;
  else if (w < 520) scale = 0.62;
  else if (w < 640) scale = 0.70;
  else if (w < 768) scale = 0.80;
  else if (w < 1024) scale = 0.90;
  
  // Adjust for portrait orientation
  if (aspect < 0.6) scale *= 0.92;
  
  return Math.max(0.35, scale);
}

/**
 * Adaptive Three.js camera Z position for responsive camera
 */
function getAdaptiveThreeZoom() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  const aspect = w / h;
  
  let z = 112;
  if (w < 360) z = 190;
  else if (w < 420) z = 178;
  else if (w < 520) z = 165;
  else if (w < 640) z = 152;
  else if (w < 768) z = 140;
  else if (w < 1024) z = 126;
  
  // Adjust for portrait orientation
  if (aspect < 0.6) z += 18;
  
  return z;
}

/**
 * Responsive neural network node count for Three.js scenes
 */
function getResponsiveNodeCount() {
  const w = window.innerWidth;
  if (w < 360) return 80;
  if (w < 480) return 100;
  if (w < 768) return 140;
  if (w < 1024) return 200;
  return 300;
}

/**
 * Device type detection
 */
function getDeviceType() {
  const w = window.innerWidth;
  if (w < 480) return 'mobile';
  if (w < 768) return 'tablet-portrait';
  if (w < 1024) return 'tablet-landscape';
  return 'desktop';
}

/**
 * Check if device supports hover
 */
function supportsHover() {
  return window.matchMedia('(hover: hover)').matches;
}

/**
 * Check if user prefers reduced motion
 */
function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Initialize responsive event listeners
 */
function initResponsiveListeners() {
  // Update on resize
  window.addEventListener(
    'resize',
    debounce(() => {
      document.documentElement.style.setProperty('--device-type', getDeviceType());
    }, 250),
    { passive: true }
  );

  // Set initial device type
  document.documentElement.style.setProperty('--device-type', getDeviceType());
}

/**
 * Debounce utility function
 */
function debounce(func, delay) {
  let timeoutId;
  return function (...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * Apply responsive utilities on page load
 */
document.addEventListener('DOMContentLoaded', () => {
  initResponsiveMenu();
  initResponsiveListeners();
});

// Fallback for pages that might not trigger DOMContentLoaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initResponsiveMenu();
    initResponsiveListeners();
  });
} else {
  initResponsiveMenu();
  initResponsiveListeners();
}

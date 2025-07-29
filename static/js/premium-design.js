// Premium SaaS Design Interactions
class PremiumDesign {
  constructor() {
    this.init();
  }

  init() {
    this.initAnimations();
    this.initInteractions();
    this.initNavigation();
    this.initForms();
    this.initModals();
  }

  // Initialize scroll animations
  initAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in');
          
          // Add stagger animation to children
          const children = entry.target.querySelectorAll('.animate-stagger > *');
          children.forEach((child, index) => {
            child.style.setProperty('--stagger', index);
            child.classList.add('animate-slide-up');
          });
        }
      });
    }, observerOptions);

    // Observe all sections
    document.querySelectorAll('section').forEach(section => {
      observer.observe(section);
    });
  }

  // Initialize interactive elements
  initInteractions() {
    // Button ripple effect
    document.querySelectorAll('.btn-premium').forEach(button => {
      button.addEventListener('click', this.createRipple);
    });

    // Parallax effects
    window.addEventListener('scroll', this.handleParallax);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', this.smoothScroll);
    });
  }

  // Create ripple effect on button click
  createRipple(e) {
    const button = e.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;

    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(255, 255, 255, 0.5);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => ripple.remove(), 600);
  }

  // Handle parallax scrolling
  handleParallax() {
    const scrolled = window.pageYOffset;
    const parallaxElements = document.querySelectorAll('.parallax');
    
    parallaxElements.forEach(element => {
      const speed = element.dataset.speed || 0.5;
      const yPos = -(scrolled * speed);
      element.style.transform = `translateY(${yPos}px)`;
    });
  }

  // Smooth scroll for anchor links
  smoothScroll(e) {
    e.preventDefault();
    const target = document.querySelector(e.currentTarget.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }

  // Initialize navigation
  initNavigation() {
    const navbar = document.querySelector('nav');
    if (!navbar) return;

    // Navbar scroll effect
    window.addEventListener('scroll', () => {
      if (window.scrollY > 100) {
        navbar.classList.add('bg-white/95', 'backdrop-blur-sm', 'shadow-lg');
        navbar.classList.remove('bg-transparent');
      } else {
        navbar.classList.remove('bg-white/95', 'backdrop-blur-sm', 'shadow-lg');
        navbar.classList.add('bg-transparent');
      }
    });

    // Mobile menu toggle
    const mobileToggle = document.querySelector('[data-mobile-toggle]');
    const mobileMenu = document.querySelector('[data-mobile-menu]');
    
    if (mobileToggle && mobileMenu) {
      mobileToggle.addEventListener('click', () => {
        mobileMenu.classList.toggle('hidden');
      });
    }
  }

  // Initialize form enhancements
  initForms() {
    // Floating labels
    document.querySelectorAll('input, textarea').forEach(input => {
      if (input.placeholder) {
        this.addFloatingLabel(input);
      }
    });

    // Form validation
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', this.validateForm);
    });
  }

  // Add floating label effect
  addFloatingLabel(input) {
    const wrapper = document.createElement('div');
    wrapper.className = 'relative';
    
    const label = document.createElement('label');
    label.textContent = input.placeholder;
    label.className = 'absolute left-4 top-3 text-gray-500 transition-all duration-200 pointer-events-none';
    
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);
    wrapper.appendChild(label);
    
    input.placeholder = '';
    
    const updateLabel = () => {
      if (input.value || input === document.activeElement) {
        label.classList.add('-top-2', 'left-2', 'text-xs', 'bg-white', 'px-2', 'text-blue-600');
        label.classList.remove('top-3', 'left-4', 'text-gray-500');
      } else {
        label.classList.remove('-top-2', 'left-2', 'text-xs', 'bg-white', 'px-2', 'text-blue-600');
        label.classList.add('top-3', 'left-4', 'text-gray-500');
      }
    };
    
    input.addEventListener('focus', updateLabel);
    input.addEventListener('blur', updateLabel);
    input.addEventListener('input', updateLabel);
  }

  // Form validation
  validateForm(e) {
    const form = e.currentTarget;
    const inputs = form.querySelectorAll('input[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
      if (!input.value.trim()) {
        input.classList.add('border-red-500', 'ring-red-200');
        input.classList.remove('border-gray-300');
        isValid = false;
      } else {
        input.classList.remove('border-red-500', 'ring-red-200');
        input.classList.add('border-gray-300');
      }
    });
    
    if (!isValid) {
      e.preventDefault();
    }
  }

  // Initialize modals
  initModals() {
    document.querySelectorAll('[data-modal-open]').forEach(trigger => {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        const modalId = trigger.dataset.modalOpen;
        const modal = document.getElementById(modalId);
        if (modal) {
          modal.classList.remove('hidden');
          modal.classList.add('flex');
          document.body.style.overflow = 'hidden';
        }
      });
    });

    document.querySelectorAll('[data-modal-close]').forEach(trigger => {
      trigger.addEventListener('click', () => {
        const modal = trigger.closest('.modal');
        if (modal) {
          modal.classList.add('hidden');
          modal.classList.remove('flex');
          document.body.style.overflow = '';
        }
      });
    });
  }
}

// Initialize Lucide icons
function initIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new PremiumDesign();
  initIcons();
});

// Ripple animation keyframes
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
  @keyframes ripple {
    to {
      transform: scale(4);
      opacity: 0;
    }
  }
`;
document.head.appendChild(rippleStyle);

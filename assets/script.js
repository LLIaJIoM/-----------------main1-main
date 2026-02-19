document.addEventListener('DOMContentLoaded', () => {

  let isLite = false;
  try {
    const qs = new URLSearchParams(location.search);
    isLite = qs.get('lite') === '1';
  } catch (e) {}
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);

  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (navToggle && nav) {
    const setExpanded = value => {
      navToggle.setAttribute('aria-expanded', value ? 'true' : 'false');
    };
    setExpanded(false);
    navToggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      navToggle.classList.toggle('open', open);
      setExpanded(open);
    });
    nav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => {
        nav.classList.remove('open');
        navToggle.classList.remove('open');
        setExpanded(false);
      });
    });
  }

  const navLinks = document.querySelectorAll('a[href^="#"]');
  const navMenuLinks = document.querySelectorAll('.nav a[href^="#"]');
  const navLinkMap = new Map();
  navMenuLinks.forEach(a => {
    const id = a.getAttribute('href').slice(1);
    if (id) navLinkMap.set(id, a);
  });
  const phoneLink = document.querySelector('.phone-link');
  if (phoneLink) {
    phoneLink.addEventListener('click', () => {
      try {
        const url = new URL(window.location.href);
        url.searchParams.set('phone_call', '1');
        window.history.replaceState(null, '', url.toString());
      } catch (e) {}
    });
  }
  navLinks.forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) {
        history.pushState(null, null, '#' + id);
        
        const header = document.querySelector('.site-header');
        const headerHeight = header ? header.offsetHeight : 0;
        let elementPosition = el.getBoundingClientRect().top + window.scrollY;

        const buffer = id === 'feedback' ? -30 : 20;
        const offsetPosition = elementPosition - headerHeight - buffer;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  const items = document.querySelectorAll('.accordion-item');
  items.forEach((item, idx) => {
    const btn = item.querySelector('.accordion-btn');
    const content = item.querySelector('.accordion-content');
    if (btn && content) {
      const id = `faq-panel-${idx + 1}`;
      content.id = id;
      btn.setAttribute('aria-controls', id);
      btn.setAttribute('aria-expanded', 'false');
      content.setAttribute('aria-hidden', 'true');
    }
    if (btn) {
      btn.addEventListener('click', () => {
        const open = item.classList.contains('open');
        items.forEach(i => {
          i.classList.remove('open');
          const b = i.querySelector('.accordion-btn');
          const c = i.querySelector('.accordion-content');
          if (b) b.setAttribute('aria-expanded', 'false');
          if (c) c.setAttribute('aria-hidden', 'true');
        });
        if (!open) {
          item.classList.add('open');
          if (btn) btn.setAttribute('aria-expanded', 'true');
          if (content) content.setAttribute('aria-hidden', 'false');
        }
      });
    }
  });

  const track = document.querySelector('.carousel-track');
  const btnPrev = document.querySelector('.carousel-btn.prev');
  const btnNext = document.querySelector('.carousel-btn.next');
  if (track && btnPrev && btnNext && !isLite) {
    const sources = [];
    const dotsContainer = document.querySelector('.carousel-dots');
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    const inner = document.createElement('div');
    inner.className = 'lightbox-inner';
    const fullImg = document.createElement('img');
    inner.appendChild(fullImg);
    lightbox.appendChild(inner);
    document.body.appendChild(lightbox);
    const openLightbox = src => {
      fullImg.src = src;
      lightbox.classList.add('open');
      document.body.classList.add('modal-open');
    };
    const closeLightbox = () => {
      lightbox.classList.remove('open');
      document.body.classList.remove('modal-open');
    };
    lightbox.addEventListener('click', closeLightbox);
    inner.addEventListener('click', e => e.stopPropagation());
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeLightbox();
    });
    const fallbackPhotos = [
      "assets/portfolio/photo_10_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_12_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_14_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_18_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_21_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_24_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_31_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_40_2026-02-04_20-15-16.jpg"
    ];
    const shuffle = (array) => {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    };
    const getPortfolioList = async () => {
      try {
        const res = await fetch('assets/portfolio/index.json', { cache: 'no-store' });
        if (!res.ok) return fallbackPhotos;
        const data = await res.json();
        if (!Array.isArray(data) || !data.length) return fallbackPhotos;
        return data.map(name => `assets/portfolio/${name}`);
      } catch (e) {
        return fallbackPhotos;
      }
    };
    const buildCarousel = (allPhotos) => {
      const uniqueMap = new Map();
      allPhotos.forEach(src => {
        const match = src.match(/\/photo_(\d+)_/);
        if (match) {
          uniqueMap.set(match[1], src);
        } else {
          uniqueMap.set(src, src);
        }
      });
      const uniquePhotos = Array.from(uniqueMap.values());
      const list = shuffle([...uniquePhotos]);
      if (!list.length) return;
      list.forEach(src => sources.push(src));
      const repeated = sources.concat(sources).concat(sources);
      repeated.forEach(src => {
        const slide = document.createElement('div');
        slide.className = 'carousel-slide';
        slide.style.backgroundImage = `url('${src}')`;
        slide.addEventListener('click', () => openLightbox(src));
        track.appendChild(slide);
      });
      let index = sources.length + Math.floor(Math.random() * sources.length);
      const block = sources.length;
      const createDots = () => {
        if (!dotsContainer) return;
        dotsContainer.innerHTML = '';
        for (let i = 0; i < block; i++) {
          const dot = document.createElement('button');
          dot.type = 'button';
          dot.className = 'carousel-dot';
          dot.setAttribute('aria-label', `Слайд ${i + 1}`);
          dot.addEventListener('click', () => {
            index = block + i;
            update();
          });
          dotsContainer.appendChild(dot);
        }
      };
      const setActiveDot = () => {
        if (!dotsContainer) return;
        const active = ((index % block) + block) % block;
        dotsContainer.querySelectorAll('.carousel-dot').forEach((dot, i) => {
          const isActive = i === active;
          dot.classList.toggle('active', isActive);
          dot.setAttribute('aria-current', isActive ? 'true' : 'false');
        });
      };
      const update = () => {
        track.style.transform = `translateX(-${index * 100}%)`;
        setActiveDot();
      };
      const fixLoop = () => {
        if (index >= block * 2) {
          index -= block;
          const prev = track.style.transition;
          track.style.transition = 'none';
          track.style.transform = `translateX(-${index * 100}%)`;
          void track.offsetHeight;
          track.style.transition = prev || 'transform .45s ease';
        } else if (index < block) {
          index += block;
          const prev = track.style.transition;
          track.style.transition = 'none';
          track.style.transform = `translateX(-${index * 100}%)`;
          void track.offsetHeight;
          track.style.transition = prev || 'transform .45s ease';
        }
        setActiveDot();
      };
      createDots();
      track.addEventListener('transitionend', fixLoop);
      btnPrev.addEventListener('click', () => {
        index -= 1;
        update();
      });
      btnNext.addEventListener('click', () => {
        index += 1;
        update();
      });
      window.addEventListener('resize', update);
      let sx = 0, dx = 0;
      track.addEventListener('touchstart', e => { sx = e.touches[0].clientX; dx = 0; }, { passive: true });
      track.addEventListener('touchmove', e => { dx = e.touches[0].clientX - sx; }, { passive: true });
      track.addEventListener('touchend', () => {
        if (Math.abs(dx) > 40) {
          if (dx < 0) btnNext.click(); else btnPrev.click();
        }
      });
      update();
    };
    const initCarousel = async () => {
      const allPhotos = await getPortfolioList();
      buildCarousel(allPhotos);
    };
    initCarousel();
  }

  const form = document.getElementById('feedback-form');
  const msg = document.getElementById('form-msg');
  const phoneInput = document.getElementById('phone');
  const nameInput = document.getElementById('name');
  const commentInput = document.getElementById('comment');

  // Disable default HTML5 validation to control the order and UI manually
  if (form) form.setAttribute('novalidate', 'true');

  // Initialize Intl Tel Input с кастомным плейсхолдером и маской для РФ (кроме lite-режима)
  let iti = null;
  if (!isLite && window.intlTelInput && phoneInput) {
    iti = window.intlTelInput(phoneInput, {
      initialCountry: "ru",
      separateDialCode: true,
      autoPlaceholder: "aggressive",
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.2.1/js/utils.js",
      customPlaceholder: function (placeholder, data) {
        if (data && data.iso2 === 'ru') {
          return "(999) 999-99-99";
        }
        return placeholder;
      }
    });

    const applyMask = () => {
      const data = iti.getSelectedCountryData() || {};
      
      // Russia: Custom mask
      if (data.dialCode === '7' && data.iso2 === 'ru') {
        let raw = phoneInput.value.replace(/\D/g, '');
        if (!raw) {
          phoneInput.value = '';
          return;
        }
        if (raw[0] === '8' || raw[0] === '7') {
          raw = raw.slice(1);
        }
        const mask = "(999) 999-99-99";
        let res = "";
        let di = 0;
        for (let i = 0; i < mask.length; i++) {
          const ch = mask[i];
          if (ch === '9') {
            if (di < raw.length) {
              res += raw[di++];
            } else {
              break;
            }
          } else {
            if (!di && (ch === ' ' || ch === '-')) continue;
            res += ch;
          }
        }
        phoneInput.value = res;
      } else {
        // Other countries: Strict mask based on placeholder
        // User wants digits to be entered "according to the placeholder"
        const placeholder = phoneInput.getAttribute('placeholder') || '';
        
        // Check if placeholder looks like a mask (contains digits)
        if (placeholder && /\d/.test(placeholder)) {
             let raw = phoneInput.value.replace(/\D/g, '');
             let res = "";
             let digitIdx = 0;
             
             for (let i = 0; i < placeholder.length; i++) {
                 const ch = placeholder[i];
                 if (/\d/.test(ch)) {
                     // Digit slot
                     if (digitIdx < raw.length) {
                         res += raw[digitIdx++];
                     } else {
                         break; // No more digits to fill
                     }
                 } else {
                     // Separator (space, bracket, dash, etc.)
                     // Only show separator if we have digits following it (or we are in the middle of typing)
                     // To avoid "stuck" separators on backspace, we only show if followed by a digit.
                     if (digitIdx < raw.length) {
                         res += ch;
                     } else {
                         // Trailing separator? Stop here.
                         break;
                     }
                 }
             }
             phoneInput.value = res;
        } else {
             // Fallback for countries with no digit-placeholder: just limit length
             const maxDigits = 15;
             let val = phoneInput.value.replace(/\D/g, '');
             if (val.length > maxDigits) val = val.slice(0, maxDigits);
             if (phoneInput.value.replace(/\D/g, '') !== val) {
                 phoneInput.value = val; 
             }
        }
      }
    };

    phoneInput.addEventListener('input', applyMask);
    // When country changes, clear value and let placeholder update
    phoneInput.addEventListener('countrychange', () => {
      phoneInput.value = '';
      if (iti) iti.setNumber('');
      if (msg) {
        msg.textContent = '';
        msg.style.color = 'inherit';
      }
      // Re-apply mask to update logic if needed (though value is empty)
      // We rely on 'input' event mainly, but clearing value is safe.
    });
  }

  const resetMsg = () => {
    msg.textContent = '';
    msg.style.color = 'inherit';
    if (nameInput) nameInput.style.borderColor = '';
    if (phoneInput) phoneInput.style.borderColor = '';
    if (commentInput) commentInput.style.borderColor = '';
    // Fix intl-tel-input container border if needed, usually it wraps input
    if (phoneInput) {
        const itiContainer = phoneInput.closest('.iti');
        if (itiContainer) itiContainer.style.borderColor = '';
    }
  };

  const showError = (el, message) => {
    msg.textContent = message;
    msg.style.color = 'crimson';
    if (el) {
        el.style.borderColor = 'crimson';
        if (el === phoneInput) {
            const itiContainer = phoneInput.closest('.iti');
            if (itiContainer) itiContainer.style.borderColor = 'crimson';
        }
        if (!isIOS) {
          el.focus();
        } else {
          const active = document.activeElement;
          if (active && active !== document.body) active.blur();
        }
    }
  };

  if (form) {
      [nameInput, phoneInput, commentInput].forEach(el => {
        if (!el) return;
        el.addEventListener('input', () => {
          if (el === nameInput) {
              const v = el.value;
              const cleaned = v.replace(/[^A-Za-zА-Яа-яЁё\s-]/g, '');
              if (v !== cleaned) el.value = cleaned;
          }
          // Clear error style on input
          el.style.borderColor = '';
          if (el === phoneInput) {
              const itiContainer = phoneInput.closest('.iti');
              if (itiContainer) itiContainer.style.borderColor = '';
          }
          // If the current error message is related to this field, clear it
          if (msg.style.color === 'crimson') {
              msg.textContent = '';
          }
          
          // Real-time length check for comment
          if (el === commentInput) {
              if (el.value.length >= 1000) {
                  msg.textContent = 'Превышен допустимый лимит: больше 1000 символов нельзя.';
                  msg.style.color = 'crimson';
              }
          }
        });
      });

      form.addEventListener('submit', e => {
        e.preventDefault();
        resetMsg();

        const name = nameInput.value.trim();
        const commentVal = commentInput.value.trim();
        
        // 1. Validate Name
        if (!name) {
          showError(nameInput, 'Введите имя.');
          return;
        }
        if (!/^[A-Za-zА-Яа-яЁё\s-]+$/.test(name)) {
          showError(nameInput, 'Имя должно содержать только буквы.');
          return;
        }
        if (name.length > 50) {
          showError(nameInput, 'Имя слишком длинное (макс. 50 символов).');
          return;
        }

        // 2. Validate Phone
        const rawPhone = phoneInput.value.trim();
        if (!rawPhone) {
          showError(phoneInput, 'Введите номер телефона.');
          return;
        }

        let phoneFull = rawPhone;
        if (iti) {
          if (!iti.isValidNumber()) {
            const errorCode = iti.getValidationError();
            let errorMsg = 'Введите корректный номер телефона.';
            
            // Map error codes
            // 0: IS_POSSIBLE (shouldn't happen if invalid)
            // 1: INVALID_COUNTRY_CODE
            // 2: TOO_SHORT
            // 3: TOO_LONG
            // 4: IS_POSSIBLE_LOCAL_ONLY
            // 5: INVALID_LENGTH
            if (errorCode === 1) errorMsg = 'Неверный код страны.';
            if (errorCode === 2) errorMsg = 'Номер слишком короткий.';
            if (errorCode === 3) errorMsg = 'Номер слишком длинный.';
            // For general invalid number (e.g. invalid area code 444 in RU)
            if (errorCode === 0 || errorCode === 4 || errorCode === -99) errorMsg = 'Некорректный номер (проверьте код оператора).';

            showError(phoneInput, errorMsg);
            return;
          }
          phoneFull = iti.getNumber();
        } else {
          const digits = rawPhone.replace(/\D/g, '');
          if (digits.length < 7 || digits.length > 15) {
            showError(phoneInput, 'Введите корректный номер телефона.');
            return;
          }
        }

        // 3. Validate Comment
        if (commentVal.length > 1000) {
          showError(commentInput, 'Комментарий слишком длинный (макс. 1000 символов).');
          return;
        }

        // Submit
        const btn = form.querySelector('button[value="telegram"]'); // Default loading indicator on telegram button
        
        // Determine Action
        const submitter = e.submitter;
        const action = submitter ? submitter.value : 'telegram'; // default to telegram if enter pressed

        // WhatsApp Action
        if (action === 'whatsapp') {
          const waPhone = '79296783656'; 
          const waText = `Здравствуйте! Оставляю заявку с сайта.\nИмя: ${name}\nТелефон: ${phoneFull}\nКомментарий: ${commentVal}`;
          // Use custom protocol to avoid opening a web page/tab. 
          // If installed: opens app. If not: stays on page (Telegram still sent).
          const waUrl = `whatsapp://send?phone=${waPhone}&text=${encodeURIComponent(waText)}`;
          
          // 1. Send notification to Telegram (using keepalive to ensure it sends even if page unloads)
          const waPayload = {
            name,
            phone: phoneFull,
            comment: commentVal,
            page: location.href,
            source: 'WhatsApp'
          };
          if (iti) {
            const cd = iti.getSelectedCountryData() || {};
            waPayload.phone_country = cd.name || '';
            waPayload.phone_iso2 = cd.iso2 || '';
            waPayload.phone_dial_code = cd.dialCode || '';
          }
          fetch('/api/telegram', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            keepalive: true,
            body: JSON.stringify(waPayload)
          }).catch(() => {}); 

          // 2. UI Updates: Clear form and show success message
          msg.textContent = 'Заявка отправлена. Мы свяжемся с вами.';
          msg.style.color = 'seagreen';
          form.reset();
          if (iti) iti.setNumber('');

          // 3. Open WhatsApp in current tab (avoids new empty tab)
          window.location.href = waUrl;
          
          return; 
        }

        // Telegram Action
        if (btn) { btn.disabled = true; btn.style.opacity = '.7'; }
        msg.textContent = 'Отправка...';
        msg.style.color = 'inherit';
        
        const payload = {
          name,
          phone: phoneFull,
          comment: commentVal,
          page: location.href
        };
        if (iti) {
          const cd = iti.getSelectedCountryData() || {};
          payload.phone_country = cd.name || '';
          payload.phone_iso2 = cd.iso2 || '';
          payload.phone_dial_code = cd.dialCode || '';
        }
        
        fetch('/api/telegram', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }).then(async r => {
          const ok = r.ok;
          let data = {};
          try { data = await r.json(); } catch {}
          if (ok && data.ok) {
            msg.textContent = 'Заявка отправлена. Мы свяжемся с вами.';
            msg.style.color = 'seagreen';
            form.reset();
            if (iti) iti.setNumber(''); // Reset flags/input
          } else {
            msg.textContent = 'Не удалось отправить. Попробуйте позже.';
            msg.style.color = 'crimson';
          }
        }).catch(() => {
           msg.textContent = 'Ошибка сети. Повторите позже.';
           msg.style.color = 'crimson';
        }).finally(() => {
          if (btn) { btn.disabled = false; btn.style.opacity = '1'; }
        });
      });
  }

  try {
    const qs = new URLSearchParams(location.search);
    if (qs.get('autotest') === '1' && form) {
      form.name.value = form.name.value || 'Тест';
      if (iti) iti.setNumber('+79990000000');
      else form.phone.value = '+79990000000';
      form.comment.value = form.comment.value || 'Автотест';
      setTimeout(() => {
          form.dispatchEvent(new Event('submit', { cancelable: true }));
      }, 500);
    }
  } catch (e) {}

  // ScrollSpy: Update URL hash when scrolling through sections
  const spyObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        if (id) {
          // Use replaceState to update URL without adding to history stack
          history.replaceState(null, null, '#' + id);
          navMenuLinks.forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
          });
          const activeLink = navLinkMap.get(id);
          if (activeLink) {
            activeLink.classList.add('active');
            activeLink.setAttribute('aria-current', 'page');
          }
        }
      }
    });
  }, {
    root: null,
    rootMargin: '-50% 0px -50% 0px', // Active when section is in the middle of viewport
    threshold: 0
  });

  document.querySelectorAll('section[id]').forEach(section => {
    spyObserver.observe(section);
  });

  // Back to Top Logic
  const backToTopBtn = document.getElementById('backToTop');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        backToTopBtn.classList.add('show');
      } else {
        backToTopBtn.classList.remove('show');
      }
    });
    backToTopBtn.addEventListener('click', () => {
      const active = document.activeElement;
      if (active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.isContentEditable)) {
        active.blur();
      }
      const aboutSection = document.getElementById('about');
      if (aboutSection) {
        const header = document.querySelector('.site-header');
        const headerHeight = header ? header.offsetHeight : 0;
        const elementPosition = aboutSection.getBoundingClientRect().top + window.scrollY;
        const offsetPosition = elementPosition - headerHeight - 20;
        const behavior = isIOS ? 'auto' : 'smooth';

        window.scrollTo({
          top: offsetPosition,
          behavior
        });
        if (isIOS) {
          requestAnimationFrame(() => {
            window.scrollTo({ top: offsetPosition, behavior: 'auto' });
          });
        }

        history.pushState(null, null, '#about');
      } else {
        window.scrollTo({ top: 0, behavior: isIOS ? 'auto' : 'smooth' });
      }
    });
  }

  // Scroll Animations (Intersection Observer)
  const observerOptions = {
    threshold: 0.1
  };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target); // Animate only once
      }
    });
  }, observerOptions);

  // Add fade-up class to sections and other major elements
  const animatedElements = document.querySelectorAll('.section, .card, .service, .feature, .wide-image, .carousel');
  animatedElements.forEach(el => {
    el.classList.add('fade-up');
    observer.observe(el);
  });
});

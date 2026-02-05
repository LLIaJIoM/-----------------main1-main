document.addEventListener('DOMContentLoaded', () => {

  const navToggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  if (navToggle && nav) {
    navToggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
    nav.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => nav.classList.remove('open'));
    });
  }

  const navLinks = document.querySelectorAll('.nav a[href^="#"]');
  navLinks.forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      const id = a.getAttribute('href').slice(1);
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  const heroEl = document.querySelector('.wide-image');
  if (heroEl) {
    const test = new Image();
    test.onload = () => {
      heroEl.style.background = 'none';
      heroEl.style.height = 'auto';
      const img = test;
      img.style.width = '100%';
      img.style.height = 'auto';
      img.style.display = 'block';
      heroEl.appendChild(img);
    };
    test.onerror = () => {};
    test.src = 'assets/hero.jpg';
  }

  const items = document.querySelectorAll('.accordion-item');
  items.forEach(item => {
    const btn = item.querySelector('.accordion-btn');
    btn.addEventListener('click', () => {
      const open = item.classList.contains('open');
      items.forEach(i => i.classList.remove('open'));
      if (!open) item.classList.add('open');
    });
  });

  const track = document.querySelector('.carousel-track');
  const btnPrev = document.querySelector('.carousel-btn.prev');
  const btnNext = document.querySelector('.carousel-btn.next');
  if (track && btnPrev && btnNext) {
    const exts = ['jpg','jpeg','png','webp'];
    const max = 200;
    const sources = [];
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
    const probe = src => new Promise(res => {
      const img = new Image();
      img.onload = () => res(true);
      img.onerror = () => res(false);
      img.src = src;
    });
    (async () => {
      let list = [];
      try {
        const r = await fetch('assets/portfolio/index.json', { cache: 'no-store' });
        if (r.ok) {
          const arr = await r.json();
          if (Array.isArray(arr) && arr.length) list = arr.map(n => `assets/portfolio/${n}`);
        }
      } catch {}
      if (!list.length) {
        for (let i = 1; i <= max; i++) {
          let found = false;
          for (const ext of exts) {
            const src = `assets/portfolio/${i}.${ext}`;
            if (await probe(src)) { list.push(src); found = true; break; }
          }
          if (!found) continue;
        }
      }
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
      const update = () => {
        track.style.transform = `translateX(-${index * 100}%)`;
      };
      const fixLoop = () => {
        const block = sources.length;
        if (index >= block * 2) {
          index -= block;
          const prev = track.style.transition;
          track.style.transition = 'none';
          track.style.transform = `translateX(-${index * 100}%)`;
          // force reflow
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
      };
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
    })();
  }

  const form = document.getElementById('feedback-form');
  const msg = document.getElementById('form-msg');
  const phoneInput = document.getElementById('phone');
  const nameInput = document.getElementById('name');
  const commentInput = document.getElementById('comment');

  // Disable default HTML5 validation to control the order and UI manually
  if (form) form.setAttribute('novalidate', 'true');

  // Initialize Intl Tel Input
  let iti = null;
  if (window.intlTelInput && phoneInput) {
    iti = window.intlTelInput(phoneInput, {
      initialCountry: "ru",
      separateDialCode: true,
      utilsScript: "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/18.2.1/js/utils.js",
      autoPlaceholder: "aggressive",
      customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
          // Force bracketed format for RU to ensure it starts with brackets immediately
          if (selectedCountryData.iso2 === 'ru') {
              return "(999) 999-99-99";
          }
          return selectedCountryPlaceholder;
      }
    });

    // Helper to format number based on placeholder
    const applyMask = () => {
      // Get current value and placeholder
      let val = phoneInput.value;
      const placeholder = phoneInput.getAttribute('placeholder') || '';
      
      // Special handling for RU/KZ (+7) to strip leading 8
      const countryData = iti.getSelectedCountryData();
      if (countryData.dialCode === '7') {
         if (val.startsWith('8')) {
             val = val.slice(1);
         }
         // For Russia specifically, also strip leading 7 if user types "7..." thinking it's +7
         if (countryData.iso2 === 'ru' && val.startsWith('7')) {
             val = val.slice(1);
         }
      }
      
      // If placeholder contains digits, we can try to mask
      // Simple strategy: strip non-digits from val, and inject them into placeholder template
      // This is a naive implementation but works for simple cases like (XXX) XXX-XX-XX
      
      // However, a safer bet that intl-tel-input users use is to just rely on formatNumber
      // But formatNumber requires full number.
      
      // Let's implement a simple "replace digits in placeholder" mask
      // Only if placeholder looks like a mask (contains digits/spaces/brackets)
      if (placeholder && /[0-9]/.test(placeholder)) {
          let raw = val.replace(/\D/g, '');
          const maxDigits = placeholder.replace(/\D/g, '').length;
          if (maxDigits > 0 && raw.length > maxDigits) {
              raw = raw.slice(0, maxDigits);
          }
          
          let res = '';
          let rawIdx = 0;
          
          for (let i = 0; i < placeholder.length; i++) {
              if (rawIdx >= raw.length) break;
              
              const pChar = placeholder[i];
              // If placeholder char is a digit, replace with next raw digit
              if (/\d/.test(pChar)) {
                  res += raw[rawIdx++];
              } else {
                  // If it's a separator, add it
                  res += pChar;
              }
          }
          
          // If we have extra digits (should not happen due to truncation above, but for safety), append them
          if (rawIdx < raw.length) {
              res += raw.slice(rawIdx);
          }
          
          // Avoid overwriting if user is deleting (this is tricky with just 'input' event)
          // But user asked for "input looks like placeholder"
          if (val !== res) {
              phoneInput.value = res;
          }
      } else {
          // If no placeholder mask available, just apply the strip 8 logic
           if (phoneInput.value !== val) {
              phoneInput.value = val;
           }
      }
    };
    
    phoneInput.addEventListener('input', applyMask);
    // Also re-apply on country change
    phoneInput.addEventListener('countrychange', () => {
        phoneInput.value = '';
        applyMask();
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
        el.focus();
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
        
        // Strict length validation aligned with placeholder
        const placeholder = phoneInput.getAttribute('placeholder') || '';
        const maxDigits = placeholder.replace(/\D/g, '').length;
        const currentDigits = rawPhone.replace(/\D/g, '').length;
        if (maxDigits > 0) {
            if (currentDigits > maxDigits) {
                showError(phoneInput, 'Номер слишком длинный для выбранной страны.');
                return;
            }
            if (currentDigits < maxDigits) {
                showError(phoneInput, `Допишите номер: требуется ${maxDigits} цифр.`);
                return;
            }
        } else {
            // Fallback for rare cases without placeholder digits: use ITI validity or general bounds
            if (iti && !iti.isValidNumber()) {
                showError(phoneInput, 'Введите корректный номер телефона.');
                return;
            }
            if (currentDigits < 7 || currentDigits > 15) {
                showError(phoneInput, 'Введите корректный номер телефона.');
                return;
            }
        }
        
        const phoneFull = iti ? iti.getNumber() : rawPhone;

        // 3. Validate Comment
        if (commentVal.length > 1000) {
          showError(commentInput, 'Комментарий слишком длинный (макс. 1000 символов).');
          return;
        }

        // Submit
        const btn = form.querySelector('button[type="submit"]');
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
  } catch {}
});

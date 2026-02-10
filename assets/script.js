document.addEventListener('DOMContentLoaded', () => {

  let isLite = false;
  try {
    const qs = new URLSearchParams(location.search);
    isLite = qs.get('lite') === '1';
  } catch (e) {}

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
      if (el) {
        history.pushState(null, null, '#' + id);
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  const heroEl = document.querySelector('.wide-image');
  if (heroEl && !isLite) {
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
  if (track && btnPrev && btnNext && !isLite) {
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
    const allPhotos = [
      "assets/portfolio/photo_10_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_10_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_11_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_11_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_12_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_12_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_13_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_13_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_14_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_14_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_15_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_15_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_16_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_16_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_17_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_17_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_18_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_18_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_19_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_19_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_1_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_1_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_20_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_20_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_21_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_21_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_22_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_22_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_23_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_23_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_24_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_24_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_25_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_25_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_26_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_26_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_27_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_27_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_28_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_28_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_29_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_2_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_2_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_30_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_30_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_31_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_31_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_32_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_32_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_33_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_33_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_34_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_34_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_35_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_35_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_36_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_37_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_38_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_39_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_3_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_3_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_40_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_41_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_42_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_43_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_44_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_45_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_46_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_47_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_48_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_49_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_4_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_4_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_50_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_51_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_52_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_53_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_54_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_55_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_56_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_57_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_58_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_59_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_5_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_5_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_60_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_61_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_62_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_63_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_64_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_65_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_66_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_67_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_68_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_69_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_6_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_6_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_70_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_71_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_72_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_73_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_74_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_75_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_76_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_7_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_7_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_8_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_8_2026-02-04_20-15-16.jpg",
      "assets/portfolio/photo_9_2026-02-04_20-03-53.jpg",
      "assets/portfolio/photo_9_2026-02-04_20-15-16.jpg"
    ];
    const shuffle = (array) => {
      for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
      }
      return array;
    };
    // Use all photos, but shuffled to avoid repetition patterns
    const list = shuffle([...allPhotos]);
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
        // Other countries: Dynamic mask based on placeholder
        const placeholder = phoneInput.getAttribute('placeholder') || '';
        
        // If no placeholder or no digits in it, fallback to generic limit
        if (!placeholder || !/\d/.test(placeholder)) {
           let val = phoneInput.value;
           const dialCodeLen = data.dialCode ? data.dialCode.length : 0;
           const maxNationalDigits = 15 - dialCodeLen;
           while (val.replace(/\D/g, '').length > maxNationalDigits) {
             val = val.slice(0, -1);
           }
           if (phoneInput.value !== val) phoneInput.value = val;
           return;
        }

        let raw = phoneInput.value.replace(/\D/g, '');
        let res = "";
        let di = 0;

        for (let i = 0; i < placeholder.length; i++) {
          const ch = placeholder[i];
          if (/\d/.test(ch)) {
            // Treat any digit in placeholder as a slot
            if (di < raw.length) {
              res += raw[di++];
            } else {
              break;
            }
          } else {
            // Separator (space, bracket, dash, etc.)
            // Append only if we haven't finished entering numbers yet
            // (Similar to Russia logic: show separators that come before the next digit)
            // But if we are at the very end of raw, we might stop?
            // Actually, the loop breaks at the *next* digit check if exhausted.
            // So separators between digits are preserved.
            // Separators after the last digit are preserved ONLY if there is a digit after them that we haven't reached?
            // No, if we break at the next digit, we won't reach subsequent separators.
            // So this works: separators strictly *between* or *before* entered digits are shown.
            res += ch;
          }
        }
        phoneInput.value = res;
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

        let phoneFull = rawPhone;
        if (iti) {
          const data = iti.getSelectedCountryData() || {};
          const digitsNational = rawPhone.replace(/\D/g, '');
          if (data.dialCode === '7' && data.iso2 === 'ru') {
            if (digitsNational.length < 10) {
              showError(phoneInput, 'Допишите номер: требуется 10 цифр после +7.');
              return;
            }
            if (digitsNational.length > 10) {
              showError(phoneInput, 'Номер слишком длинный.');
              return;
            }
          } else {
            if (digitsNational.length < 7 || digitsNational.length > 15) {
              showError(phoneInput, 'Введите корректный номер телефона.');
              return;
            }
          }
          phoneFull = iti.getNumber() || '';
          if (!phoneFull) {
            showError(phoneInput, 'Введите корректный номер телефона.');
            return;
          }
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
  } catch (e) {}

  // ScrollSpy: Update URL hash when scrolling through sections
  const spyObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        if (id) {
          // Use replaceState to update URL without adding to history stack
          history.replaceState(null, null, '#' + id);
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
});

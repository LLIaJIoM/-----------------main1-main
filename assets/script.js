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
      list.forEach(src => {
        const slide = document.createElement('div');
        slide.className = 'carousel-slide';
        slide.style.backgroundImage = `url('${src}')`;
        slide.addEventListener('click', () => openLightbox(src));
        track.appendChild(slide);
        sources.push(src);
      });
      let index = Math.floor(Math.random() * sources.length);
      const update = () => {
        track.style.transform = `translateX(-${index * 100}%)`;
      };
      btnPrev.addEventListener('click', () => {
        index = (index - 1 + sources.length) % sources.length;
        update();
      });
      btnNext.addEventListener('click', () => {
        index = (index + 1) % sources.length;
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

  const normalizePhone = raw => {
    const digits = (raw || '').replace(/\D+/g, '');
    let d = digits;
    if (!d) return null;
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (d[0] !== '7') d = '7' + d.slice(0, 10);
    if (d.length > 11) d = d.slice(0, 11);
    if (d.length === 11 && d[0] === '7') return '+' + d;
    return null;
  };
  const formatMask = raw => {
    const digits = (raw || '').replace(/\D+/g, '');
    let d = digits;
    if (!d) return '';
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (d[0] !== '7') d = '7' + d;
    if (d.length > 11) d = d.slice(0, 11);
    const a = d.slice(1, 4);
    const b = d.slice(4, 7);
    const c = d.slice(7, 9);
    const e = d.slice(9, 11);
    let out = '+7';
    if (a) out += ' (' + a;
    if (a && a.length === 3) out += ')';
    if (b) out += ' ' + b;
    if (c) out += '-' + c;
    if (e) out += '-' + e;
    return out;
  };
  phoneInput.addEventListener('input', () => {
    phoneInput.value = formatMask(phoneInput.value);
  });
  phoneInput.addEventListener('invalid', () => {
    phoneInput.setCustomValidity('Введите номер телефона в формате +7 (XXX) XXX-XX-XX.');
    msg.textContent = 'Введите номер телефона в формате +7 (XXX) XXX-XX-XX.';
    msg.style.color = 'crimson';
  });
  phoneInput.addEventListener('input', () => {
    phoneInput.setCustomValidity('');
  });
  nameInput.addEventListener('invalid', () => {
    const v = nameInput.value.trim();
    let m = '';
    if (!v) m = 'Введите имя.';
    else if (v.length > 50) m = 'Имя слишком длинное (макс. 50 символов).';
    else m = 'Введите ваше имя.';
    nameInput.setCustomValidity(m);
    msg.textContent = m;
    msg.style.color = 'crimson';
  });
  nameInput.addEventListener('input', () => {
    nameInput.setCustomValidity('');
  });
  commentInput.addEventListener('invalid', () => {
    const v = commentInput.value.trim();
    let m = '';
    if (v.length > 1000) m = 'Комментарий слишком длинный (макс. 1000 символов).';
    else m = 'Можно написать до 1000 символов.';
    commentInput.setCustomValidity(m);
    msg.textContent = m;
    msg.style.color = 'crimson';
  });
  commentInput.addEventListener('input', () => {
    commentInput.setCustomValidity('');
    const v = commentInput.value;
    if (v.length >= 1000) {
      msg.textContent = 'Превышен допустимый лимит: больше 1000 символов нельзя.';
      msg.style.color = 'crimson';
    } else {
      if (msg.textContent.startsWith('Комментарий')) msg.textContent = '';
    }
  });
  commentInput.addEventListener('beforeinput', e => {
    const inserting = e.inputType && e.inputType.startsWith('insert');
    if (inserting && commentInput.value.length >= 1000) {
      msg.textContent = 'Превышен допустимый лимит: больше 1000 символов нельзя.';
      msg.style.color = 'crimson';
    }
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    const name = form.name.value.trim();
    const phone = form.phone.value.trim();
    const normalized = normalizePhone(phone);
    if (name.length > 50) {
      msg.textContent = 'Имя слишком длинное (макс. 50 символов).';
      msg.style.color = 'crimson';
      return;
    }
    const commentVal = form.comment.value.trim();
    if (commentVal.length > 1000) {
      msg.textContent = 'Комментарий слишком длинный (макс. 1000 символов).';
      msg.style.color = 'crimson';
      return;
    }
    if (!name || !phone) {
      msg.textContent = 'Заполните имя и телефон.';
      msg.style.color = 'crimson';
      return;
    }
    if (!normalized) {
      msg.textContent = 'Введите номер в формате +7 (XXX) XXX-XX-XX.';
      msg.style.color = 'crimson';
      return;
    }
    const btn = form.querySelector('button[type="submit"]');
    if (btn) { btn.disabled = true; btn.style.opacity = '.7'; }
    msg.textContent = 'Отправка...';
    msg.style.color = 'inherit';
    const payload = {
      name,
      phone: normalized,
      comment: commentVal,
      page: location.href
    };
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

  try {
    const qs = new URLSearchParams(location.search);
    if (qs.get('autotest') === '1' && form) {
      form.name.value = form.name.value || 'Тест';
      form.phone.value = form.phone.value || '+79990000000';
      form.comment.value = form.comment.value || 'Автотест';
      form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  } catch {}
});

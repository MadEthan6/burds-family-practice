// Burds Family Practice - progressive enhancements (site remains 100% usable without JS).
(function () {
  // 1. Mobile navigation toggle + outside click / Escape dismissal
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    function setNav(open) {
      toggle.setAttribute('aria-expanded', String(open));
      nav.classList.toggle('is-open', open);
      // Lock page scroll behind the open menu on phones
      document.documentElement.classList.toggle('nav-open', open);
    }
    function closeNav() { setNav(false); }
    toggle.addEventListener('click', function () {
      setNav(toggle.getAttribute('aria-expanded') !== 'true');
    });
    // Tapping a menu link (including same-page #anchors) closes the menu
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });
    // Close the menu if the screen grows to desktop width
    window.addEventListener('resize', function () {
      if (window.innerWidth > 1220 && nav.classList.contains('is-open')) closeNav();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) {
        closeNav();
        toggle.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (nav.classList.contains('is-open') && !nav.contains(e.target) && !toggle.contains(e.target)) {
        closeNav();
      }
    });
  }

  // 2. Office hours in Central time: [openHour, closeHour] per weekday (0 = Sunday)
  var HOURS = { 0: null, 1: [8, 17], 2: [8, 17], 3: [8, 17], 4: [8, 18], 5: [8, 12], 6: null };
  var DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

  function centralNow() {
    try {
      var parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/Chicago', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
      }).formatToParts(new Date());
      var map = {};
      parts.forEach(function (p) { map[p.type] = p.value; });
      var day = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(map.weekday);
      return { day: day, hour: (parseInt(map.hour, 10) % 24) + parseInt(map.minute, 10) / 60 };
    } catch (e) {
      var d = new Date();
      return { day: d.getDay(), hour: d.getHours() + d.getMinutes() / 60 };
    }
  }

  function fmtHour(h) {
    var suffix = h >= 12 ? 'pm' : 'am';
    var hr = h % 12 === 0 ? 12 : h % 12;
    return hr + ' ' + suffix;
  }

  function nextOpening(day) {
    for (var i = 1; i <= 7; i++) {
      var d = (day + i) % 7;
      if (HOURS[d]) return (i === 1 ? 'tomorrow' : DAY_NAMES[d]) + ' at ' + fmtHour(HOURS[d][0]);
    }
    return '';
  }

  var now = centralNow();
  var today = HOURS[now.day];
  var isOpen = !!(today && now.hour >= today[0] && now.hour < today[1]);
  var statusText;
  if (isOpen) {
    statusText = 'Open now · until ' + fmtHour(today[1]) + ' today';
  } else if (today && now.hour < today[0]) {
    statusText = 'Closed now · opens today at ' + fmtHour(today[0]);
  } else {
    statusText = 'Closed now · opens ' + nextOpening(now.day);
  }
  document.querySelectorAll('[data-open-status]').forEach(function (status) {
    status.innerHTML = '<span class="dot" aria-hidden="true"></span>' + statusText;
    status.classList.toggle('is-open', isOpen);
  });

  document.querySelectorAll('.hours tr[data-days]').forEach(function (row) {
    var days = row.getAttribute('data-days').split(',').map(Number);
    if (days.indexOf(now.day) !== -1) row.classList.add('is-today');
  });

  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // 3. Interactive DPC Household Cost Estimator
  document.querySelectorAll('[data-dpc-calc]').forEach(function (calc) {
    var state = { adults: 1, spouse: true, kids: 2, visits: 8 };
    var adultsOut = calc.querySelector('[data-dpc-val="adults"]');
    var kidsOut = calc.querySelector('[data-dpc-val="kids"]');
    var spouseCb = calc.querySelector('[data-dpc-spouse]');
    var visitsInput = calc.querySelector('[data-dpc-visits]');
    var visitsOut = calc.querySelector('[data-dpc-visits-val]');
    var totalOut = calc.querySelector('[data-dpc-monthly]');
    var annualOut = calc.querySelector('[data-dpc-annual]');
    var breakdownOut = calc.querySelector('[data-dpc-breakdown]');
    var copayOut = calc.querySelector('[data-dpc-copay]');
    var presets = calc.querySelectorAll('[data-preset]');

    function money(n) {
      return '$' + Math.round(n).toLocaleString('en-US');
    }

    function syncPresets() {
      var key = state.adults + ',' + (state.spouse ? 1 : 0) + ',' + state.kids;
      presets.forEach(function (btn) {
        btn.classList.toggle('is-active', btn.getAttribute('data-preset') === key);
      });
    }

    function render() {
      var monthly = state.adults * 99 + (state.spouse ? 79 : 0) + state.kids * 49;
      var annual = monthly * 12;
      var people = state.adults + (state.spouse ? 1 : 0) + state.kids;
      var parts = [state.adults + ' adult' + (state.adults > 1 ? 's' : '') + ' (' + money(state.adults * 99) + ')'];
      if (state.spouse) parts.push('spouse ($79)');
      if (state.kids > 0) parts.push(state.kids + ' child' + (state.kids > 1 ? 'ren' : '') + ' (' + money(state.kids * 49) + ')');

      if (adultsOut) adultsOut.textContent = String(state.adults);
      if (kidsOut) kidsOut.textContent = String(state.kids);
      if (spouseCb) spouseCb.checked = state.spouse;
      if (visitsInput) visitsInput.value = String(state.visits);
      if (visitsOut) visitsOut.textContent = state.visits + ' visits/yr';
      if (totalOut) totalOut.textContent = money(monthly) + '/mo';
      if (annualOut) annualOut.textContent = money(annual) + '/yr for ' + people + (people === 1 ? ' member' : ' household members');
      if (breakdownOut) breakdownOut.textContent = parts.join(' + ') + ' · $0 per-visit copays';
      if (copayOut) {
        copayOut.textContent = 'Whether your household needs 2 visits this year or 20, the price stays ' + money(monthly) + '/mo with no copays and no surprise bills.';
      }
      syncPresets();
    }

    calc.querySelectorAll('[data-dpc-step]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var field = btn.getAttribute('data-dpc-step');
        var delta = parseInt(btn.getAttribute('data-delta'), 10) || 0;
        if (field === 'adults') state.adults = Math.max(1, Math.min(4, state.adults + delta));
        if (field === 'kids') state.kids = Math.max(0, Math.min(8, state.kids + delta));
        render();
      });
    });

    if (spouseCb) {
      spouseCb.addEventListener('change', function () {
        state.spouse = !!spouseCb.checked;
        render();
      });
    }

    if (visitsInput) {
      visitsInput.addEventListener('input', function () {
        state.visits = Math.max(2, Math.min(20, parseInt(visitsInput.value, 10) || 6));
        render();
      });
    }

    presets.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var vals = btn.getAttribute('data-preset').split(',').map(Number);
        state.adults = vals[0] || 1;
        state.spouse = !!vals[1];
        state.kids = vals[2] || 0;
        render();
      });
    });

    render();
  });

  // 4. Resources Live Search & Category Filters
  var resourcePage = document.querySelector('[data-resource-filter]');
  if (resourcePage) {
    var searchInput = resourcePage.querySelector('[data-resource-search]');
    var topicBtns = resourcePage.querySelectorAll('[data-topic-btn]');
    var countEl = resourcePage.querySelector('[data-resource-count]');
    var emptyEl = document.querySelector('[data-resource-empty]');
    var resetBtn = document.querySelector('[data-resource-reset]');
    var sections = document.querySelectorAll('[data-resource-section]');
    var items = Array.prototype.slice.call(document.querySelectorAll('[data-resource-section] li[data-topic]'));
    var activeTopic = 'all';

    function applyFilter() {
      var q = (searchInput ? searchInput.value : '').trim().toLowerCase();
      var visibleTotal = 0;

      sections.forEach(function (sec) {
        var secItems = sec.querySelectorAll('li[data-topic]');
        var secVisible = 0;
        secItems.forEach(function (li) {
          var topic = li.getAttribute('data-topic') || '';
          var matchTopic = activeTopic === 'all' || topic.split(/\s+/).indexOf(activeTopic) !== -1;
          var matchText = !q || li.textContent.toLowerCase().indexOf(q) !== -1;
          var show = matchTopic && matchText;
          li.hidden = !show;
          if (show) {
            secVisible++;
            visibleTotal++;
          }
        });
        sec.hidden = secVisible === 0;
      });

      if (countEl) {
        countEl.textContent = 'Showing ' + visibleTotal + ' of ' + items.length + ' resources';
      }
      if (emptyEl) {
        emptyEl.hidden = visibleTotal !== 0;
      }
    }

    topicBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        activeTopic = btn.getAttribute('data-topic-btn') || 'all';
        topicBtns.forEach(function (b) {
          var active = b === btn;
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', String(active));
        });
        applyFilter();
      });
    });

    if (searchInput) {
      searchInput.addEventListener('input', applyFilter);
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', function () {
        activeTopic = 'all';
        if (searchInput) searchInput.value = '';
        topicBtns.forEach(function (b) {
          var active = b.getAttribute('data-topic-btn') === 'all';
          b.classList.toggle('is-active', active);
          b.setAttribute('aria-pressed', String(active));
        });
        applyFilter();
      });
    }

    applyFilter();
  }

  // 5. Guided Callback & Employer Inquiry Builder (static-safe email + copy summary)
  document.querySelectorAll('form[data-inquiry-form]').forEach(function (form) {
    var resultBox = form.parentElement.querySelector('[data-inquiry-result]');
    var previewEl = form.parentElement.querySelector('[data-inquiry-preview]');
    var mailtoEl = form.parentElement.querySelector('[data-inquiry-mailto]');
    var copyBtn = form.parentElement.querySelector('[data-inquiry-copy]');
    var errEl = form.querySelector('[data-inquiry-error]');
    var latestSummary = '';

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = (form.elements.name && form.elements.name.value || '').trim();
      var contact = (form.elements.contact && form.elements.contact.value || '').trim();
      var topic = (form.elements.topic && form.elements.topic.value || 'General Inquiry').trim();
      var timing = (form.elements.timing && form.elements.timing.value || 'Any weekday window').trim();
      var notes = (form.elements.notes && form.elements.notes.value || '').trim();

      if (!name || !contact) {
        if (errEl) {
          errEl.textContent = 'Please enter your name and preferred phone number or email address.';
          errEl.hidden = false;
        }
        return;
      }
      if (errEl) errEl.hidden = true;

      var lines = [
        'Inquiry Type: ' + topic,
        'Name / Organization: ' + name,
        'Preferred Contact: ' + contact,
        'Best Time to Reach: ' + timing
      ];
      if (notes) lines.push('Notes (Non-Urgent): ' + notes);
      latestSummary = lines.join('\n');

      if (previewEl) previewEl.textContent = latestSummary;
      if (mailtoEl) {
        var subject = encodeURIComponent(topic + ': ' + name);
        var body = encodeURIComponent(latestSummary + '\n\nSent from burdsfamilypractice.com');
        mailtoEl.href = 'mailto:bfpstaff@burdsfamilypractice.com?subject=' + subject + '&body=' + body;
      }
      if (resultBox) {
        resultBox.hidden = false;
        resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });

    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        if (!latestSummary || !navigator.clipboard) return;
        navigator.clipboard.writeText(latestSummary).then(function () {
          var prev = copyBtn.textContent;
          copyBtn.textContent = 'Copied to Clipboard';
          setTimeout(function () { copyBtn.textContent = prev; }, 2000);
        });
      });
    }
  });

  // 6. FAQ Expand / Collapse All toggle
  document.querySelectorAll('[data-faq-toggle]').forEach(function (btn) {
    var faq = btn.parentElement.nextElementSibling;
    if (!faq) return;
    btn.addEventListener('click', function () {
      var details = faq.querySelectorAll('details');
      var anyClosed = false;
      details.forEach(function (d) { if (!d.open) anyClosed = true; });
      details.forEach(function (d) { d.open = anyClosed; });
      btn.textContent = anyClosed ? 'Collapse all questions' : 'Expand all questions';
    });
  });

  // 6b. Swipe rows on phones: hide the "swipe" hint once the user has scrolled
  document.querySelectorAll('[data-swipe]').forEach(function (row) {
    row.addEventListener('scroll', function () {
      if (row.scrollLeft > 24) {
        row.classList.add('is-swiped');
        var hint = row.previousElementSibling;
        if (hint && hint.classList.contains('swipe-hint')) hint.style.visibility = 'hidden';
      }
    }, { passive: true });
  });

  // 6c. Learning Hub guides (imported from Squarespace) hard-code many tiny labels;
  // raise anything under 13px so it stays readable on phones.
  document.querySelectorAll('.bfp-learn').forEach(function (root) {
    root.querySelectorAll('*').forEach(function (el) {
      if (!el.firstChild || el.closest('svg')) return;
      var size = parseFloat(getComputedStyle(el).fontSize);
      if (size && size < 13) el.style.setProperty('font-size', '13px', 'important');
    });
  });

  // 7. Back to top visibility & smooth click
  var topBtn = document.querySelector('.back-to-top');
  if (topBtn) {
    topBtn.hidden = false;
    function syncTop() {
      topBtn.classList.toggle('is-visible', window.scrollY > 520);
    }
    window.addEventListener('scroll', syncTop, { passive: true });
    syncTop();
    topBtn.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
})();

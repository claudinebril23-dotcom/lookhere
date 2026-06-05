import re

path = 'bookings/templates/admin/base_site.html'
content = open(path, encoding='utf-8').read()
original_len = len(content)

# ─────────────────────────────────────────────────────────────
# 1. REMOVE Quick Settings button from header HTML
# ─────────────────────────────────────────────────────────────
# Remove the settings button + entire qs-panel HTML block
# Find from the button to the closing </div> of qs-panel
qs_html_pattern = re.compile(
    r'\s*<button class="header-btn" id="settings-btn"[^>]*>.*?</button>\s*'
    r'<!-- Quick Settings Panel -->.*?</div>\s*<!-- end qs-panel -->',
    re.DOTALL
)
# Try exact match first
settings_btn_start = content.find('\n      <button class="header-btn" id="settings-btn"')
qs_panel_end = content.find('</div>\n\n      <button class="header-btn" id="settings-btn"')

# Find the settings button block
btn_marker = '      <button class="header-btn" id="settings-btn" aria-label="Quick settings">\n        <i class="fas fa-cog"></i>\n      </button>'
if btn_marker in content:
    # Find the full qs-panel block that follows
    btn_idx = content.find(btn_marker)
    # Find the end of the qs-panel div (it ends before the closing </div> of header-actions)
    # The qs-panel is a sibling of the button, find its closing tag
    panel_start = content.find('      <!-- Quick Settings Panel -->', btn_idx)
    if panel_start > 0:
        # Find the matching closing </div> for qs-panel
        # Count nested divs from qs-panel opening
        search_from = content.find('<div class="qs-panel"', panel_start)
        depth = 0
        i = search_from
        while i < len(content):
            if content[i:i+4] == '<div':
                depth += 1
            elif content[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    panel_end = i + 6
                    break
            i += 1
        
        # Remove button + panel
        remove_block = content[btn_idx - 7 : panel_end + 1]  # include leading newline
        content = content.replace(
            '\n\n      <button class="header-btn" id="settings-btn" aria-label="Quick settings">\n        <i class="fas fa-cog"></i>\n      </button>\n\n      <!-- Quick Settings Panel -->',
            ''
        )
        # Also remove the rest of the qs-panel up to its closing div
        # Re-find after first replacement
        qs_open = content.find('      <div class="qs-panel" id="qs-panel"')
        if qs_open > 0:
            depth = 0
            i = qs_open
            while i < len(content):
                if content[i:i+4] == '<div':
                    depth += 1
                elif content[i:i+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        qs_close = i + 6
                        break
                i += 1
            content = content[:qs_open] + content[qs_close:]
        print('✅ Removed settings button + qs-panel HTML')
    else:
        print('⚠️  qs-panel comment not found')
else:
    print('⚠️  settings button not found')

# ─────────────────────────────────────────────────────────────
# 2. REMOVE Quick Settings CSS block
# ─────────────────────────────────────────────────────────────
qs_css_start = content.find('  /* ========== QUICK SETTINGS PANEL ========== */')
if qs_css_start > 0:
    # Find the end — the next major CSS section comment
    qs_css_end = content.find('\n\n  /* ========== LIGHT MODE CLARITY', qs_css_start)
    if qs_css_end < 0:
        qs_css_end = content.find('\n\n  /* ========== DARK MODE', qs_css_start)
    if qs_css_end > 0:
        content = content[:qs_css_start] + content[qs_css_end:]
        print('✅ Removed Quick Settings CSS')
    else:
        print('⚠️  Could not find end of QS CSS block')
else:
    print('⚠️  QS CSS block not found')

# ─────────────────────────────────────────────────────────────
# 3. REMOVE Quick Settings JS block
# ─────────────────────────────────────────────────────────────
qs_js_start = content.find('  // ========== QUICK SETTINGS ==========')
if qs_js_start > 0:
    qs_js_end = content.find('\n  // ========== SMOOTH SCROLL REVEAL', qs_js_start)
    if qs_js_end > 0:
        content = content[:qs_js_start] + content[qs_js_end:]
        print('✅ Removed Quick Settings JS')
    else:
        print('⚠️  Could not find end of QS JS block')
else:
    print('⚠️  QS JS block not found')

# ─────────────────────────────────────────────────────────────
# 4. FIX DUPLICATE TOASTS — replace the DOMContentLoaded notification block
#    with a single, deduplicated version that:
#    - Uses a shown-message tracker to prevent duplicates
#    - Removes the separate gallery photo listener (it duplicates Django messages)
#    - Stores admin save actions as Notification records via API
#    - Makes notification items clickable (link to booking change page)
# ─────────────────────────────────────────────────────────────

old_domcontent = '''  // Check for success messages from Django
  document.addEventListener('DOMContentLoaded', function () {
    // Check URL parameters for success messages
    const urlParams = new URLSearchParams(window.location.search);
    const successMsg = urlParams.get('success');

    if (successMsg) {
      showNotification(decodeURIComponent(successMsg), 'success', 'Success');

      // Remove success parameter from URL
      urlParams.delete('success');
      const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
      window.history.replaceState({}, '', newUrl);
    }

    // Check for Django messages
    const djangoMessages = document.querySelectorAll('.messagelist li, .messages li');
    djangoMessages.forEach(msg => {
      const text = msg.textContent.trim();
      let type = 'info';

      if (msg.classList.contains('success')) type = 'success';
      else if (msg.classList.contains('error')) type = 'error';
      else if (msg.classList.contains('warning')) type = 'warning';

      if (text) {
        showNotification(text, type, type.charAt(0).toUpperCase() + type.slice(1));
      }

      // Hide Django's default message
      msg.style.display = 'none';
    });

    // Listen for gallery photo additions
    if (window.location.pathname.includes('/admin/bookings/galleryphoto/')) {
      // Check if we just added a photo (look for success message)
      const successMessages = document.querySelectorAll('.success, .messagelist .success');
      successMessages.forEach(msg => {
        const text = msg.textContent.trim();
        if (text.toLowerCase().includes('added') || text.toLowerCase().includes('successfully')) {
          // Extract photo title if available
          const titleMatch = text.match(/["\'](.*?)["\']/);
          const photoTitle = titleMatch ? titleMatch[1] : 'Photo';

          showNotification(
            `The Gallery Photo "${photoTitle}" was added successfully.`,
            'success',
            'Gallery Updated'
          );
        }
      });
    }
  });'''

new_domcontent = '''  // ── Deduplicated admin-save toast + bell integration ──
  // Pages where we intercept Django messages and store them in the bell
  const TRACKED_PAGES = [
    '/admin/bookings/booking/',
    '/admin/bookings/package/',
    '/admin/bookings/addon/',
    '/admin/bookings/galleryphoto/',
    '/admin/bookings/sitesettings/',
  ];

  function isTrackedPage() {
    return TRACKED_PAGES.some(p => window.location.pathname.startsWith(p));
  }

  // Single set to prevent showing the same message text twice per page load
  const shownMessages = new Set();

  function showOnce(text, type, title) {
    const key = type + ':' + text;
    if (shownMessages.has(key)) return;
    shownMessages.add(key);
    showNotification(text, type, title);
  }

  document.addEventListener('DOMContentLoaded', function () {
    // URL ?success= parameter
    const urlParams = new URLSearchParams(window.location.search);
    const successMsg = urlParams.get('success');
    if (successMsg) {
      showOnce(decodeURIComponent(successMsg), 'success', 'Success');
      urlParams.delete('success');
      const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
      window.history.replaceState({}, '', newUrl);
    }

    // Django messagelist — one toast per unique message, hide the default UI
    const djangoMessages = document.querySelectorAll('.messagelist li, .messages li');
    djangoMessages.forEach(msg => {
      const text = msg.textContent.trim();
      if (!text) return;
      let type = 'info';
      if (msg.classList.contains('success')) type = 'success';
      else if (msg.classList.contains('error')) type = 'error';
      else if (msg.classList.contains('warning')) type = 'warning';

      showOnce(text, type, type.charAt(0).toUpperCase() + type.slice(1));
      msg.style.display = 'none';
    });
  });'''

if old_domcontent in content:
    content = content.replace(old_domcontent, new_domcontent)
    print('✅ Fixed duplicate toast / DOMContentLoaded block')
else:
    # Try a looser match for the gallery photo section
    gallery_block_start = content.find("    // Listen for gallery photo additions")
    if gallery_block_start > 0:
        gallery_block_end = content.find('\n  });\n\n  // ========== PREVENT', gallery_block_start)
        if gallery_block_end > 0:
            content = content[:gallery_block_start] + content[gallery_block_end:]
            print('✅ Removed gallery photo duplicate listener (partial fix)')
        else:
            print('⚠️  Could not remove gallery block')
    print('⚠️  Full DOMContentLoaded replacement not matched — check manually')

# ─────────────────────────────────────────────────────────────
# 5. Make notification items CLICKABLE — update renderNotifPanel
#    to wrap booking notifications in an anchor tag
# ─────────────────────────────────────────────────────────────
old_render = '''    list.innerHTML = notifications.map(n => `
      <div class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}">
        <div class="notif-item-dot"></div>
        <div class="notif-item-body">
          <div class="notif-item-title">${escapeHtml(n.title)}</div>
          <div class="notif-item-msg">${escapeHtml(n.message)}</div>
          <div class="notif-item-time">${escapeHtml(n.created_at)}</div>
        </div>
      </div>
    `).join('');'''

new_render = '''    list.innerHTML = notifications.map(n => {
      const href = n.admin_url || '';
      const tag = href ? 'a' : 'div';
      const hrefAttr = href ? `href="${escapeHtml(href)}"` : '';
      return `
        <${tag} class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}" ${hrefAttr}>
          <div class="notif-item-dot"></div>
          <div class="notif-item-body">
            <div class="notif-item-title">${escapeHtml(n.title)}</div>
            <div class="notif-item-msg">${escapeHtml(n.message)}</div>
            <div class="notif-item-time">${escapeHtml(n.created_at)}</div>
          </div>
        </${tag}>
      `;
    }).join('');

    // Mark individual notification as read on click
    list.querySelectorAll('.notif-item[data-id]').forEach(item => {
      item.addEventListener('click', function () {
        const id = this.dataset.id;
        if (!this.classList.contains('unread')) return;
        fetch('/api/notifications/mark-read/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
          },
          body: 'id=' + id,
        }).then(() => {
          this.classList.remove('unread');
          fetchNotifications(false);
        }).catch(() => {});
      });
    });'''

if old_render in content:
    content = content.replace(old_render, new_render)
    print('✅ Made notification items clickable')
else:
    print('⚠️  renderNotifPanel list.innerHTML not matched')

# ─────────────────────────────────────────────────────────────
# 6. Fix seenNotifIds seed logic — currently seeds AFTER the
#    forEach so it never actually seeds on first load
# ─────────────────────────────────────────────────────────────
old_fetch = '''        if (toastNew) {
          // Toast only unread notifications not yet seen this session
          data.notifications.forEach(n => {
            if (!n.is_read && !seenNotifIds.has(n.id)) {
              seenNotifIds.add(n.id);
              showNotification(n.message, 'success', n.title);
            }
          });
        }

        // Seed seen IDs on first load so we don't toast existing notifications
        if (seenNotifIds.size === 0) {
          data.notifications.forEach(n => seenNotifIds.add(n.id));
        }'''

new_fetch = '''        // Seed on first load BEFORE toasting so existing notifs are never shown
        if (seenNotifIds.size === 0) {
          data.notifications.forEach(n => seenNotifIds.add(n.id));
        } else if (toastNew) {
          // Toast only unread notifications not yet seen this session
          data.notifications.forEach(n => {
            if (!n.is_read && !seenNotifIds.has(n.id)) {
              seenNotifIds.add(n.id);
              showOnce(n.message, 'success', n.title);
            }
          });
        }'''

if old_fetch in content:
    content = content.replace(old_fetch, new_fetch)
    print('✅ Fixed seenNotifIds seed logic')
else:
    print('⚠️  seenNotifIds block not matched')

# ─────────────────────────────────────────────────────────────
# Write result
# ─────────────────────────────────────────────────────────────
open(path, 'w', encoding='utf-8').write(content)
print(f'\nDone. File size: {original_len} → {len(content)} chars')

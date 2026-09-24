/**
 * Sugar Rush chatbot widget — dùng chung cho các trang HTML tĩnh
 * (shop.html, about-us.html, contact.html). Trang chủ dùng bản React
 * trong src/App.tsx nên KHÔNG cần nạp file này ở trang chủ.
 */
(function () {
  if (window.__sugarRushChatbot) return;
  window.__sugarRushChatbot = true;

  var STYLE = [
    '.sr-chat-root{position:fixed;bottom:24px;right:24px;z-index:50;display:flex;flex-direction:column;align-items:flex-end;gap:12px;font-family:Arial,sans-serif;}',
    '.sr-chat-panel{width:min(400px,calc(100vw - 24px));height:0;opacity:0;transform:translateY(22px) scale(0.96);transform-origin:bottom right;transition:all .3s ease;overflow:hidden;border-radius:20px;pointer-events:none;box-shadow:0 18px 40px rgba(0,0,0,.18);background:#f5f5f5;border:1px solid rgba(68,68,68,.14);display:flex;flex-direction:column;}',
    '.sr-chat-panel.open{height:min(680px,calc(100dvh - 140px));opacity:1;transform:translateY(0) scale(1);pointer-events:auto;}',
    '.sr-chat-head{height:62px;flex-shrink:0;background:#3a62ff;display:flex;align-items:center;justify-content:space-between;padding:0 14px 0 12px;color:#fff;}',
    '.sr-chat-head-info{display:flex;align-items:center;gap:8px;}',
    '.sr-chat-avatar{width:30px;height:30px;border-radius:50%;overflow:hidden;background:#fff;display:flex;align-items:center;justify-content:center;}',
    '.sr-chat-avatar img{width:100%;height:100%;object-fit:cover;display:block;}',
    '.sr-chat-title{font-size:16px;font-weight:700;line-height:1.2;}',
    '.sr-chat-status{display:flex;align-items:center;gap:6px;font-size:11px;opacity:.9;}',
    '.sr-chat-status i{width:7px;height:7px;border-radius:50%;background:#91f5a6;display:inline-block;}',
    '.sr-chat-min{width:26px;height:26px;border-radius:50%;border:none;background:rgba(255,255,255,.18);color:#fff;font-size:18px;cursor:pointer;line-height:1;display:flex;align-items:center;justify-content:center;}',
    '.sr-chat-body{flex:1 1 auto;min-height:0;background:#f8f8f8;padding:12px 12px 10px;display:flex;flex-direction:column;gap:12px;overflow-y:auto;}',
    '.sr-chat-time{align-self:flex-end;font-size:10px;color:#6a6a6a;}',
    '.sr-chat-msg{max-width:84%;border-radius:14px;padding:10px 12px;font-size:13px;line-height:1.5;color:#202124;background:#e8e8eb;}',
    '.sr-chat-msg.user{align-self:flex-end;background:#FFB5C1;}',
    '.sr-chat-msg-wrap{display:flex;flex-direction:column;gap:3px;align-items:flex-end;}',
    '.sr-chat-msg-wrap.bot{align-items:flex-start;}',
    '.sr-chat-foot{flex-shrink:0;background:#f7f7f7;padding:10px 12px 12px;border-top:1px solid rgba(0,0,0,.06);}',
    '.sr-chat-chips{display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;}',
    '.sr-chat-chip{border:1px solid rgba(73,78,242,.2);border-radius:999px;background:#fff;padding:8px 10px;font-size:11px;color:#3a3a3a;cursor:pointer;font-family:Arial,sans-serif;}',
    '.sr-chat-form{display:flex;align-items:center;gap:10px;background:#ececef;border-radius:16px;padding:6px 8px 6px 12px;}',
    '.sr-chat-input{flex:1;min-width:0;border:none;outline:none;background:transparent;font-family:Arial,sans-serif;font-size:13px;color:#202124;}',
    '.sr-chat-send{width:30px;height:30px;border-radius:50%;border:none;background:linear-gradient(135deg,#4b6bff 0%,#6d5ef6 100%);color:#fff;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;}',
    '.sr-chat-toggle{border:none;background:transparent;padding:0;cursor:pointer;width:64px;height:79px;display:flex;align-items:center;justify-content:center;transition:transform .2s ease,opacity .2s ease;}',
    '.sr-chat-toggle img{width:100%;height:100%;object-fit:contain;display:block;}'
  ].join('');

  var css = document.createElement('style');
  css.textContent = STYLE;
  document.head.appendChild(css);

  function now() {
    try {
      return new Intl.DateTimeFormat('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date());
    } catch (e) {
      var d = new Date();
      return (d.getHours() < 10 ? '0' : '') + d.getHours() + ':' + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes();
    }
  }

  var root = document.createElement('div');
  root.className = 'sr-chat-root';
  root.innerHTML =
    '<div class="sr-chat-panel" id="srChatPanel">' +
      '<div class="sr-chat-head">' +
        '<div class="sr-chat-head-info">' +
          '<div class="sr-chat-avatar"><img src="/chatbot2.svg" alt="AI"></div>' +
          '<div>' +
            '<div class="sr-chat-title">Sugar Rush</div>' +
            '<div class="sr-chat-status"><i></i>Trực tuyến</div>' +
          '</div>' +
        '</div>' +
        '<button type="button" class="sr-chat-min" aria-label="Thu nhỏ">&minus;</button>' +
      '</div>' +
      '<div class="sr-chat-body" id="srChatBody">' +
        '<div style="display:flex;align-items:center;gap:8px;">' +
          '<img src="/chatbot2.svg" alt="AI" style="width:26px;height:26px;border-radius:50%;object-fit:cover;display:block;">' +
          '<span style="font-size:10px;color:#666;">' + now() + '</span>' +
        '</div>' +
        '<div class="sr-chat-msg">Chào bạn! Mình là trợ lý ảo chăm sóc da của <strong>Sugar Rush</strong>. Hôm nay da của bạn đang gặp vấn đề gì (mụn, khô, thâm sạm...) hay bạn cần tìm sản phẩm nào nhỉ?</div>' +
        '<div class="sr-chat-time">' + now() + '</div>' +
      '</div>' +
      '<div class="sr-chat-foot">' +
        '<div class="sr-chat-chips">' +
          '<button type="button" class="sr-chat-chip">Sản phẩm bán chạy</button>' +
          '<button type="button" class="sr-chat-chip">Bảng giá</button>' +
          '<button type="button" class="sr-chat-chip">Cách dùng</button>' +
        '</div>' +
        '<form class="sr-chat-form">' +
          '<input class="sr-chat-input" placeholder="Nhập tin nhắn của bạn..." aria-label="Chat message">' +
          '<button type="submit" class="sr-chat-send" aria-label="Send message">&#10148;</button>' +
        '</form>' +
      '</div>' +
    '</div>' +
    '<button type="button" class="sr-chat-toggle" aria-label="Open chat"><img src="/chatbot2.svg" alt="chat"></button>';
  document.body.appendChild(root);

  var panel = root.querySelector('#srChatPanel');
  var body = root.querySelector('#srChatBody');
  var form = root.querySelector('.sr-chat-form');
  var input = root.querySelector('.sr-chat-input');
  var toggleBtn = root.querySelector('.sr-chat-toggle');
  var minBtn = root.querySelector('.sr-chat-min');

  function setOpen(open) {
    panel.classList.toggle('open', open);
  }

  toggleBtn.addEventListener('click', function () {
    setOpen(!panel.classList.contains('open'));
  });
  minBtn.addEventListener('click', function () {
    setOpen(false);
  });

  function addMessage(role, text, time) {
    var wrap = document.createElement('div');
    wrap.className = 'sr-chat-msg-wrap' + (role === 'user' ? '' : ' bot');
    var bubble = document.createElement('div');
    bubble.className = 'sr-chat-msg' + (role === 'user' ? ' user' : '');
    bubble.textContent = text;
    var stamp = document.createElement('span');
    stamp.className = 'sr-chat-time';
    stamp.textContent = time + (role === 'user' ? ' \u2713' : '');
    wrap.appendChild(bubble);
    wrap.appendChild(stamp);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function sendMessage(text) {
    text = (text || '').trim();
    if (!text) return;
    input.value = '';
    addMessage('user', text, now());

    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    })
      .then(function (res) {
        if (!res.ok) throw new Error('Chat request failed: ' + res.status);
        return res.json();
      })
      .then(function (data) {
        addMessage('ai', data.response || data.reply || 'Không nhận được phản hồi.', now());
      })
      .catch(function () {
        addMessage('ai', 'Không kết nối được với Python. Hãy chạy scene_1.py trước.', now());
      });
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage(input.value);
  });

  root.querySelectorAll('.sr-chat-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      sendMessage(chip.textContent);
    });
  });
})();
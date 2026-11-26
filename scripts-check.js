/* Simple navigation between sections inside this single-page prototype */
  function navigate(id){
    // hide all main sections (home, community, gallery, notifications, profile)
    const sections = ['home','community','gallery','notifications','profile'];
    sections.forEach(s => {
      const el = document.getElementById(s);
      if(el) el.style.display = (s === id ? 'block' : 'none');
    });
    // if target doesn't exist, fallback to home
    if(!document.getElementById(id)) {
      if(id === 'community') openModal('community');
      if(id === 'gallery') openModal('gallery');
      if(id === 'notifications') openModal('notifications');
      if(id === 'profile') openModal('profile');
    }
    // scroll top
    window.scrollTo({top:0, behavior:'smooth'});
  }

  // initialize: hide non-home sections (this prototype has home visible only)
  ['community','gallery','notifications','profile'].forEach(s=>{
    if(!document.getElementById(s)) {
      const wrapper = document.createElement('section');
      wrapper.id = s;
      wrapper.style.display = 'none';
      wrapper.className = 'left-col';
      wrapper.innerHTML = '<div class="card"><h3>'+s.charAt(0).toUpperCase()+s.slice(1)+'</h3><p style="color:#666; margin-top:8px">Section en prototype: app single-file (HTML). Cliquez sur les boutons pour simuler.</p></div>';
      document.querySelector('main').prepend(wrapper);
    } else {
      document.getElementById(s).style.display = 'none';
    }
  });

  // Modal helper
  function openModal(name){
    const root = document.getElementById('modal-root');
    root.style.display = 'block';
    root.innerHTML = ''; // clear
    const backdrop = document.createElement('div');
    backdrop.className = 'modal-backdrop';
    backdrop.onclick = (e)=>{ if(e.target === backdrop) closeModal(); };
    const modal = document.createElement('div');
    modal.className = 'modal';

    if(name === 'publish'){
      modal.innerHTML = '<h3>Nouvelle publication</h3>'
        + '<div class="row"><input type="text" id="pub-title" placeholder="Titre (optionnel)"></div>'
        + '<div class="row"><textarea id="pub-text" rows="4" placeholder="Ã‰crivez votre texte, tÃ©moignage, annonce..."></textarea></div>'
        + '<div class="row"><input type="file" id="pub-media" accept="image/*,video/*"></div>'
        + '<div style="display:flex; gap:8px; justify-content:flex-end;"><button class="btn ghost" onclick="closeModal()">Annuler</button><button class="btn primary" onclick="publish()">Publier</button></div>';
    } else if(name === 'donate'){
      modal.innerHTML = '<h3>Faire un don</h3>'
        + '<p style="color:#666">Choisissez un montant (ex: Mobile Money, Carte bancaire, PayPal) â€” ceci est un mock (prototype).</p>'
        + '<div class="donation-grid" style="margin:10px 0">'
        + '<button class="donation-amt" onclick="selectAmt(this)">10â‚¬</button>'
        + '<button class="donation-amt" onclick="selectAmt(this)">25â‚¬</button>'
        + '<button class="donation-amt" onclick="selectAmt(this)">50â‚¬</button>'
        + '<button class="donation-amt" onclick="selectAmt(this)">100â‚¬</button>'
        + '<button class="donation-amt" onclick="selectAmt(this)">Autre</button>'
        + '</div>'
        + '<div class="row" id="other-amt-row" style="display:none"><input type="number" id="other-amt" placeholder="Montant libre (EUR)"></div>'
        + '<div class="row"><select id="pay-method"><option>Mobile Money</option><option>Carte bancaire</option><option>PayPal</option></select></div>'
        + '<div style="display:flex; gap:8px; justify-content:flex-end; margin-top:8px;"><button class="btn ghost" onclick="closeModal()">Annuler</button><button class="btn primary" onclick="donate()">Payer</button></div>';
    } else if(name === 'messenger'){
      modal.innerHTML = '<h3>Messagerie (prototype)</h3>'
        + '<p style="color:#666">Chat individuel et groupe — en vrai: WebSocket / RTC.</p>'
        + '<div style="display:flex; justify-content:flex-end; margin-top:8px;"><button class="btn" onclick="closeModal()">Fermer</button></div>';
    } else {
      modal.innerHTML = '<h3>Fenêtre: ' + name + '</h3>'
        + '<div style="display:flex; justify-content:flex-end; margin-top:8px;"><button class="btn" onclick="closeModal()">Fermer</button></div>';
    }

    backdrop.appendChild(modal);
    root.appendChild(backdrop);
  }

  function closeModal(){
    const root = document.getElementById('modal-root');
    if(!root) return;
    root.style.display = 'none';
    root.innerHTML = '';
  }

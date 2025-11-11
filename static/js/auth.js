// Auth page helpers: password toggle + conditional organization fields
(function(){
  // Password show/hide toggle
  function togglePassword(btn){
    var targetId = btn.getAttribute('data-target');
    var input = document.getElementById(targetId);
    if(!input) return;
    if(input.type === 'password'){
      input.type = 'text';
      btn.textContent = 'Hide';
    } else {
      input.type = 'password';
      btn.textContent = 'Show';
    }
  }

  document.addEventListener('click', function(ev){
    var btn = ev.target.closest('.toggle-pass');
    if(btn){
      togglePassword(btn);
      ev.preventDefault();
    }
  });

  // Organization/Self switch: hide org fields when Self selected
  function applyOrgFieldsVisibility(selected){
    var container = document.querySelector('.org-fields');
    var orgName = document.getElementById('org_name');
    var role = document.getElementById('role_in_org');
    if(!container || !orgName || !role) return;
    var isSelf = (selected === 'self');
    if(isSelf){
      container.classList.add('hidden');
      orgName.disabled = true; role.disabled = true;
      orgName.removeAttribute('required'); role.removeAttribute('required');
    } else {
      container.classList.remove('hidden');
      orgName.disabled = false; role.disabled = false;
      orgName.setAttribute('required','true'); role.setAttribute('required','true');
    }
  }

  function initOrgSwitch(){
    var radios = Array.prototype.slice.call(document.querySelectorAll('input[name="account_type"]'));
    if(radios.length === 0) return;
    var checked = radios.find(function(r){ return r.checked; });
    applyOrgFieldsVisibility(checked ? checked.value : 'organization');
    radios.forEach(function(r){
      r.addEventListener('change', function(){ applyOrgFieldsVisibility(this.value); });
    });
  }

  function initCaptchaGate(){
    var forms = Array.prototype.slice.call(document.querySelectorAll('form.auth-form'));
    forms.forEach(function(form){
      var checkbox = form.querySelector('.captcha-box input[type="checkbox"]');
      var submit = form.querySelector('[data-requires-captcha]');
      if(!checkbox || !submit) return;
      // Initialize disabled state until checked
      submit.disabled = !checkbox.checked;
      checkbox.addEventListener('change', function(){
        submit.disabled = !checkbox.checked;
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function(){
    initOrgSwitch();
    initCaptchaGate();
  });
})();
// Client-side guidance only; Django remains responsible for validation.
(() => {
  const password = document.querySelector('input[name="password1"]');
  const confirm = document.querySelector('input[name="password2"]');
  const feedback = document.getElementById('password-feedback');
  if (password && confirm && feedback) {
    const meter = document.getElementById('password-strength');
    const strength = document.getElementById('password-strength-text');
    const match = document.getElementById('password-match');
    const update = () => {
      const value = password.value;
      feedback.hidden = !value && !confirm.value;
      let score = 0;
      if (value.length >= 8) score++;
      if (value.length >= 12) score++;
      if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score++;
      if (/\d/.test(value) && /[^a-zA-Z0-9\s]/.test(value)) score++;
      if (value.length < 8) score = Math.min(score, 1);
      meter.value = score;
      strength.textContent = value ? ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'][score] + ' (estimate only)' : '';
      match.textContent = !confirm.value ? '' : value === confirm.value ? 'Passwords match.' : 'Passwords do not match.';
    };
    password.addEventListener('input', update);
    confirm.addEventListener('input', update);
    update();
  }
  const loginPassword = document.querySelector('input[name="password"]');
  const warning = document.getElementById('caps-lock-warning');
  if (loginPassword && warning) {
    const update = event => {
      warning.hidden = !event.getModifierState('CapsLock');
    };
    loginPassword.addEventListener('keydown', update);
    loginPassword.addEventListener('keyup', update);
    loginPassword.addEventListener('blur', () => { warning.hidden = true; });
  }
})();

/**
 * Submits any <form data-ajax-form> to its Formspree action in the background
 * and shows the outcome in the form's [data-form-status] element.
 * Without JavaScript the form still posts normally to Formspree.
 */

function setStatus(form: HTMLFormElement, message: string, isError: boolean) {
  const status = form.querySelector<HTMLElement>('[data-form-status]');
  if (!status) return;
  status.textContent = message;
  status.dataset.state = isError ? 'error' : 'success';
  status.hidden = false;
}

document.querySelectorAll<HTMLFormElement>('form[data-ajax-form]').forEach((form) => {
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector<HTMLButtonElement>('button[type="submit"]');
    if (button) button.disabled = true;

    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' },
      });

      if (res.ok) {
        form.reset();
        setStatus(form, form.dataset.successMessage ?? 'Thank you — your message has been sent.', false);
      } else {
        const body = await res.json().catch(() => null);
        const detail = body?.errors?.map((e: { message: string }) => e.message).join(' ');
        console.error('Form submission failed', { action: form.action, status: res.status, detail });
        setStatus(form, detail || 'Sorry, something went wrong. Please try again or email me directly.', true);
      }
    } catch (err) {
      console.error('Form submission error', { action: form.action, err });
      setStatus(form, 'Sorry, the message could not be sent. Please check your connection and try again.', true);
    } finally {
      if (button) button.disabled = false;
    }
  });
});

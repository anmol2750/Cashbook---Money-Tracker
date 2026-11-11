(() => {
  const root = document.querySelector("[data-currency-converter]");
  if (!root) return;

  const form = root.querySelector("[data-converter-form]");
  const amountInput = root.querySelector("[data-converter-amount]");
  const fromSelect = root.querySelector("[data-currency-from]");
  const toSelect = root.querySelector("[data-currency-to]");
  const swapButton = root.querySelector("[data-currency-swap]");
  const convertButton = root.querySelector("[data-convert-button]");
  const result = root.querySelector("[data-conversion-result]");
  const rateDetails = root.querySelector("[data-rate-details]");
  const apiBase = root.dataset.apiBase;
  const locale = root.dataset.locale || undefined;
  let hasConverted = false;

  function currencyFormatter(currency) {
    try {
      return new Intl.NumberFormat(locale, { style: "currency", currency });
    } catch (_) {
      return new Intl.NumberFormat(undefined, { style: "currency", currency });
    }
  }

  function numberFormatter() {
    return new Intl.NumberFormat(locale, { maximumSignificantDigits: 8 });
  }

  async function loadCurrencies() {
    try {
      const response = await fetch(`${apiBase}/currencies`);
      if (!response.ok) return;
      const currencies = await response.json();
      if (!Array.isArray(currencies)) return;

      [fromSelect, toSelect].forEach((select) => {
        const selected = select.value;
        const options = currencies
          .filter((currency) => currency.iso_code && currency.name)
          .sort((left, right) => left.iso_code.localeCompare(right.iso_code))
          .map((currency) => {
            const option = document.createElement("option");
            option.value = currency.iso_code;
            option.textContent = `${currency.name} (${currency.iso_code})`;
            return option;
          });
        select.replaceChildren(...options);
        if (currencies.some((currency) => currency.iso_code === selected)) select.value = selected;
      });
    } catch (_) {
      // Keep the currencies configured in the app available if the list service is offline.
    }
  }

  async function convert() {
    const amount = Number(amountInput.value);
    if (!Number.isFinite(amount) || amount < 0.000001) {
      amountInput.reportValidity();
      return;
    }

    const from = fromSelect.value;
    const to = toSelect.value;
    convertButton.disabled = true;
    rateDetails.textContent = root.dataset.loadingMessage;

    try {
      if (from === to) {
        result.textContent = currencyFormatter(to).format(amount);
        rateDetails.textContent = `1 ${from} = 1 ${to}`;
        hasConverted = true;
        return;
      }

      const response = await fetch(`${apiBase}/rate/${encodeURIComponent(from.toLowerCase())}/${encodeURIComponent(to.toLowerCase())}`);
      if (!response.ok) throw new Error("Rate unavailable");
      const data = await response.json();
      if (!Number.isFinite(data.rate)) throw new Error("Invalid rate");

      result.textContent = currencyFormatter(to).format(amount * data.rate);
      rateDetails.textContent = `1 ${from} = ${numberFormatter().format(data.rate)} ${to} · ${root.dataset.rateDateLabel}: ${data.date}`;
      hasConverted = true;
    } catch (_) {
      result.textContent = "—";
      rateDetails.textContent = root.dataset.errorMessage;
      hasConverted = false;
    } finally {
      convertButton.disabled = false;
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    convert();
  });

  swapButton.addEventListener("click", () => {
    const previousFrom = fromSelect.value;
    fromSelect.value = toSelect.value;
    toSelect.value = previousFrom;
    if (hasConverted) convert();
  });

  loadCurrencies();
})();

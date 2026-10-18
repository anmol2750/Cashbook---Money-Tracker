(() => {
  const root = document.querySelector(".cash-counter");
  if (!root) return;

  const rows = [...root.querySelectorAll("[data-denomination]")];
  const totalOutputs = [...root.querySelectorAll("[data-grand-total], [data-grand-total-copy]")];
  const pieceCount = root.querySelector("[data-piece-count]");
  const prefix = root.dataset.currencyPrefix || "";
  const amountFormat = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });
  const countFormat = new Intl.NumberFormat();
  const status = root.querySelector("[data-status]");
  const shareButton = root.querySelector("[data-share]");
  let statusTimer;

  function asMinorUnits(value) {
    return Math.round(Number(value) * 100);
  }

  function formatMinorUnits(value) {
    return amountFormat.format(value / 100);
  }

  function readCount(input) {
    const value = Number.parseInt(input.value, 10);
    return Number.isFinite(value) && value > 0 ? value : 0;
  }

  function update() {
    let totalMinorUnits = 0;
    let totalPieces = 0;

    rows.forEach((row) => {
      const denomination = asMinorUnits(row.dataset.denomination);
      const input = row.querySelector("[data-count]");
      const count = readCount(input);
      const rowTotal = denomination * count;
      totalMinorUnits += rowTotal;
      totalPieces += count;
      row.querySelector("[data-line-total]").textContent = prefix + formatMinorUnits(rowTotal);
    });

    totalOutputs.forEach((output) => {
      output.textContent = formatMinorUnits(totalMinorUnits);
    });
    pieceCount.textContent = countFormat.format(totalPieces);
    root.dataset.totalMinorUnits = String(totalMinorUnits);
    root.dataset.totalPieces = String(totalPieces);
  }

  function announce(message) {
    window.clearTimeout(statusTimer);
    status.textContent = message;
    statusTimer = window.setTimeout(() => {
      status.textContent = "";
    }, 3000);
  }

  rows.forEach((row) => {
    const input = row.querySelector("[data-count]");
    input.addEventListener("input", () => {
      if (input.value !== "" && Number(input.value) < 0) input.value = "";
      if (input.value !== "" && !Number.isInteger(Number(input.value))) {
        input.value = String(Math.max(0, Math.floor(Number(input.value))));
      }
      update();
    });
    row.querySelectorAll("[data-adjust]").forEach((button) => {
      button.addEventListener("click", () => {
        const next = Math.max(0, readCount(input) + Number(button.dataset.adjust));
        input.value = next === 0 ? "" : String(next);
        update();
      });
    });
  });

  root.querySelector("[data-clear]").addEventListener("click", () => {
    rows.forEach((row) => {
      row.querySelector("[data-count]").value = "";
    });
    update();
    announce(root.dataset.clearMessage);
  });

  shareButton.addEventListener("click", async () => {
    const totalMinorUnits = Number(root.dataset.totalMinorUnits || 0);
    const totalPieces = Number(root.dataset.totalPieces || 0);
    const lines = rows.flatMap((row) => {
      const count = readCount(row.querySelector("[data-count]"));
      if (!count) return [];
      const denomination = row.dataset.denomination;
      const lineTotal = asMinorUnits(denomination) * count;
      return [prefix + denomination + " × " + count + " = " + prefix + formatMinorUnits(lineTotal)];
    });
    const summary = [
      root.dataset.shareTitle,
      ...lines,
      root.dataset.sharePieces + ": " + countFormat.format(totalPieces),
      root.dataset.shareTotal + ": " + prefix + formatMinorUnits(totalMinorUnits),
    ].join("\n");

    try {
      if (navigator.share) {
        await navigator.share({ title: root.dataset.shareTitle, text: summary });
        announce(root.dataset.sharedMessage);
      } else if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(summary);
        announce(root.dataset.copiedMessage);
      } else {
        announce(root.dataset.unavailableMessage);
      }
    } catch (error) {
      if (error.name !== "AbortError") announce(root.dataset.errorMessage);
    }
  });

  update();
})();

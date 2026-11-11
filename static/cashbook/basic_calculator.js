(() => {
  const root = document.querySelector("[data-basic-calculator]");
  if (!root) return;

  const result = root.querySelector("[data-result]");
  const expression = root.querySelector("[data-expression]");
  const numberFormat = new Intl.NumberFormat(undefined, { maximumFractionDigits: 12 });
  let currentInput = "0";
  let previousValue = null;
  let operator = null;
  let waitingForOperand = false;
  let displayError = false;

  function formatInput(value) {
    if (value === "Error") return value;
    const [integer, fraction] = value.split(".");
    const formattedInteger = numberFormat.format(Number(integer || 0));
    return fraction === undefined ? formattedInteger : `${formattedInteger}.${fraction}`;
  }

  function render() {
    result.textContent = formatInput(currentInput);
  }

  function clear() {
    currentInput = "0";
    previousValue = null;
    operator = null;
    waitingForOperand = false;
    displayError = false;
    expression.textContent = "";
    render();
  }

  function startNewOperand() {
    if (displayError) clear();
    if (waitingForOperand) {
      currentInput = "0";
      waitingForOperand = false;
    }
  }

  function enterDigit(digit) {
    startNewOperand();
    if (currentInput === "0") currentInput = digit;
    else if (currentInput === "-0") currentInput = `-${digit}`;
    else if (currentInput.replace(/\D/g, "").length < 15) currentInput += digit;
    render();
  }

  function enterDecimal() {
    startNewOperand();
    if (!currentInput.includes(".")) currentInput += ".";
    render();
  }

  function calculate(left, right, selectedOperator) {
    if (selectedOperator === "+") return left + right;
    if (selectedOperator === "-") return left - right;
    if (selectedOperator === "*") return left * right;
    if (selectedOperator === "/") return right === 0 ? null : left / right;
    return right;
  }

  function tidy(value) {
    return Number(value.toPrecision(12)).toString();
  }

  function chooseOperator(nextOperator) {
    if (displayError) clear();
    const inputValue = Number(currentInput);
    if (operator && !waitingForOperand) {
      const calculated = calculate(previousValue, inputValue, operator);
      if (calculated === null || !Number.isFinite(calculated)) return showError();
      currentInput = tidy(calculated);
      previousValue = calculated;
      render();
    } else {
      previousValue = inputValue;
    }
    operator = nextOperator;
    waitingForOperand = true;
    const operatorLabel = { "*": "×", "/": "÷", "-": "−" }[nextOperator] || nextOperator;
    expression.textContent = `${formatInput(tidy(previousValue))} ${operatorLabel}`;
  }

  function equals() {
    if (!operator || previousValue === null || waitingForOperand) return;
    const rightValue = Number(currentInput);
    const leftValue = previousValue;
    const selectedOperator = operator;
    const calculated = calculate(leftValue, rightValue, selectedOperator);
    if (calculated === null || !Number.isFinite(calculated)) return showError();
    const operatorLabel = { "*": "×", "/": "÷", "-": "−" }[selectedOperator] || selectedOperator;
    expression.textContent = `${formatInput(tidy(leftValue))} ${operatorLabel} ${formatInput(tidy(rightValue))} =`;
    currentInput = tidy(calculated);
    previousValue = null;
    operator = null;
    waitingForOperand = true;
    render();
  }

  function showError() {
    currentInput = "Error";
    previousValue = null;
    operator = null;
    waitingForOperand = true;
    displayError = true;
    expression.textContent = "";
    result.textContent = currentInput;
  }

  function applyAction(action) {
    if (action === "clear") return clear();
    if (action === "equals") return equals();
    if (action === "decimal") return enterDecimal();
    if (action === "sign") {
      if (displayError) clear();
      if (waitingForOperand && operator) {
        currentInput = "-0";
        waitingForOperand = false;
        return render();
      }
      if (Number(currentInput) !== 0) currentInput = currentInput.startsWith("-") ? currentInput.slice(1) : `-${currentInput}`;
      return render();
    }
    if (action === "percent") {
      if (displayError) clear();
      currentInput = tidy(Number(currentInput) / 100);
      return render();
    }
    if (action === "backspace") {
      if (waitingForOperand || displayError) return;
      currentInput = currentInput.length > 1 ? currentInput.slice(0, -1) : "0";
      if (currentInput === "-" || currentInput === "-0") currentInput = "0";
      return render();
    }
  }

  root.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button || !root.contains(button)) return;
    if (button.dataset.digit !== undefined) return enterDigit(button.dataset.digit);
    if (button.dataset.operator) return chooseOperator(button.dataset.operator);
    if (button.dataset.action) return applyAction(button.dataset.action);
  });

  document.addEventListener("keydown", (event) => {
    if (/^\d$/.test(event.key)) return enterDigit(event.key);
    if (event.key === ".") return enterDecimal();
    if (["+", "-", "*", "/"].includes(event.key)) return chooseOperator(event.key);
    if (event.key === "Enter" || event.key === "=") {
      event.preventDefault();
      return equals();
    }
    if (event.key === "Backspace") {
      event.preventDefault();
      return applyAction("backspace");
    }
    if (event.key === "Escape") return clear();
    if (event.key === "%") return applyAction("percent");
  });

  render();
})();

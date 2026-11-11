(() => {
  const categorySelect = document.querySelector("[data-category-select]");
  const customCategoryField = document.querySelector("[data-custom-category-field]");

  if (!categorySelect || !customCategoryField) return;

  const customCategoryInput = customCategoryField.querySelector("input");

  function updateCustomCategoryVisibility() {
    const needsCustomCategory = categorySelect.value === "__other__";
    customCategoryField.hidden = !needsCustomCategory;
    categorySelect.setAttribute("aria-expanded", String(needsCustomCategory));
    if (customCategoryInput) customCategoryInput.required = needsCustomCategory;
  }

  categorySelect.addEventListener("change", updateCustomCategoryVisibility);
  updateCustomCategoryVisibility();
})();

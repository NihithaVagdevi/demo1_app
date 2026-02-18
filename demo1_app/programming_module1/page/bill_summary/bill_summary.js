frappe.pages["bill-summary"].on_page_load = function (wrapper) {
  const page = frappe.ui.make_app_page({
    parent: wrapper,
    title: "Bill Summary",
    single_column: true
  });

  page.main.innerHTML = `
    <div class="card">
      <h3>Bill Summary</h3>
      <p id="total-bills">Total Bills: Loading...</p>
      <p id="total-amount">Total Amount: Loading...</p>
    </div>
  `;
};

(() => {
  // ../demo1_app/demo1_app/public/js/bill_summary.bundle.js
  console.log("\u2705 bill_summary.bundle.js loaded");
  frappe.call({
    method: "demo1_app.programming_module1.page.bill_summary.bill_summary.get_summary",
    callback: function(r) {
      if (r.message) {
        document.getElementById("total-bills").innerText = "Total Bills: " + r.message.count;
        document.getElementById("total-amount").innerText = "Total Amount: \u20B9" + r.message.total;
      }
    }
  });
})();
//# sourceMappingURL=bill_summary.bundle.ERB3BBM5.js.map

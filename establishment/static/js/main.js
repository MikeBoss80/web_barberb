$(document).ready(function() {
  const urlParams = new URLSearchParams(window.location.search);
  const activeTab = urlParams.get('tab');
  
  if (activeTab === 'management') {
    $('.tab-btn[data-tab="management"]').trigger('click');
  }
});

document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach(tab => tab.classList.remove("active"));
    btn.classList.add("active");
    
    fetch(btn.dataset.url)
      .then(res => res.text())
      .then(html => {
        document.querySelector("#tab-content").innerHTML = html;
        const tabType = btn.dataset.tab;
        if (tabType === 'management') {
          initializeManagementComponents();
        }
        // Aquí se puede agregar más validaciones para otros tabs
        // if (tabType === 'reportes' && typeof initializeReportesComponents === 'function') {
        //   initializeReportesComponents();
        // }
        // if (tabType === 'configuracion' && typeof initializeConfigComponents === 'function') {
        //   initializeConfigComponents();
        // }
      });
  });
});


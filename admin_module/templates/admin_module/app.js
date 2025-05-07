document.addEventListener("DOMContentLoaded", function () {
    const menuDashboard = document.querySelector(".menu-dashboard");
    const toggleBtn = document.querySelector(".top-menu .toggle");
  
    toggleBtn.addEventListener("click", function () {
      menuDashboard.classList.toggle("open");
    });
  });
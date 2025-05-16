<<<<<<< HEAD
// Esperar a que el DOM cargue
document.addEventListener('DOMContentLoaded', () => {
  console.log('app.js cargado');

  // Verificar existencia de elementos
  const barCtx = document.getElementById('barChart');
  const areaCtx = document.getElementById('areaChart');
  const donutCtx = document.getElementById('donutChart');

  if (!barCtx || !areaCtx || !donutCtx) {
    console.error('Elementos canvas no encontrados');
    return;
  }

  // Gráfica de barras: Ganancias 2021 vs 2020
  new Chart(barCtx, {
    type: 'bar',
    data: {
      labels: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep'],
      datasets: [
        {
          label: '2021',
          data: [1200,1400,1300,1000,1500,1700,1600,1800,1900],
          backgroundColor: '#4CAF50'
        },
        {
          label: '2020',
          data: [1000,1200,1100,900,1300,1400,1500,1600,1700],
          backgroundColor: '#FF9800'
        }
      ]
    },
    options: { responsive: true }
  });

  // Gráfica de área: Citas Realizadas
  new Chart(areaCtx, {
    type: 'line',
    data: {
      labels: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep'],
      datasets: [{
        label: 'Citas',
        data: [50,60,55,45,65,70,75,80,85],
        fill: true,
        backgroundColor: 'rgba(255,165,0,0.2)',
        borderColor: '#FF9800',
        tension: 0.4
      }]
    },
    options: { responsive: true }
  });

  // Gráfica de donut: Distribución de servicios
  new Chart(donutCtx, {
    type: 'doughnut',
    data: {
      labels: ['Corte','Tinte','Barba','Otros'],
      datasets: [{
        data: [45,30,15,10],
        backgroundColor: ['#FF9800','#4CAF50','#FF5722','#2196F3']
      }]
    },
    options: { responsive: true }
  });
});
=======
document.addEventListener("DOMContentLoaded", function () {
    const menuDashboard = document.querySelector(".menu-dashboard");
    const toggleBtn = document.querySelector(".top-menu .toggle");
  
    toggleBtn.addEventListener("click", function () {
      menuDashboard.classList.toggle("open");
    });
  });
>>>>>>> cf7be63 (Vista Dashboard agregada, mas menu de navegacion)

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
    
    console.log('📱 Cargando tab:', btn.dataset.tab, 'desde URL:', btn.dataset.url);
    
    fetch(btn.dataset.url)
      .then(res => {
        console.log('📥 Respuesta del tab recibida:', res.status);
        return res.text();
      })
      .then(html => {
        console.log('📄 HTML del tab cargado, insertando en contenedor...');
        document.querySelector("#tab-content").innerHTML = html;
        
        // Ejecutar scripts que están dentro del HTML cargado
        const scripts = document.querySelector("#tab-content").querySelectorAll('script');
        scripts.forEach(script => {
          if (script.src) {
            // Script externo - cargar dinámicamente
            const newScript = document.createElement('script');
            newScript.src = script.src;
            document.head.appendChild(newScript);
          } else {
            // Script inline - ejecutar directamente
            eval(script.textContent);
          }
        });
        
        const tabType = btn.dataset.tab;
        
        console.log('🔍 Procesando tab tipo:', tabType);
        
        if (tabType === 'management') {
          console.log('⚙️ Inicializando Management...');
          initializeManagementComponents();
        }
        // Inicializar componentes de configuración
        if (tabType === 'configuration') {
          console.log('🔧 Inicializando Configuration...');
          // Esperar un poco para que el script se ejecute
          setTimeout(() => {
            if (typeof initializeConfigComponents === 'function') {
              initializeConfigComponents();
            } else {
              console.error('❌ initializeConfigComponents no está definido después del timeout');
            }
          }, 100);
        }
        // Aquí se puede agregar más validaciones para otros tabs
        // if (tabType === 'reportes' && typeof initializeReportesComponents === 'function') {
        //   initializeReportesComponents();
        // }
      })
      .catch(err => {
        console.error('💥 Error cargando tab:', err);
      });
  });
});


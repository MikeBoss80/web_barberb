document.addEventListener('DOMContentLoaded', function () {
    fetch('http://127.0.0.1:8000/services/getmap/').then(response => {
        if (response.ok) {
            response.json().then(data => {
                (g=>{var h,a,k,p="The Google Maps JavaScript API",c="google",l="importLibrary",q="__ib__",m=document,b=window;b=b[c]||(b[c]={});var d=b.maps||(b.maps={}),r=new Set,e=new URLSearchParams,u=()=>h||(h=new Promise(async(f,n)=>{await (a=m.createElement("script"));e.set("libraries",[...r]+"");for(k in g)e.set(k.replace(/[A-Z]/g,t=>"_"+t[0].toLowerCase()),g[k]);e.set("callback",c+".maps."+q);a.src=`https://maps.${c}apis.com/maps/api/js?`+e;d[q]=f;a.onerror=()=>h=n(Error(p+" could not load."));a.nonce=m.querySelector("script[nonce]")?.nonce||"";m.head.append(a)}));d[l]?console.warn(p+" only loads once. Ignoring:",g):d[l]=(f,...n)=>r.add(f)&&u().then(()=>d[l](f,...n))})({
                    key: data.mapApiKey,
                    v: "weekly",
                    // Use the 'v' parameter to indicate the version to use (weekly, beta, alpha, etc.).
                    // Add other bootstrap parameters as needed, using camel case.
                });
                initMap();
            });
        }
    });
});
       
let map;
async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { PlacesService } = await google.maps.importLibrary("places");

    var ubitacionUser = new google.maps.LatLng(4.679531063698843,-74.04015630448359);

    map = new Map(document.getElementById("map"), {
        center: ubitacionUser,
        zoom: 15,
    });


    let btnSearch = document.getElementById("btnSearch");
    let inputSearch = document.getElementById("inputSearch");
    let request = {};
    document.getElementById("btnSearch").addEventListener("click", function () {
        let searchValue = inputSearch.value;
        if (searchValue) {
            request = {
                location: ubitacionUser, 
                query: searchValue,
                radius: 500
            };

            service = new PlacesService(map);
            service.textSearch(request, (results, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && results) {
                for (let i = 0; i < results.length; i++) {
                    createMarker(results[i]);
                }
            
                map.setCenter(results[0].geometry.location);
                }
            });
        } else {
            alert("Please enter a search term.");
        }
    });
    
    
}

function createMarker(place) {
    if (!place.geometry || !place.geometry.location) return;
  
    const marker = new google.maps.Marker({
      map,
      position: place.geometry.location,
    });
  
    google.maps.event.addListener(marker, "click", () => {
      infowindow.setContent(place.name || "");
      infowindow.open(map);
    });
}
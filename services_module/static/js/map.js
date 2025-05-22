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
    let lat = '4.679531063698843';
    let lng = '-74.04015630448359';
    var ubicationUser = new google.maps.LatLng(4.679531063698843,-74.04015630448359);

    map = new Map(document.getElementById("map"), {
        center: ubicationUser,
        zoom: 15,
    });


    let inputSearch = document.getElementById("inputSearch");
    document.getElementById("btnSearch").addEventListener("click", function () {
        let searchValue = inputSearch.value;
        if (searchValue) {
            const request = {
                location: '4.679531063698843,-74.04015630448359',
                query: searchValue,
                radius: 500
            }
            getPlacesList(request)
        } else {
            alert("Por favor ingrese un lugar a buscar");
        }
    });
}

function createMarker(place) {
    console.log(place);
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

function getPlacesList(params) {
    let url = 'http://127.0.0.1:8000/services/getplacesbysearch'
    url += `?query=${params.query}&location=${params.location}&radius=${params.radius}`;
    fetch(url).then(response => {
        if (response.ok) {
            response.json().then(data => {
                for (let i = 0; i < data.results.length; i++) {
                    createMarker(data.results[i]);
                }
                loadPlacesList(data.results);        
                map.setCenter(data.results[0].geometry.location);
            });
        }
    });
}

function loadPlacesList(dataPlaces) {
    let list = document.getElementById("listPlaces");
    list.innerHTML = '';
    dataPlaces.forEach((place) => {
        const card = document.createElement('div');
        card.className = 'card';
        card.style.width = '19rem';
        card.innerHTML = `
            <img src="https://placehold.co/100x50" class="card-img-top" alt="${place.name}">
            <div class="card-body">
                <h6 class="card-title">${place.name}</h6>
                <div class="row">
                    <div class="col-4">
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#staticBackdrop">
                        Solicitar
                        </button>
                    </div>
                    <div class="col-5">
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#staticBackdrop">
                        Ver más
                        </button>
                    </div>
                    <div class="col-3 align-self-center">
                        <p class="card-text">${place.rating ?? 0.0} <i class="bi bi-star-fill"></i></p>
                    </div>
                    </div>
                </div>
            </div>
        `;

        list.appendChild(card);
    });
}
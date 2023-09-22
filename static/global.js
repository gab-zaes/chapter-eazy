document.addEventListener("DOMContentLoaded", function(){
    if (document.querySelector(".drop-btn")) {
        btn = document.querySelector(".drop-btn");
        btn.addEventListener("click", function(){
            document.querySelector(".dropdown ul").classList.toggle("hidden");
        });
    }

    if (document.querySelector(".div-flashes")) {
        div = document.querySelector(".div-flashes");
        div.classList.add("animate");
    }

    // track current page
    if (window.location.pathname === "/write") {
        document.getElementById("write-link").classList.add("ativo");
    } else if (window.location.pathname === "/export") {
        document.getElementById("export-link").classList.add("ativo");
    }
});
document.addEventListener("DOMContentLoaded", function() {
    let meta = this.getElementById("meta")
    document.getElementById("pdf").addEventListener("click", () => {
        meta.classList.remove("hidden");
    });

    document.getElementById("md").addEventListener("click", () => {
        meta.classList.add("hidden");
    });

    document.getElementById("download").addEventListener("click", () => {
        let anchor = document.getElementById("download");
        anchor.download = document.getElementById("filename").innerText;

        console.log(anchor.href);

        anchor.click();
    })
    // document.querySelector("main").removeChild(anchor);
});
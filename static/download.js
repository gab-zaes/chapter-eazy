document.addEventListener("DOMContentLoaded", function() {
    let anchor = document.createElement("a");
    anchor.href = document.getElementById("path").innerText;
    anchor.download = document.getElementById("filename").innerText;

    console.log(anchor.href);

    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
});
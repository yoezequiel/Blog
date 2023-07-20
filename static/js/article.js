const modoLecturaBtn = document.getElementById("modoLecturaBtn");
const contenido = document.querySelector("#container");

modoLecturaBtn.addEventListener("click", () => {
    document.body.classList.toggle("modo-lectura");
    contenido.classList.toggle("modo-lectura");
});

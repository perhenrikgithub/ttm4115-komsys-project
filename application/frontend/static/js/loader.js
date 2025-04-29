document.addEventListener("DOMContentLoaded", function () {
    // const forms = document.querySelectorAll(".buttons form");
    const forms = document.querySelectorAll("form");
    const container = document.querySelector(".container");
    const loader = document.querySelector(".hidden");
    const report = document.querySelector(".report-container");

    const h2 = document.querySelector("h2");
    const h3 = document.querySelector("h3");

    forms.forEach((form) => {
        form.addEventListener("submit", function (event) {
            h2.style.display = "none";
            h3.style.display = "none";

            report.style.display = "none";
            container.style.display = "none";
            loader.style.display = "flex";
            loader.style.justifyContent = "center";
            loader.style.alignItems = "center";
            loader.style.height = "30vh";
        });
    });
});

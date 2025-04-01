
    document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("search-form");
    const searchMessage = document.getElementById("search-message");

    searchForm.addEventListener("submit", function (event) {
        event.preventDefault(); 
        searchMessage.style.display = "block";
    });
});


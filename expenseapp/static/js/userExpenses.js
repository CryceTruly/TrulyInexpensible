const field = document.getElementById("search");
const tableArea = document.querySelector(".table-area");
let outputArea = document.querySelector(".search-output-area");
let resultRows = document.querySelector(".result-rows");
const searchBtn = document.querySelector(".search-btn");
const currentPaginator = document.querySelector(".container-pagination");
tableArea.style.display = "block";
outputArea.style.display = "none";
currentPaginator.style.display = "block";
const showResults = (data) => {
  for (let expense = 0; expense < data.length; expense++) {
    resultRows.innerHTML += `
        <tr class="text-sm-left small">
     <td>${data[expense].amount}</td>
      <td>${data[expense].name}</td>
      <td>${data[expense].category}</td>
       <td>${new Date(data[expense].date).toDateString()}</td>

       </tr>
        `;
  }
};

const searchItems = (e) => {
  resultRows.innerHTML = ``;
  e.preventDefault();
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      var cookies = document.cookie.split(";");
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  var csrftoken = getCookie("csrftoken");

  if (field.value.trim() === "") {
    return;
  }

  fetch("/expenses/search_expenses", {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    body: JSON.stringify({ data: field.value.trim() }),
  })
    .then((data) => data.json())
    .then((data) => {
      tableArea.style.display = "none";
      outputArea.style.display = "block";
      currentPaginator.style.display = "none";

      if (data.length > 0) {
        showResults(data);
      } else {
        resultRows.innerHTML += `<p class="text-info lead">No Results Found for query <strong>${field.value.trim()}</strong></p>`;
      }
    })
    .catch((err) => err);
};

field.addEventListener("keyup", function (e) {
  if (field.value.trim().length > 0) {
    searchItems(e);
  } else {
    tableArea.style.display = "block";
    outputArea.style.display = "none";
    currentPaginator.style.display = "block";
  }
});

searchBtn.addEventListener("click", searchItems);

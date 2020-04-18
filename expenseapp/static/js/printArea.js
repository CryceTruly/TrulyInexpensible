const printArea = document.querySelector("#doc-content");
const printBtn = document.querySelector("#doc-button");

const printDoc = () => {
  console.log("333", 333);
  window.print();
};

printBtn.addEventListener("click", printDoc);

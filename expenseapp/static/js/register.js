const username = document.querySelector(".username");
const username_spinner = document.querySelector(".username_spinner");
const username_check_done = document.querySelector(".username-check-done");
const submit = document.querySelector(".submit-btn");
const email_spinner = document.querySelector(".email_spinner");
const email_check_done = document.querySelector(".email-check-done");
const emailField = document.querySelector(".user-email");
const passwordField = document.querySelector(".passwordField");
const showToggler = document.querySelector(".show-toggler");

showToggler.addEventListener("click", () => {
  if (showToggler.textContent == "SHOW") {
    showToggler.textContent = "HIDE";
    passwordField.setAttribute("type", "text");
  } else {
    showToggler.textContent = "SHOW";
    passwordField.setAttribute("type", "password");
  }
});

const checkUserName = async (e) => {
  const value = e.target.value;
  username_spinner.style.display = "none";
  username_check_done.style.display = "none";
  document.querySelector(".invalid-feedback").style.display = "none";

  if (value.trim().length > 0) {
    username_spinner.style.display = "block";
    document.querySelector(".invalid-feedback").style.display = "none";

    let response = await fetch(`/authentication/check_username`, {
      body: JSON.stringify({ username: value }),
      method: "post",
    });

    let data = await response.json();
    if (data.is_available) {
      username_spinner.style.display = "none";
      username_check_done.style.display = "block";
      username.classList.remove("is-invalid");

      submit.removeAttribute("disabled");
    } else {
      username.classList.add("is-invalid");
      submit.disabled = true;
      username_spinner.style.display = "none";
      username_check_done.style.display = "none";
      document.querySelector(".invalid-feedback").style.display = "block";
      document.querySelector(".invalid-feedback").innerHTML = data.error;
    }
  } else {
    username_spinner.style.display = "none";
    username_check_done.style.display = "none";
  }
};

const checkEmail = async (e) => {
  const value = e.target.value;
  email_spinner.style.display = "none";
  email_check_done.style.display = "none";
  document.querySelector(".email-invalid-feedback").style.display = "none";
  if (value.trim().length > 0) {
    email_spinner.style.display = "block";
    document.querySelector(".invalid-feedback").style.display = "none";
    let response = await fetch(`/authentication/check_email`, {
      body: JSON.stringify({ email: value }),
      method: "post",
    });
    let data = await response.json();

    if (data.valid) {
      email_spinner.style.display = "none";
      email_check_done.style.display = "block";
      document.querySelector(".email-invalid-feedback").style.display = "none";
      emailField.classList.remove("is-invalid");
    } else {
      emailField.classList.add("is-invalid");
      email_spinner.style.display = "none";
      email_check_done.style.display = "none";
      document.querySelector(".email-invalid-feedback").style.display = "block";
      document.querySelector(".email-invalid-feedback").innerHTML = data.error;
    }
  } else {
    email_spinner.style.display = "none";
    email_check_done.style.display = "none";
  }
};
username.addEventListener("keyup", checkUserName);
emailField.addEventListener("keyup", checkEmail);

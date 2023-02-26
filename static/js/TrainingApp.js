const tables = [
  document.getElementById('first'),
  document.getElementById('second'),
  document.getElementById('third'),
  document.getElementById('fourth'),
  document.getElementById('fifth'),
  document.getElementById('sixth'),
  document.getElementById('seventh')
];

const lastResults = document.getElementById('last-results')
const lastResultShow = document.getElementById('last-result-show')
const lastResultCheckbox = document.getElementById('last-result-checkbox')
const chooseDay = document.getElementById("id_day")

chooseDay.addEventListener('change', function () {
  let selectedDay = this.value;

  for (let i = 0; i < tables.length; i++) {
    if (i === (selectedDay - 1)) {
      tables[i].removeAttribute("hidden");
      lastResults.setAttribute('hidden', "true")
      lastResultShow.removeAttribute("hidden")
    } else {
      tables[i].setAttribute("hidden", "true");
    }
  }
});

lastResultCheckbox.addEventListener('change', function (){
  if (this.checked) {
    lastResults.removeAttribute("hidden")
  } else {
    lastResults.setAttribute('hidden', "true")
  }
})





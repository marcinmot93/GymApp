const tables = [
  document.getElementById('first'),
  document.getElementById('second'),
  document.getElementById('third'),
  document.getElementById('fourth'),
  document.getElementById('fifth'),
  document.getElementById('sixth'),
  document.getElementById('seventh')
];

const chooseDay = document.getElementById("id_day")

chooseDay.addEventListener('change', function () {
  let selectedDay = this.value;

  for (let i = 0; i < tables.length; i++) {
    if (i === (selectedDay - 1)) {
      tables[i].removeAttribute("hidden");
    } else {
      tables[i].setAttribute("hidden", "true");
    }
  }
});





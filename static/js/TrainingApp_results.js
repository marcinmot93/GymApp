document.getElementById('selected-date').addEventListener('change', function (){
    let selectedDate = this.value
    let url = this.getAttribute('data-url')
    window.location.href = url + '?selected_date=' + selectedDate;
});
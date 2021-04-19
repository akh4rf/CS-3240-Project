function fillEntry() {
  var duration_field = document.getElementById('AddExerciseModal').getElementsByTagName('input')[2],
      calories_field = document.getElementById('AddExerciseModal').getElementsByTagName('input')[3];

  var dropdown = document.getElementById('drop'),
      exercise = dropdown.value,
      selected_item = dropdown.options[dropdown.selectedIndex],
      duration = selected_item.getAttribute('data-duration'),
      calories = selected_item.getAttribute('data-calories');

  duration_field.value=duration;
  calories_field.value=calories;
}

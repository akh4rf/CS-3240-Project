function updateEntryModal() {
  changeExtra();
  fillEntry();
}

function fillEntry() {
  var duration_field = document.getElementById('AddExerciseModal').getElementsByTagName('input')[2],
      calories_field = document.getElementById('AddExerciseModal').getElementsByTagName('input')[3],
      extra_field = document.getElementById('insertExtra').getElementsByTagName('input')[0];

  var dropdown = document.getElementById('drop'),
      exercise = dropdown.value,
      selected_item = dropdown.options[dropdown.selectedIndex],
      duration = selected_item.getAttribute('data-duration'),
      calories = selected_item.getAttribute('data-calories'),
      extra = selected_item.getAttribute('data-extra');


  duration_field.value=duration;
  calories_field.value=calories;
  extra_field.value=extra;
}

function changeExtra() {

  var parentDiv = document.getElementById('insertExtra'),
      dropdown = document.getElementById('drop'),
      exercise = dropdown.value,
      selected_item = dropdown.options[dropdown.selectedIndex],
      extra_type = selected_item.getAttribute('data-type');

  // Clear out current field for extra data
  parentDiv.innerHTML = "";

  if (extra_type=="SpeedCardio") {
    parentDiv.innerHTML = '<label for="extra">Mile Time (Minutes)</label><input class="my-2 form-control" type="number" placeholder="0.00" name="extra" id="extra" step="0.01" required>'
  }
  else if (extra_type=="Bodyweight") {
    parentDiv.innerHTML = '<label for="extra">Total Reps</label><input class="my-2 form-control" type="number" placeholder="000" name="extra" id="extra" required>'
  }
  else if (extra_type=="DistanceCardio") {
      parentDiv.innerHTML = '<label for="extra">Distance (Miles)</label><input class="my-2 form-control" type="number" placeholder="0.00" name="extra" id="extra" step="0.01" required>'
    }

}
